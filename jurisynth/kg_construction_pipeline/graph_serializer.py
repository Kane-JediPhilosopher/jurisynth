import re
from collections import defaultdict
from rdflib import RDF, RDFS, URIRef, Namespace, Dataset

# ---------------------------------------------------------------------
# Namespaces
# ---------------------------------------------------------------------

JS_DATA = Namespace("http://jurisynth/data/")
JS_SOURCE = Namespace("http://jurisynth/source/")
DOCUMENT = Namespace("http://jurisynth/source/document/")
CHUNK = Namespace("http://jurisynth/source/chunk/")


# ---------------------------------------------------------------------
# URI helpers
# ---------------------------------------------------------------------

def normalize_identifier(text):
    """
    Convert arbitrary identifiers into URI-safe fragments.
    """

    text = text.strip().lower()
    text = re.sub(r"\.[^.]+$", "", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text)

    return text.strip("_")


def document_uri(doc_id):
    return DOCUMENT[normalize_identifier(doc_id)]

def chunk_uri(doc_id, chunk_id):
    return CHUNK[f"{normalize_identifier(doc_id)}_{normalize_identifier(chunk_id)}"]


# ---------------------------------------------------------------------
# Dataset builder
# ---------------------------------------------------------------------

def build_quad_dataset(
    validated_triples,
    schema_namespaces=None,
):
    """
    Construct a hierarchical RDF Dataset.

    Structure
    ---------

    Dataset

        ├── Document named graphs
        │       document -> chunk
        │
        ├── Chunk named graphs
        │       extracted triples
        │
        └── Default graph
                optional future metadata

    Parameters
    ----------
    validated_triples : list[dict]

        Output from the validation module.

    schema_namespaces : list[(prefix, Namespace)], optional

    Returns
    -------
    rdflib.Dataset
    """

    dataset = Dataset()

    # -------------------------------------------------------------
    # Namespace bindings
    # -------------------------------------------------------------

    dataset.bind("rdf", RDF)
    dataset.bind("rdfs", RDFS)

    dataset.bind("source", DOCUMENT)
    dataset.bind("chunk", CHUNK)
    dataset.bind("js_source", JS_SOURCE)

    if schema_namespaces:
        for prefix, namespace in schema_namespaces:
            dataset.bind(prefix, namespace)

    # -------------------------------------------------------------
    # Track discovered chunks
    # -------------------------------------------------------------

    document_chunks = defaultdict(set)

    # -------------------------------------------------------------
    # Populate chunk graphs
    # -------------------------------------------------------------

    for element in validated_triples:

        doc_id = element["doc_id"]
        chunk_id = element["chunk_id"]

        triple = element["triple"]

        graph_uri = chunk_uri(doc_id, chunk_id)

        g = dataset.graph(graph_uri)

        g.add((
            triple["subject"],
            triple["predicate"],
            triple["object"],
        ))

        document_chunks[doc_id].add(chunk_id)

    # -------------------------------------------------------------
    # Populate document graphs
    # -------------------------------------------------------------

    for doc_id, chunks in document_chunks.items():
        doc_graph = dataset.graph(document_uri(doc_id))
        doc_resource = document_uri(doc_id)

        doc_graph.add((
            doc_resource,
            RDF.type,
            JS_SOURCE.Document,
        ))

        doc_graph.add((
            doc_resource,
            RDFS.label,
            URIRef(doc_resource)
        ))

        for chunk_id in sorted(chunks):
            chunk_resource = chunk_uri(doc_id, chunk_id,)

            doc_graph.add((
                chunk_resource,
                RDF.type,
                JS_SOURCE.Chunk,
            ))

            doc_graph.add((
                doc_resource,
                JS_SOURCE.has_chunk,
                chunk_resource,
            ))

    return dataset


# ---------------------------------------------------------------------
# Serialization
# ---------------------------------------------------------------------

def serialize_dataset(
    dataset,
    output_file,
    format="nquads",
):
    """
    Serialize an RDF Dataset.

    Parameters
    ----------
    dataset : rdflib.Dataset

    output_file : str

    format : str
        Defaults to N-Quads.
    """

    dataset.serialize(
        destination=output_file,
        format=format,
    )