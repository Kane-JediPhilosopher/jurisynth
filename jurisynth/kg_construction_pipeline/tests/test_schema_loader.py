import pytest
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, OWL

from schema_loader import extract_resources, load_schema


# =====================================================================
# Resource extraction
# =====================================================================

def test_extract_resources_extracts_label_and_comment():
    graph = Graph()

    uri = URIRef("http://jurisynth/data/Animal")

    graph.add((uri, RDF.type, OWL.Class))
    graph.add((uri, RDFS.label, Literal("Animal")))
    graph.add((uri, RDFS.comment, Literal("A living organism.")))

    resources, metadata = extract_resources(graph, "class")

    assert resources == {
        str(uri): "Animal"
    }

    assert metadata[str(uri)]["type"] == "class"
    assert metadata[str(uri)]["label"] == "Animal"
    assert metadata[str(uri)]["comment"] == "A living organism."
    assert metadata[str(uri)]["text"] == (
        "Animal. A living organism."
    )


def test_extract_resources_falls_back_to_uri_fragment():
    graph = Graph()

    uri = URIRef("http://jurisynth/data/Animal")

    graph.add((uri, RDF.type, OWL.Class))

    resources, metadata = extract_resources(graph, "class")

    assert resources[str(uri)] == "Animal"
    assert metadata[str(uri)]["label"] == "Animal"


def test_extract_resources_ignores_blank_nodes():
    graph = Graph()

    graph.add((BNode(), RDF.type, OWL.Class))

    resources, metadata = extract_resources(graph, "class")

    assert resources == {}
    assert metadata == {}


# =====================================================================
# Deprecation + property metadata
# =====================================================================

def test_extract_resources_filters_explicitly_deprecated_resource():
    graph = Graph()

    uri = URIRef("http://jurisynth/data/OldClass")

    graph.add((uri, RDF.type, OWL.Class))
    graph.add((uri, RDFS.label, Literal("Old Class")))
    graph.add((uri, OWL.deprecated, Literal(True)))

    resources, metadata = extract_resources(graph, "class")

    assert resources == {}
    assert metadata == {}


@pytest.mark.parametrize(
    "label, comment",
    [
        ("Deprecated Class", ""),
        ("Old Class", "This resource is deprecated."),
    ],
)
def test_extract_resources_filters_resources_with_deprecated_text(
    label,
    comment,
):
    graph = Graph()

    uri = URIRef("http://jurisynth/data/OldClass")

    graph.add((uri, RDF.type, OWL.Class))
    graph.add((uri, RDFS.label, Literal(label)))

    if comment:
        graph.add((uri, RDFS.comment, Literal(comment)))

    resources, metadata = extract_resources(graph, "class")

    assert resources == {}
    assert metadata == {}


def test_extract_resources_extracts_property_domain_and_range():
    graph = Graph()

    property_uri = URIRef(
        "http://jurisynth/data/hasValue"
    )
    domain_uri = URIRef(
        "http://jurisynth/data/Animal"
    )
    range_uri = URIRef(
        "http://jurisynth/data/Plant"
    )

    graph.add(
        (property_uri, RDF.type, OWL.ObjectProperty)
    )
    graph.add(
        (property_uri, RDFS.label, Literal("has value"))
    )
    graph.add(
        (property_uri, RDFS.domain, domain_uri)
    )
    graph.add(
        (property_uri, RDFS.range, range_uri)
    )

    resources, metadata = extract_resources(
        graph,
        "object property",
    )

    assert resources[str(property_uri)] == "has value"

    assert metadata[str(property_uri)]["domain"] == {
        domain_uri
    }

    assert metadata[str(property_uri)]["range"] == {
        range_uri
    }


# =====================================================================
# Schema loading
# =====================================================================

def test_load_schema_parses_schema_files(tmp_path):
    schema_1 = tmp_path / "schema1.rdf"
    schema_2 = tmp_path / "schema2.rdf"

    schema_1.write_text(
        """<?xml version="1.0"?>
        <rdf:RDF
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
            xmlns:owl="http://www.w3.org/2002/07/owl#"
            xmlns:js="http://jurisynth/data/">

            <owl:Class rdf:about="http://jurisynth/data/Animal">
                <rdfs:label>Animal</rdfs:label>
            </owl:Class>
        </rdf:RDF>
        """,
        encoding="utf-8",
    )

    schema_2.write_text(
        """<?xml version="1.0"?>
        <rdf:RDF
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
            xmlns:owl="http://www.w3.org/2002/07/owl#"
            xmlns:js="http://jurisynth/data/">

            <owl:ObjectProperty rdf:about="http://jurisynth/data/hasValue">
                <rdfs:label>has value</rdfs:label>
            </owl:ObjectProperty>
        </rdf:RDF>
        """,
        encoding="utf-8",
    )

    result = load_schema(tmp_path)

    assert "http://jurisynth/data/Animal" in result["classes"]
    assert (
        "http://jurisynth/data/hasValue"
        in result["object_properties"]
    )

    assert (
        "http://jurisynth/data/Animal"
        in result["rdf_resources"]
    )

    assert (
        "http://jurisynth/data/hasValue"
        in result["rdf_resources"]
    )

    assert result["rdf_dict"][
        "http://jurisynth/data/Animal"
    ] == "Animal"

    assert result["rdf_dict"][
        "http://jurisynth/data/hasValue"
    ] == "has value"


def test_load_schema_aggregates_resource_metadata(tmp_path):
    schema = tmp_path / "schema.rdf"

    schema.write_text(
        """<?xml version="1.0"?>
        <rdf:RDF
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
            xmlns:owl="http://www.w3.org/2002/07/owl#">

            <owl:Class rdf:about="http://jurisynth/data/Animal">
                <rdfs:label>Animal</rdfs:label>
            </owl:Class>

            <owl:ObjectProperty rdf:about="http://jurisynth/data/hasValue">
                <rdfs:label>has value</rdfs:label>
            </owl:ObjectProperty>
        </rdf:RDF>
        """,
        encoding="utf-8",
    )

    result = load_schema(tmp_path)

    assert set(result["resource_metadata"]) == {
        "http://jurisynth/data/Animal",
        "http://jurisynth/data/hasValue",
    }

    assert (
        result["resource_metadata"][
            "http://jurisynth/data/Animal"
        ]["type"]
        == "class"
    )

    assert (
        result["resource_metadata"][
            "http://jurisynth/data/hasValue"
        ]["type"]
        == "object property"
    )


def test_load_schema_returns_expected_structure(tmp_path):
    schema = tmp_path / "schema.rdf"

    schema.write_text(
        """<?xml version="1.0"?>
        <rdf:RDF
            xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
            xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
            xmlns:owl="http://www.w3.org/2002/07/owl#">

            <owl:Class rdf:about="http://jurisynth/data/Animal">
                <rdfs:label>Animal</rdfs:label>
            </owl:Class>
        </rdf:RDF>
        """,
        encoding="utf-8",
    )

    result = load_schema(tmp_path)

    expected_keys = {
        "graph",
        "namespaces",
        "classes",
        "class_metadata",
        "object_properties",
        "object_property_metadata",
        "datatype_properties",
        "datatype_property_metadata",
        "datatypes",
        "datatype_metadata",
        "resource_metadata",
        "rdf_resources",
        "rdf_dict",
    }

    assert set(result) == expected_keys


# =====================================================================
# Document-assertion provenance
# =====================================================================



# =====================================================================
# Document-assertion provenance
# =====================================================================



# =====================================================================
# Document-assertion provenance
# =====================================================================



# =====================================================================
# Document-assertion provenance
# =====================================================================



# =====================================================================
# Document-assertion provenance
# =====================================================================



# =====================================================================
# Document-assertion provenance
# =====================================================================