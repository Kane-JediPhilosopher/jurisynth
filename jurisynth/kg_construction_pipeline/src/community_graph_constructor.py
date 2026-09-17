from collections import defaultdict
import gc

import igraph as ig
import leidenalg as la

from rdflib import (
    Dataset,
    Namespace,
    RDF,
    RDFS,
    URIRef,
    Literal,
)


# ---------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------

JS_SOURCE = Namespace("http://jurisynth/source/")
JS_DATA = Namespace("http://jurisynth/data/")

DOCUMENT = Namespace("http://jurisynth/source/document/")
CHUNK = Namespace("http://jurisynth/source/chunk/")


# ---------------------------------------------------------------------
# Default filtering
# ---------------------------------------------------------------------

DEFAULT_EXCLUDED_PREDICATES = {
    RDF.type,
    RDFS.label,
}


# ---------------------------------------------------------------------
# Dataset graph helpers
# ---------------------------------------------------------------------

def is_chunk_graph(graph_identifier):
    """
    Return True if the graph identifier belongs to a source chunk graph.

    Only chunk graphs contain the semantic RDF assertions used to
    construct the entity graph.

    Assertion/provenance graphs are deliberately excluded because their
    triples describe the representation of an assertion rather than the
    semantic relationship itself.
    """

    return str(graph_identifier).startswith(
        str(CHUNK)
    )


def extract_semantic_triples(
    dataset,
):
    """
    Stream semantic RDF triples from chunk named graphs.

    Yields
    ------
    tuple
        (subject, predicate, object)

    Notes
    -----
    This deliberately yields triples instead of materialising the entire
    semantic corpus as a Python list. The RDFLib Dataset already owns the
    triples in memory; duplicating them can consume tens of GiB on a large
    corpus.
    """

    graph_count = 0
    triple_count = 0

    for graph in dataset.contexts():

        if not is_chunk_graph(
            graph.identifier
        ):
            continue

        graph_count += 1

        for subject, predicate, obj in graph:

            triple_count += 1

            if triple_count % 500_000 == 0:
                print(
                    f"[Community Graph] Streamed "
                    f"{triple_count:,} semantic triples "
                    f"from {graph_count:,} chunk graphs.",
                    flush=True,
                )

            yield (
                subject,
                predicate,
                obj,
            )

    print(
        f"[Community Graph] Semantic triple stream complete | "
        f"triples={triple_count:,} | "
        f"chunk_graphs={graph_count:,}",
        flush=True,
    )


# ---------------------------------------------------------------------
# Entity / relation extraction
# ---------------------------------------------------------------------

def extract_entities_and_relations(
    dataset,
    excluded_predicates=None,
):
    """
    Derive entity and relation sets by streaming semantic triples.
    """

    if excluded_predicates is None:
        excluded_predicates = (
            DEFAULT_EXCLUDED_PREDICATES
        )

    entities = set()
    relations = set()

    for subject, predicate, obj in extract_semantic_triples(
        dataset
    ):

        if predicate in excluded_predicates:
            continue

        if not isinstance(subject, URIRef):
            continue

        if not isinstance(obj, URIRef):
            continue

        entities.add(subject)
        entities.add(obj)
        relations.add(predicate)

    return entities, relations


# ---------------------------------------------------------------------
# Build entity graph
# ---------------------------------------------------------------------

def build_entity_graph(
    dataset,
    excluded_predicates=None,
):
    """
    Convert the completed KG into an unweighted entity graph.

    Semantic triples are streamed directly from RDFLib instead of first
    materialising the whole corpus as a Python list.
    """

    if excluded_predicates is None:
        excluded_predicates = (
            DEFAULT_EXCLUDED_PREDICATES
        )

    vertices = {}
    edges = []
    predicates = []

    # Deduplication is still required because the same semantic relationship
    # may occur in multiple chunks.
    seen_edges = set()

    scanned = 0
    accepted = 0

    print(
        "[Community Graph] Building entity graph by streaming triples...",
        flush=True,
    )

    for subject, predicate, obj in extract_semantic_triples(
        dataset
    ):

        scanned += 1

        if predicate in excluded_predicates:
            continue

        if not isinstance(subject, URIRef):
            continue

        if not isinstance(obj, URIRef):
            continue

        if subject not in vertices:
            vertices[subject] = len(vertices)

        if obj not in vertices:
            vertices[obj] = len(vertices)

        source_id = vertices[subject]
        target_id = vertices[obj]

        # Preserve predicate identity when determining duplicates.
        edge_key = (
            source_id,
            predicate,
            target_id,
        )

        if edge_key in seen_edges:
            continue

        seen_edges.add(edge_key)

        edges.append(
            (
                source_id,
                target_id,
            )
        )

        predicates.append(predicate)

        accepted += 1

        if accepted % 250_000 == 0:
            print(
                f"[Community Graph] Entity graph progress | "
                f"scanned={scanned:,} | "
                f"unique_edges={accepted:,} | "
                f"vertices={len(vertices):,}",
                flush=True,
            )

    print(
        f"[Community Graph] Triple scan complete | "
        f"scanned={scanned:,} | "
        f"vertices={len(vertices):,} | "
        f"edges={len(edges):,}",
        flush=True,
    )

    # Save only what is needed from the vertex dictionary.
    vertex_uris = list(vertices.keys())
    vertex_count = len(vertex_uris)

    # This set can be enormous and is no longer needed once deduplication
    # has finished. Free it BEFORE igraph creates another large graph
    # representation.
    del seen_edges
    del vertices
    gc.collect()

    print(
        "[Community Graph] Deduplication state released; "
        "constructing igraph graph...",
        flush=True,
    )

    graph = ig.Graph(
        n=vertex_count,
        edges=edges,
        directed=False,
    )

    # igraph now owns its internal edge representation.
    del edges

    graph.vs["uri"] = vertex_uris
    del vertex_uris

    graph.es["predicate"] = predicates
    del predicates

    gc.collect()

    print(
        f"[Community Graph] Entity graph complete | "
        f"vertices={graph.vcount():,} | "
        f"edges={graph.ecount():,}",
        flush=True,
    )

    return graph


# ---------------------------------------------------------------------
# Single Leiden pass
# ---------------------------------------------------------------------

def leiden_partition(
    graph,
    resolution=1.0,
    seed=42,
):
    """
    Run one Leiden partitioning pass.
    """

    return la.find_partition(
        graph,
        la.RBConfigurationVertexPartition,
        resolution_parameter=resolution,
        seed=seed,
    )


# ---------------------------------------------------------------------
# Build collapsed community graph
# ---------------------------------------------------------------------

def build_community_graph(
    graph,
    partition,
):
    """
    Collapse a graph's communities into a new graph.

    Each vertex in the resulting graph represents one community from
    the previous level.

    No edge weights are used. Multiple inter-community relationships
    therefore collapse into a single edge.
    """

    vertex_to_comm = dict()

    for community_id, members in enumerate(
        partition
    ):
        for vertex in members:
            vertex_to_comm[vertex] = community_id

    edges = list()
    seen_edges = set()

    for edge in graph.es:

        source = vertex_to_comm[
            edge.source
        ]

        target = vertex_to_comm[
            edge.target
        ]

        # Internal relationship
        if source == target:
            continue

        edge_key = tuple(
            sorted(
                (
                    source,
                    target,
                )
            )
        )

        if edge_key in seen_edges:
            continue

        seen_edges.add(edge_key)
        edges.append(edge_key)

    community_graph = ig.Graph(
        n=len(partition),
        edges=edges,
        directed=False,
    )

    return community_graph


# ---------------------------------------------------------------------
# Hierarchical Leiden
# ---------------------------------------------------------------------

def hierarchical_leiden(
    graph,
    max_levels=5,
    resolution=1.0,
    seed=42,
):
    """
    Generate a genuine hierarchical Leiden structure.

    Level 0
        Community members are original entity URIs.

    Level > 0
        Community members are the community URIs from the immediately
        preceding level.

    Each higher-level community therefore has an explicit parent-child
    relationship with the communities below it.

    Returns
    -------
    dict

        {
            0: {
                0: {
                    "members": [entity_uri, ...],
                    "children": [],
                    "parent": None
                }
            },

            1: {
                0: {
                    "members": [community_uri, ...],
                    "children": [...],
                    "parent": None
                }
            }
        }
    """

    hierarchy = dict()

    current_graph = graph

    # -----------------------------------------------------------------
    # At level 0, graph vertices represent actual entities.
    # At subsequent levels, they represent communities.
    # -----------------------------------------------------------------

    current_vertex_ids = [
        graph.vs[index]["uri"]
        for index in range(
            graph.vcount()
        )
    ]

    previous_community_uris = list()

    for level in range(max_levels):

        # -------------------------------------------------------------
        # Run Leiden
        # -------------------------------------------------------------

        print(
            f"[Community Graph] Leiden level {level} starting | "
            f"vertices={current_graph.vcount():,} | "
            f"edges={current_graph.ecount():,}",
            flush=True,
        )

        partition = leiden_partition(
            current_graph,
            resolution=resolution,
            seed=seed,
        )

        community_count = len(partition)

        print(
            f"[Community Graph] Leiden level {level} complete | "
            f"communities={community_count:,}",
            flush=True,
        )

        communities = dict()

        current_community_uris = list()

        # -------------------------------------------------------------
        # Construct communities
        # -------------------------------------------------------------

        for community_id, members in enumerate(
            partition
        ):

            community_uri = JS_DATA[
                f"community_l{level}_{community_id}"
            ]

            current_community_uris.append(
                community_uri
            )

            member_uris = [
                current_vertex_ids[vertex]
                for vertex in members
            ]

            communities[community_id] = {
                "uri": community_uri,
                "members": member_uris,
                "children": list(),
                "parent": None,
            }

        # -------------------------------------------------------------
        # Establish parent-child relationships
        #
        # At level > 0:
        #
        # current community
        #       |
        #       +-- child community from previous level
        #
        # -------------------------------------------------------------

        if level > 0:

            previous_to_parent = dict()

            for community_id, members in enumerate(
                partition
            ):

                parent_uri = current_community_uris[
                    community_id
                ]

                for vertex in members:

                    child_uri = current_vertex_ids[
                        vertex
                    ]

                    previous_to_parent[
                        child_uri
                    ] = parent_uri

                    communities[
                        community_id
                    ]["children"].append(
                        child_uri
                    )

            # ---------------------------------------------------------
            # Store parent information on previous-level communities
            # ---------------------------------------------------------

            for previous_community in hierarchy[
                level - 1
            ].values():

                previous_uri = (
                    previous_community["uri"]
                )

                previous_community[
                    "parent"
                ] = previous_to_parent.get(
                    previous_uri
                )

        hierarchy[level] = communities

        # -------------------------------------------------------------
        # Stop conditions
        # -------------------------------------------------------------

        if community_count <= 1:
            break

        # If the partition did not reduce the number of vertices,
        # there is no meaningful higher-level hierarchy.
        if community_count >= current_graph.vcount():
            break

        # -------------------------------------------------------------
        # Collapse communities into next-level graph
        # -------------------------------------------------------------

        current_graph = build_community_graph(
            current_graph,
            partition,
        )

        # At the next level, vertices represent the current
        # level's communities.
        current_vertex_ids = (
            current_community_uris
        )

    return hierarchy


# ---------------------------------------------------------------------
# Full community-construction pipeline
# ---------------------------------------------------------------------

def build_graph_communities(
    dataset,
    max_levels=5,
    resolution=1.0,
    excluded_predicates=None,
):
    """
    Construct global communities from the completed KG.

    The module derives its entities and semantic relationships directly
    from the Dataset rather than depending on intermediate pipeline
    variables.
    """

    graph = build_entity_graph(
        dataset,
        excluded_predicates=excluded_predicates,
    )

    hierarchy = hierarchical_leiden(
        graph,
        max_levels=max_levels,
        resolution=resolution,
    )

    return hierarchy, graph


# ---------------------------------------------------------------------
# Community RDF serialization
# ---------------------------------------------------------------------

def serialize_communities(
    hierarchy,
    dataset=None,
):
    """
    Serialize the community hierarchy into one dedicated named graph.

    Level 0:
        entity -> memberOf -> community

    Higher levels:
        child_community -> memberOf -> parent_community

    This produces an RDF representation of the hierarchy without
    creating a separate named graph for every community.
    """

    if dataset is None:
        dataset = Dataset()

    community_graph = dataset.graph(
        JS_SOURCE.community
    )

    dataset.bind(
        "js_source",
        JS_SOURCE
    )

    # -----------------------------------------------------------------
    # Serialize communities
    # -----------------------------------------------------------------

    for level, communities in hierarchy.items():

        for community_id, data in communities.items():

            community_uri = data["uri"]

            # ---------------------------------------------------------
            # Community identity
            # ---------------------------------------------------------

            community_graph.add(
                (
                    community_uri,
                    RDF.type,
                    JS_SOURCE.Community,
                )
            )

            community_graph.add(
                (
                    community_uri,
                    RDFS.label,
                    Literal(
                        str(community_uri)
                    ),
                )
            )

            # ---------------------------------------------------------
            # Membership
            # ---------------------------------------------------------

            for member in data["members"]:

                if not isinstance(
                    member,
                    URIRef,
                ):
                    continue

                community_graph.add(
                    (
                        member,
                        JS_SOURCE.memberOf,
                        community_uri,
                    )
                )

    return dataset

# ---------------------------------------------------------------------
# Module execution
# ---------------------------------------------------------------------

def construct_communities(
    dataset,
    max_levels=5,
    resolution=1.0,
    excluded_predicates=None,
    output_file=None,
    format="nquads",
):
    """
    Construct the global community hierarchy from a completed
    Jurisynth RDF Dataset and optionally serialize the result.

    Parameters
    ----------
    dataset : rdflib.Dataset
        Completed Jurisynth RDF Dataset.

    max_levels : int
        Maximum number of Leiden hierarchy levels.

    resolution : float
        Leiden resolution parameter.

    excluded_predicates : set, optional
        Predicates excluded when constructing the entity graph.

    output_file : str, optional
        Destination path for the completed Dataset.
        If None, the Dataset is not serialized.

    format : str
        RDF serialization format. Defaults to N-Quads.

    Returns
    -------
    tuple[dict, igraph.Graph, rdflib.Dataset]
        hierarchy:
            Hierarchical community structure.

        entity_graph:
            Entity graph used for community detection.

        dataset:
            Dataset containing the serialized community hierarchy.
    """

    # -------------------------------------------------------------
    # Build global entity graph and community hierarchy
    # -------------------------------------------------------------

    hierarchy, entity_graph = build_graph_communities(
        dataset,
        max_levels=max_levels,
        resolution=resolution,
        excluded_predicates=excluded_predicates,
    )

    # -------------------------------------------------------------
    # Add community hierarchy to the Dataset
    # -------------------------------------------------------------

    dataset = serialize_communities(
        hierarchy,
        dataset,
    )

    # -------------------------------------------------------------
    # Optionally serialize completed Dataset
    # -------------------------------------------------------------

    if output_file is not None:
        dataset.serialize(
            output_file,
            format=format,
        )

    return (
        hierarchy,
        entity_graph,
        dataset,
    )
