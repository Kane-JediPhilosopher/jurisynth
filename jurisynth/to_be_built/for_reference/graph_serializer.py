from collections import defaultdict
import re

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

JS_DATA = Namespace("http://jurisynth/data/")
JS_SOURCE = Namespace("http://jurisynth/source/")

DOCUMENT = Namespace("http://jurisynth/source/document/")
CHUNK = Namespace("http://jurisynth/source/chunk/")
ASSERTION = Namespace("http://jurisynth/source/assertion/")


# ---------------------------------------------------------------------
# URI helpers
# ---------------------------------------------------------------------

def normalize_identifier(text):
    """
    Convert an arbitrary identifier into a URI-safe fragment.
    """

    text = str(text).strip().lower()

    # Remove file extension
    text = re.sub(r"\.[^.]+$", "", text)

    # Replace non-alphanumeric runs
    text = re.sub(r"[^a-z0-9]+", "_", text)

    # Collapse repeated underscores
    text = re.sub(r"_+", "_", text)

    return text.strip("_")


def document_uri(doc_id):
    return DOCUMENT[
        normalize_identifier(doc_id)
    ]


def chunk_uri(doc_id, chunk_id):
    return CHUNK[
        f"{normalize_identifier(doc_id)}_"
        f"{normalize_identifier(chunk_id)}"
    ]


def assertion_uri(doc_id, chunk_id, assertion_id):
    """
    Generate a stable URI for one extracted assertion.

    The chunk ID is included to make the identifier globally
    traceable to its source location.
    """

    return ASSERTION[
        f"{normalize_identifier(doc_id)}_"
        f"{normalize_identifier(chunk_id)}_"
        f"{normalize_identifier(assertion_id)}"
    ]


def modifier_uri(doc_id, chunk_id, assertion_id, modifier_id):
    """
    Generate a stable URI for one modifier belonging to
    an assertion.
    """

    return JS_DATA[
        "modifier_"
        f"{normalize_identifier(doc_id)}_"
        f"{normalize_identifier(chunk_id)}_"
        f"{normalize_identifier(assertion_id)}_"
        f"{normalize_identifier(modifier_id)}"
    ]


# ---------------------------------------------------------------------
# Modifier serialization
# ---------------------------------------------------------------------

def serialize_modifier(
    graph,
    modifier_resource,
    modifier,
):
    """
    Serialize one modifier into the assertion graph.

    At present, modifiers are treated conservatively as opaque
    values because the extraction pipeline does not yet impose a
    structured modifier schema.

    A future structured modifier representation can be introduced
    here without changing the assertion graph architecture.
    """

    graph.add(
        (
            modifier_resource,
            RDF.type,
            JS_SOURCE.Modifier,
        )
    )

    graph.add(
        (
            modifier_resource,
            JS_SOURCE.value,
            Literal(str(modifier)),
        )
    )


# ---------------------------------------------------------------------
# Dataset builder
# ---------------------------------------------------------------------

def build_quad_dataset(
    validated_assertions,
    schema_namespaces=None,
):
    """
    Construct the Jurisynth RDF Dataset from validated assertions.

    Architecture
    ------------

    1. Chunk graphs contain the ordinary RDF triples extracted
       from each chunk.

    2. A single global assertion graph contains assertion-level
       n-ary structures when an assertion has modifiers.

    3. Document graphs describe document provenance and link
       documents to their chunks and assertion resources.

    Conceptually:

        GRAPH chunk_X {
            subject predicate object .
        }

        GRAPH js:Assertions {
            assertion_X rdf:type js:Assertion ;
                js:subject subject ;
                js:predicate predicate ;
                js:object object ;
                js:sourceChunk chunk_X ;
                js:hasModifier modifier_X .

            modifier_X rdf:type js:Modifier ;
                js:value "..." .
        }

        GRAPH document_X {
            document_X rdf:type js:Document ;
                js:hasChunk chunk_X ;
                js:hasAssertion assertion_X .
        }

    The ordinary triple is therefore retained for efficient graph
    traversal and retrieval, while the assertion representation
    provides a place for statement-level metadata.

    Parameters
    ----------
    validated_assertions : list[dict]

        Expected format:

        {
            "doc_id": str,
            "chunk_id": str,
            "assertion_id": int,

            "assertion": {
                "subject": URIRef,
                "predicate": URIRef,
                "object": URIRef | Literal
            },

            "modifiers": [...]
        }

    schema_namespaces : list[(prefix, Namespace)], optional
        Ontology/schema namespace bindings.

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

    dataset.bind("source", JS_SOURCE)
    dataset.bind("data", JS_DATA)

    dataset.bind("document", DOCUMENT)
    dataset.bind("chunk", CHUNK)
    dataset.bind("assertion", ASSERTION)

    if schema_namespaces:

        for prefix, namespace in schema_namespaces:

            dataset.bind(
                prefix,
                namespace,
            )

    # -------------------------------------------------------------
    # Global assertion graph
    # -------------------------------------------------------------

    assertion_graph = dataset.graph(ASSERTION)

    # -------------------------------------------------------------
    # Track discovered chunks and assertions
    # -------------------------------------------------------------

    document_chunks = defaultdict(set)
    document_assertions = defaultdict(set)

    # -------------------------------------------------------------
    # Serialize validated assertions
    # -------------------------------------------------------------

    for element in validated_assertions:

        doc_id = element["doc_id"]
        chunk_id = element["chunk_id"]
        assertion_id = element["assertion_id"]

        assertion = element["assertion"]

        # IMPORTANT:
        # modifiers lives alongside "assertion", not inside it.
        modifiers = element.get(
            "modifiers",
            [],
        )

        # ---------------------------------------------------------
        # Source chunk
        # ---------------------------------------------------------

        source_chunk = chunk_uri(
            doc_id,
            chunk_id,
        )

        chunk_graph = dataset.graph(
            source_chunk
        )

        # ---------------------------------------------------------
        # Core RDF triple
        #
        # Always preserve this representation.
        # ---------------------------------------------------------

        chunk_graph.add(
            (
                assertion["subject"],
                assertion["predicate"],
                assertion["object"],
            )
        )

        document_chunks[doc_id].add(
            chunk_id
        )

        # ---------------------------------------------------------
        # Assertion-level representation
        #
        # Only required when assertion-specific metadata exists.
        # Currently that means modifiers.
        # ---------------------------------------------------------

        if not modifiers:
            continue

        assertion_resource = assertion_uri(
            doc_id,
            chunk_id,
            assertion_id,
        )

        # ---------------------------------------------------------
        # Assertion identity
        # ---------------------------------------------------------

        assertion_graph.add(
            (
                assertion_resource,
                RDF.type,
                JS_SOURCE.Assertion,
            )
        )

        # ---------------------------------------------------------
        # Core assertion components
        # ---------------------------------------------------------

        assertion_graph.add(
            (
                assertion_resource,
                JS_SOURCE.subject,
                assertion["subject"],
            )
        )

        assertion_graph.add(
            (
                assertion_resource,
                JS_SOURCE.predicate,
                assertion["predicate"],
            )
        )

        assertion_graph.add(
            (
                assertion_resource,
                JS_SOURCE.object,
                assertion["object"],
            )
        )

        # ---------------------------------------------------------
        # Provenance
        # ---------------------------------------------------------

        assertion_graph.add(
            (
                assertion_resource,
                JS_SOURCE.source_chunk,
                source_chunk,
            )
        )

        # ---------------------------------------------------------
        # Modifiers
        # ---------------------------------------------------------

        for modifier_id, modifier in enumerate(
            modifiers,
            start=1,
        ):

            modifier_resource = modifier_uri(
                doc_id,
                chunk_id,
                assertion_id,
                modifier_id,
            )

            assertion_graph.add(
                (
                    assertion_resource,
                    JS_SOURCE.has_modifier,
                    modifier_resource,
                )
            )

            serialize_modifier(
                assertion_graph,
                modifier_resource,
                modifier,
            )

        # Track assertion for document-level provenance.
        document_assertions[doc_id].add(
            assertion_resource
        )

    # -------------------------------------------------------------
    # Populate document graphs
    # -------------------------------------------------------------

    for doc_id, chunks in document_chunks.items():

        doc_resource = document_uri(
            doc_id
        )

        doc_graph = dataset.graph(
            doc_resource
        )

        # ---------------------------------------------------------
        # Document identity
        # ---------------------------------------------------------

        doc_graph.add(
            (
                doc_resource,
                RDF.type,
                JS_SOURCE.Document,
            )
        )

        doc_graph.add(
            (
                doc_resource,
                RDFS.label,
                Literal(str(doc_id)),
            )
        )

        # ---------------------------------------------------------
        # Chunk resources
        # ---------------------------------------------------------

        for chunk_id in sorted(chunks):

            chunk_resource = chunk_uri(
                doc_id,
                chunk_id,
            )

            doc_graph.add(
                (
                    chunk_resource,
                    RDF.type,
                    JS_SOURCE.Chunk,
                )
            )

            doc_graph.add(
                (
                    doc_resource,
                    JS_SOURCE.has_chunk,
                    chunk_resource,
                )
            )

    # -------------------------------------------------------------
    # Link assertions from document provenance graphs
    # -------------------------------------------------------------

    for doc_id, assertions in document_assertions.items():

        doc_resource = document_uri(
            doc_id
        )

        doc_graph = dataset.graph(
            doc_resource
        )

        for assertion_resource in assertions:

            doc_graph.add(
                (
                    doc_resource,
                    JS_SOURCE.has_assertion,
                    assertion_resource,
                )
            )

    return dataset


# ---------------------------------------------------------------------
# Serialisation
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

# ---------------------------------------------------------------------
# Module execution
# ---------------------------------------------------------------------

def serialize_graph(
    validated_assertions,
    schema_namespaces=None,
    output_file="jurisynth_graph.nq",
    format="nquads",
):
    """
    Build and serialize the Jurisynth RDF Dataset.

    Parameters
    ----------
    validated_assertions : list[dict]
        Assertions that have passed the validation stage.

    schema_namespaces : list[(prefix, Namespace)], optional
        Ontology/schema namespace bindings.

    output_file : str
        Destination path for the serialized RDF Dataset.

    format : str
        RDF serialization format. Defaults to N-Quads.

    Returns
    -------
    rdflib.Dataset
        The constructed RDF Dataset.
    """

    dataset = build_quad_dataset(
        validated_assertions,
        schema_namespaces=schema_namespaces,
    )

    serialize_dataset(
        dataset,
        output_file,
        format=format,
    )

    return dataset