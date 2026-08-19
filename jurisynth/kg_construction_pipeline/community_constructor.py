
from rdflib import RDF, RDFS, URIRef, Namespace, Dataset
from collections import Counter
import igraph as ig
import leidenalg as la

# ---------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------

JS_SOURCE = Namespace("http://jurisynth/source/")
JS_DATA = Namespace("http://jurisynth/data/")


# ---------------------------------------------------------------------
# Default filtering
# ---------------------------------------------------------------------

DEFAULT_EXCLUDED_PREDICATES = {
    RDF.type,
    RDFS.label,
}


# ---------------------------------------------------------------------
# Build weighted entity graph
# ---------------------------------------------------------------------

def build_entity_graph(
    validated_triples,
    excluded_predicates=None,
):
    """
    Convert RDF triples into a weighted entity graph.

    Nodes:
        RDF resources

    Edges:
        Object-property relationships

    Edge weights:
        Frequency of identical relations

    Returns
    -------
    igraph.Graph
    """

    if excluded_predicates is None:
        excluded_predicates = DEFAULT_EXCLUDED_PREDICATES


    vertices = dict()

    edge_counter = Counter()
    edge_predicates = dict()


    for element in validated_triples:

        triple = element["triple"]

        subject = triple["subject"]
        predicate = triple["predicate"]
        obj = triple["object"]


        # Ignore literals
        if not isinstance(obj, URIRef):
            continue

        # Ignore noisy predicates
        if predicate in excluded_predicates:
            continue

        if subject not in vertices:
            vertices[subject] = len(vertices)

        if obj not in vertices:
            vertices[obj] = len(vertices)

        edge_key = (subject, predicate, obj)
        edge_counter[edge_key] += 1
        edge_predicates[edge_key] = predicate

    edges = list()
    weights = list()
    predicates = list()


    for (
        (subject, predicate, obj),
        weight
    ) in edge_counter.items():

        edges.append((vertices[subject], vertices[obj]))
        weights.append(weight)
        predicates.append(predicate)

    graph = ig.Graph(
        n=len(vertices),
        edges=edges,
        directed=False,
    )

    graph.vs["uri"] = list(vertices.keys())

    graph.es["weight"] = weights
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
    Run Leiden clustering.
    """

    return la.find_partition(
        graph,
        la.RBConfigurationVertexPartition,
        weights="weight",
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
    Collapse nodes into community nodes.
    """

    vertex_to_comm = dict()

    for cid, members in enumerate(partition):
        for vertex in members:
            vertex_to_comm[vertex] = cid

    edge_weights = Counter()

    for edge in graph.es:
        source = vertex_to_comm[edge.source]
        target = vertex_to_comm[edge.target]

        if source == target:
            continue

        key = tuple(
            sorted((source, target))
        )

        edge_weights[key] += edge["weight"]

    community_graph = ig.Graph(
        n=len(partition),
        directed=False,
    )

    edges = list()
    weights = list()


    for key, weight in edge_weights.items():
        edges.append(key)
        weights.append(weight)

    if edges:
        community_graph.add_edges(edges)

    community_graph.es["weight"] = weights

    community_graph.vs["uri"] = [
        f"community_{i}"
        for i in range(len(partition))
    ]

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
    Generate hierarchical Leiden communities.

    Returns
    -------
    dict
        {
            level:
                {
                    community_id:
                        {
                            "members": list(),
                            "children": list()
                        }
                }
        }
    """

    hierarchy = dict()
    current_graph = graph
    previous_count = None

    for level in range(max_levels):
        partition = leiden_partition(
            current_graph,
            resolution,
            seed,
        )

        communities = dict()


        for cid, members in enumerate(partition):

            communities[cid] = {
                "members": [
                    current_graph.vs[v]["uri"]
                    for v in members
                ],
                "children": list()
            }

        hierarchy[level] = communities
        community_count = len(partition)

        # Stop if no useful hierarchy remains
        if community_count <= 1:
            break

        if previous_count == community_count:
            break

        previous_count = community_count
        current_graph = build_community_graph(current_graph, partition)

    return hierarchy


# ---------------------------------------------------------------------
# Full Leiden pipeline
# ---------------------------------------------------------------------

def build_graph_communities(
    validated_triples,
    max_levels=5,
    resolution=1.0,
    excluded_predicates=None,
):
    """
    Complete Leiden pipeline.
    """

    graph = build_entity_graph(validated_triples, excluded_predicates)

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
    Convert Leiden hierarchy into RDF triples.

    Returns
    -------
    rdflib.Dataset
    """

    if dataset is None:
        dataset = Dataset()


    community_graph = dataset.graph(JS_SOURCE.community)

    dataset.bind("js_source", JS_SOURCE)


    for level, communities in hierarchy.items():
        for cid, data in communities.items():
            community_uri = JS_DATA[f"community_l{level}_{cid}"]

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
                    URIRef(str(community_uri)),
                )
            )

            for member in data["members"]:
                if isinstance(member, URIRef):
                    community_graph.add(
                        (
                            member,
                            JS_SOURCE.memberOf,
                            community_uri,
                        )
                    )

    return dataset