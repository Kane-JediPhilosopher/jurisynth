from collections import Counter
from rdflib import RDF, RDFS, URIRef, Literal

# ---------------------------------------------------------------------
# Built-in predicates
# ---------------------------------------------------------------------

BUILTIN_PREDICATES = {
    RDF.type,
    RDFS.label,
    RDFS.comment,
}


# ---------------------------------------------------------------------
# Resource type lookup
# ---------------------------------------------------------------------

def build_resource_type_lookup(resolved_triples):
    """
    Build a lookup table:
        resource URI -> set[rdf:type]

    A resource may have multiple rdf:type assertions.
    """

    resource_types = dict()

    for element in resolved_triples:

        triple = element["triple"]

        if triple["predicate"] != RDF.type:
            continue

        resource = triple["subject"]
        rdf_type = triple["object"]

        resource_types.setdefault(resource, set()).add(rdf_type)

    return resource_types


# ---------------------------------------------------------------------
# Main validation function
# ---------------------------------------------------------------------

def validate_triples(resolved_triples, resource_metadata):
    """
    Validate resolved triples against the ontology schema.

    Validation stages
    -----------------

        • Predicate existence
        • Subject domain
        • Object range
        • Literal datatype

    Missing rdf:type assertions are treated as WARNINGS,
    not errors.

    Parameters
    ----------
    resolved_triples : list[dict]

        Expected format:

        {
            "doc_id": str,
            "chunk_id": str,
            "triple": {
                "subject": URIRef,
                "predicate": URIRef,
                "object": URIRef | Literal
            }
        }

    resource_metadata : dict

        Ontology metadata dictionary.

    Returns
    -------
    dict

        {
            "validated_triples": [...],   # valid + warning
            "validation_errors": [...],  # invalid
            "statistics": {...}
        }
    """

    # -------------------------------------------------------------
    # Build resource type cache
    # -------------------------------------------------------------

    resource_types = build_resource_type_lookup(resolved_triples)

    validated_triples = list()
    validation_errors = list()

    statistics = Counter()

    # -------------------------------------------------------------
    # Validate each triple
    # -------------------------------------------------------------

    for element in resolved_triples:

        statistics["total"] += 1
        triple = element["triple"]

        subject = triple["subject"]
        predicate = triple["predicate"]
        obj = triple["object"]

        errors = list()
        warnings = list()

        # ---------------------------------------------------------
        # Built-in RDF predicates
        # ---------------------------------------------------------

        if predicate in BUILTIN_PREDICATES:

            updated = {
                **element,
                "validation_status": "valid",
                "warnings": [],
            }

            validated_triples.append(updated)
            statistics["valid"] += 1

            continue

        # ---------------------------------------------------------
        # Predicate existence
        # ---------------------------------------------------------

        metadata = resource_metadata.get(str(predicate))

        if metadata is None:
            warnings.append("unknown_predicate")

        else:
            # =====================================================
            # Domain validation
            # =====================================================

            expected_domains = metadata.get("domain", set())

            if expected_domains:
                subject_types = resource_types.get(subject)

                if not subject_types:
                    warnings.append("missing_subject_type")

                elif subject_types.isdisjoint(expected_domains):
                    errors.append("domain_violation")

            # =====================================================
            # Range validation
            # =====================================================

            expected_ranges = metadata.get("range", set())
            property_type = metadata.get("type")

            # -----------------------------------------------------
            # Object property
            # -----------------------------------------------------

            if property_type == "object property":

                if not isinstance(obj, URIRef):
                    errors.append("expected_resource")

                elif expected_ranges:
                    object_types = resource_types.get(obj)

                    if not object_types:
                        warnings.append("missing_object_type")

                    elif object_types.isdisjoint(expected_ranges):
                        errors.append("range_violation")

            # -----------------------------------------------------
            # Datatype property
            # -----------------------------------------------------

            elif property_type == "datatype property":

                if not isinstance(obj, Literal):
                    errors.append("expected_literal")

                elif expected_ranges:
                    literal_datatype = obj.datatype

                    if literal_datatype not in expected_ranges:
                        errors.append("datatype_violation")

        # ---------------------------------------------------------
        # Finalise
        # ---------------------------------------------------------

        if errors:

            statistics["invalid"] += 1

            for error in errors:
                statistics[error] += 1

            updated = {
                **element,
                "validation_status": "invalid",
                "warnings": warnings,
                "errors": errors,
            }

            validation_errors.append(updated)

        else:

            status = "warning" if warnings else "valid"

            statistics[status] += 1

            for warning in warnings:
                statistics[warning] += 1

            updated = {
                **element,
                "validation_status": status,
                "warnings": warnings,
            }

            validated_triples.append(updated)

    return {
        "validated_triples": validated_triples,
        "validation_errors": validation_errors,
        "statistics": dict(statistics),
    }