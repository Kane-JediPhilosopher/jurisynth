from collections import defaultdict

import igraph as ig
import leidenalg as la

from rdflib import (
    Dataset,
    Namespace,
    RDF,
    RDFS,
    URIRef,
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
    Extract semantic RDF triples from the completed KG.

    Only triples stored in chunk named graphs are considered.

    Returns
    -------
    list[tuple]
        A list of:
            (subject, predicate, object)

    Notes
    -----
    This intentionally ignores assertion/provenance graphs. A triple such
    as:

        assertion_007 -> subject -> :EntityA

    is provenance structure, not an EntityA relationship.

    The actual semantic assertion remains:

        :EntityA -> :someProperty -> :EntityB
    """

    semantic_triples = list()

    for graph in dataset.contexts():

        if not is_chunk_graph(
            graph.identifier
        ):
            continue

        for subject, predicate, obj in graph:

            semantic_triples.append(
                (
                    subject,
                    predicate,
                    obj,
                )
            )

    return semantic_triples


# ---------------------------------------------------------------------
# Entity / relation extraction
# ---------------------------------------------------------------------

def extract_entities_and_relations(
    dataset,
    excluded_predicates=None,
):
    """
    Derive the entity and relation sets from the completed KG.

    Entities:
        URI resources participating in semantic object-property
        relationships.

    Relations:
        Predicates connecting URI resources.

    Literal-valued assertions are not included in the entity graph,
    because literals cannot act as graph vertices.

    Returns
    -------
    tuple[set, set]
        entities, relations
    """

    if excluded_predicates is None:
        excluded_predicates = (
            DEFAULT_EXCLUDED_PREDICATES
        )

    entities = set()
    relations = set()

    semantic_triples = extract_semantic_triples(
        dataset
    )

    for subject, predicate, obj in semantic_triples:

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

    Nodes:
        RDF resources.

    Edges:
        Object-property relationships between RDF resources.

    Edge metadata:
        The RDF predicate responsible for the edge.

    Important:
        Edge multiplicity is deliberately NOT represented as a weight.

        If the same semantic triple occurs repeatedly across chunks,
        it still represents one graph relationship.
    """

    if excluded_predicates is None:
        excluded_predicates = (
            DEFAULT_EXCLUDED_PREDICATES
        )

    vertices = dict()
    edges = list()
    predicates = list()

    # Prevent duplicate graph edges while retaining predicate identity.
    seen_edges = set()

    semantic_triples = extract_semantic_triples(
        dataset
    )

    for subject, predicate, obj in semantic_triples:

        # -------------------------------------------------------------
        # Ignore schema/noise predicates
        # -------------------------------------------------------------

        if predicate in excluded_predicates:
            continue

        # -------------------------------------------------------------
        # Only URI -> URI relationships become entity-graph edges
        # -------------------------------------------------------------

        if not isinstance(subject, URIRef):
            continue

        if not isinstance(obj, URIRef):
            continue

        # -------------------------------------------------------------
        # Register vertices
        # -------------------------------------------------------------

        if subject not in vertices:
            vertices[subject] = len(vertices)

        if obj not in vertices:
            vertices[obj] = len(vertices)

        # -------------------------------------------------------------
        # Avoid edge multiplicity
        # -------------------------------------------------------------

        edge_key = (
            subject,
            predicate,
            obj,
        )

        if edge_key in seen_edges:
            continue

        seen_edges.add(edge_key)

        edges.append(
            (
                vertices[subject],
                vertices[obj],
            )
        )

        predicates.append(predicate)

    # -------------------------------------------------------------
    # Construct graph
    # -------------------------------------------------------------

    graph = ig.Graph(
        n=len(vertices),
        edges=edges,
        directed=False,
    )

    graph.vs["uri"] = list(
        vertices.keys()
    )

    graph.es["predicate"] = predicates

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

        partition = leiden_partition(
            current_graph,
            resolution=resolution,
            seed=seed,
        )

        community_count = len(partition)

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