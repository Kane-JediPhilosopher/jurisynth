from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD

from assertion_validator import (
    build_resource_type_lookup,
    is_proposition_complete,
    is_structurally_incomplete_predicate,
    validate_assertions,
    run_assertion_validation,
)


# =====================================================================
# Helpers
# =====================================================================

def make_assertion(subject, predicate, obj, assertion_id=0):
    return {
        "doc_id": "doc1",
        "chunk_id": "chunk1",
        "assertion_id": assertion_id,
        "assertion": {
            "subject": subject,
            "predicate": predicate,
            "object": obj,
        },
        "modifiers": [],
    }

def make_metadata(
    property_type,
    domain=None,
    range_=None,
):
    return {
        "type": property_type,
        "domain": set(domain or []),
        "range": set(range_ or []),
    }


# =====================================================================
# Resource type lookup
# =====================================================================

def test_build_resource_type_lookup_collects_multiple_types():
    animal = URIRef("http://example.org/Animal")
    mammal = URIRef("http://example.org/Mammal")
    vertebrate = URIRef("http://example.org/Vertebrate")

    assertions = [
        make_assertion(animal, RDF.type, mammal),
        make_assertion(animal, RDF.type, vertebrate),
    ]

    result = build_resource_type_lookup(assertions)

    assert result[animal] == {mammal, vertebrate}


def test_build_resource_type_lookup_ignores_non_type_assertions():
    animal = URIRef("http://example.org/Animal")
    label = URIRef("http://example.org/label")

    assertions = [
        make_assertion(
            animal,
            label,
            Literal("cat"),
        )
    ]

    result = build_resource_type_lookup(assertions)

    assert result == {}


# =====================================================================
# Objectless predicate heuristics
# =====================================================================

def test_is_proposition_complete_accepts_complete_predicates():
    assert is_proposition_complete("exists")
    assert is_proposition_complete("is_active")
    assert is_proposition_complete("applies")


def test_is_proposition_complete_rejects_incomplete_predicates():
    assert not is_proposition_complete("applicable_to")
    assert not is_proposition_complete("derived_from")
    assert not is_proposition_complete("according_to")
    assert not is_proposition_complete("refer_to")


def test_is_proposition_complete_rejects_standalone_interrogatives():
    assert not is_proposition_complete("what")
    assert not is_proposition_complete("which")
    assert not is_proposition_complete("whom")
    assert not is_proposition_complete("whose")
    assert not is_proposition_complete("where")
    assert not is_proposition_complete("when")
    assert not is_proposition_complete("how")
    

def test_is_proposition_complete_handles_empty_predicate():
    assert is_proposition_complete("") is False
    assert is_proposition_complete("   ") is False


# =====================================================================
# Structural incompleteness
# =====================================================================

def test_structurally_incomplete_predicate_detects_suffixes():
    assert is_structurally_incomplete_predicate(
        "http://example.org/applicable_to"
    )
    assert is_structurally_incomplete_predicate(
        "http://example.org/derived_from"
    )
    assert is_structurally_incomplete_predicate(
        "http://example.org/with"
    )


def test_structurally_incomplete_predicate_accepts_complete_predicate():
    assert not is_structurally_incomplete_predicate(
        "http://example.org/applies"
    )
    assert not is_structurally_incomplete_predicate(
        "http://example.org/exists"
    )


# =====================================================================
# Positive validation cases
# =====================================================================

def test_valid_object_property():
    subject = URIRef("http://example.org/A")
    obj = URIRef("http://example.org/B")
    thing = URIRef("http://example.org/Thing")
    relates_to = URIRef("http://example.org/relates_to")

    assertions = [
        make_assertion(subject, RDF.type, thing, 0),
        make_assertion(obj, RDF.type, thing, 1),
        make_assertion(subject, relates_to, obj, 2),
    ]

    metadata = {
        str(relates_to): make_metadata(
            "object property",
            domain={thing},
            range_={thing},
        )
    }

    result = validate_assertions(assertions, metadata)

    assert result["statistics"]["valid"] == 3
    assert result["validation_errors"] == []


def test_valid_datatype_property():
    subject = URIRef("http://example.org/A")
    thing = URIRef("http://example.org/Thing")
    age = URIRef("http://example.org/age")

    assertions = [
        make_assertion(subject, RDF.type, thing),
        make_assertion(
            subject,
            age,
            Literal(42, datatype=XSD.integer),
        ),
    ]

    metadata = {
        str(age): make_metadata(
            "datatype property",
            domain={thing},
            range_={XSD.integer},
        )
    }

    result = validate_assertions(assertions, metadata)

    assert result["statistics"]["valid"] == 2
    assert result["validation_errors"] == []


# =====================================================================
# Negative validation cases
# =====================================================================

def test_domain_violation():
    subject = URIRef("http://example.org/A")
    wrong_type = URIRef("http://example.org/Wrong")
    required_type = URIRef("http://example.org/Required")
    predicate = URIRef("http://example.org/p")

    assertions = [
        make_assertion(subject, RDF.type, wrong_type),
        make_assertion(
            subject,
            predicate,
            URIRef("http://example.org/B"),
        ),
    ]

    metadata = {
        str(predicate): make_metadata(
            "object property",
            domain={required_type},
        )
    }

    result = validate_assertions(assertions, metadata)

    assert result["statistics"]["domain_violation"] == 1
    assert result["statistics"]["invalid"] == 1


def test_range_violation():
    subject = URIRef("http://example.org/A")
    obj = URIRef("http://example.org/B")
    subject_type = URIRef("http://example.org/Subject")
    wrong_type = URIRef("http://example.org/Wrong")
    required_type = URIRef("http://example.org/Required")
    predicate = URIRef("http://example.org/p")

    assertions = [
        make_assertion(subject, RDF.type, subject_type),
        make_assertion(obj, RDF.type, wrong_type),
        make_assertion(subject, predicate, obj),
    ]

    metadata = {
        str(predicate): make_metadata(
            "object property",
            domain={subject_type},
            range_={required_type},
        )
    }

    result = validate_assertions(assertions, metadata)

    assert result["statistics"]["range_violation"] == 1


def test_object_property_rejects_literal():
    subject = URIRef("http://example.org/A")
    predicate = URIRef("http://example.org/p")

    assertions = [
        make_assertion(
            subject,
            predicate,
            Literal("not a resource"),
        )
    ]

    metadata = {
        str(predicate): make_metadata("object property")
    }

    result = validate_assertions(assertions, metadata)

    assert result["statistics"]["expected_resource"] == 1
    assert result["statistics"]["invalid"] == 1


def test_datatype_property_rejects_resource():
    subject = URIRef("http://example.org/A")
    predicate = URIRef("http://example.org/p")
    obj = URIRef("http://example.org/B")

    assertions = [
        make_assertion(subject, predicate, obj)
    ]

    metadata = {
        str(predicate): make_metadata("datatype property")
    }

    result = validate_assertions(assertions, metadata)

    assert result["statistics"]["expected_literal"] == 1


def test_datatype_property_rejects_wrong_literal_datatype():
    subject = URIRef("http://example.org/A")
    predicate = URIRef("http://example.org/age")

    assertions = [
        make_assertion(
            subject,
            predicate,
            Literal("forty-two", datatype=XSD.string),
        )
    ]

    metadata = {
        str(predicate): make_metadata(
            "datatype property",
            range_={XSD.integer},
        )
    }

    result = validate_assertions(assertions, metadata)

    assert result["statistics"]["datatype_violation"] == 1


# =====================================================================
# Warning cases
# =====================================================================

def test_unknown_predicate_produces_warning_not_error():
    predicate = URIRef("http://example.org/unknown")

    assertions = [
        make_assertion(
            URIRef("http://example.org/A"),
            predicate,
            URIRef("http://example.org/B"),
        )
    ]

    result = validate_assertions(assertions, {})

    assert result["statistics"]["warning"] == 1
    assert result["statistics"]["unknown_predicate"] == 1
    assert result["validation_errors"] == []


def test_missing_subject_type_produces_warning():
    predicate = URIRef("http://example.org/p")
    required_type = URIRef("http://example.org/Thing")

    assertions = [
        make_assertion(
            URIRef("http://example.org/A"),
            predicate,
            URIRef("http://example.org/B"),
        )
    ]

    metadata = {
        str(predicate): make_metadata(
            "object property",
            domain={required_type},
        )
    }

    result = validate_assertions(assertions, metadata)

    assert result["statistics"]["missing_subject_type"] == 1
    assert result["statistics"]["warning"] == 1
    assert result["validation_errors"] == []


def test_missing_object_type_produces_warning():
    subject = URIRef("http://example.org/A")
    obj = URIRef("http://example.org/B")
    thing = URIRef("http://example.org/Thing")
    predicate = URIRef("http://example.org/p")

    assertions = [
        make_assertion(subject, RDF.type, thing),
        make_assertion(subject, predicate, obj),
    ]

    metadata = {
        str(predicate): make_metadata(
            "object property",
            domain={thing},
            range_={thing},
        )
    }

    result = validate_assertions(assertions, metadata)

    assert result["statistics"]["missing_object_type"] == 1
    assert result["statistics"]["warning"] == 1


# =====================================================================
# Objectless assertions
# =====================================================================

def test_complete_objectless_assertion_becomes_true_literal():
    subject = URIRef("http://example.org/A")
    predicate = URIRef("http://example.org/exists")

    assertions = [
        make_assertion(subject, predicate, None)
    ]

    result = validate_assertions(assertions, {})

    validated = result["validated_assertions"][0]

    assert validated["validation_status"] == "valid"
    assert validated["assertion"]["object"] == Literal(
        True,
        datatype=XSD.boolean,
    )
    assert result["statistics"]["objectless_true"] == 1


def test_incomplete_objectless_assertion_is_invalid():
    subject = URIRef("http://example.org/A")
    predicate = URIRef("http://example.org/applicable_to")

    assertions = [
        make_assertion(subject, predicate, None)
    ]

    result = validate_assertions(assertions, {})

    assert result["statistics"]["missing_object"] == 1
    assert result["statistics"]["invalid"] == 1
    assert len(result["validation_errors"]) == 1


# =====================================================================
# Built-in predicates
# =====================================================================

def test_builtin_predicates_are_accepted_without_metadata():
    assertions = [
        make_assertion(
            URIRef("http://example.org/A"),
            RDF.type,
            URIRef("http://example.org/Thing"),
        ),
        make_assertion(
            URIRef("http://example.org/A"),
            RDFS.label,
            Literal("Animal"),
        ),
        make_assertion(
            URIRef("http://example.org/A"),
            RDFS.comment,
            Literal("A comment"),
        ),
    ]

    result = validate_assertions(assertions, {})

    assert result["statistics"]["valid"] == 3
    assert result["validation_errors"] == []


# =====================================================================
# Edge cases / Preservation
# =====================================================================

def test_empty_input_returns_empty_outputs():
    result = validate_assertions([], {})

    assert result["validated_assertions"] == []
    assert result["validation_errors"] == []
    assert result["statistics"] == {}


def test_modifiers_are_preserved():
    element = make_assertion(
        URIRef("http://example.org/A"),
        URIRef("http://example.org/p"),
        URIRef("http://example.org/B"),
    )

    element["modifiers"] = [
        {"type": "negation"},
        {"type": "temporal"},
    ]

    result = validate_assertions([element], {})

    validated = result["validated_assertions"][0]

    assert validated["modifiers"] == element["modifiers"]


def test_multiple_subject_types_satisfy_domain():
    subject = URIRef("http://example.org/A")
    type_a = URIRef("http://example.org/AType")
    type_b = URIRef("http://example.org/BType")
    predicate = URIRef("http://example.org/p")

    assertions = [
        make_assertion(subject, RDF.type, type_a),
        make_assertion(subject, RDF.type, type_b),
        make_assertion(
            subject,
            predicate,
            URIRef("http://example.org/B"),
        ),
    ]

    metadata = {
        str(predicate): make_metadata(
            "object property",
            domain={type_b},
        )
    }

    result = validate_assertions(assertions, metadata)

    assert result["statistics"].get("domain_violation", 0) == 0


# =====================================================================
# Module entry point
# =====================================================================

def test_run_assertion_validation_matches_validate_assertions():
    assertions = [
        make_assertion(
            URIRef("http://example.org/A"),
            URIRef("http://example.org/p"),
            URIRef("http://example.org/B"),
        )
    ]

    metadata = {}

    direct = validate_assertions(assertions, metadata)

    validated, errors, statistics = run_assertion_validation(
        assertions,
        metadata,
    )

    assert validated == direct["validated_assertions"]
    assert errors == direct["validation_errors"]
    assert statistics == direct["statistics"]