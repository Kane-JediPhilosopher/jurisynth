from collections import Counter

from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS


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

def build_resource_type_lookup(scored_assertions):
    """
    Build a lookup table:

        resource URI -> set[rdf:type]

    A resource may have multiple rdf:type assertions.
    """
    resource_types = dict()

    for element in scored_assertions:
        assertion = element["assertion"]

        if assertion["predicate"] != RDF.type:
            continue

        resource = assertion["subject"]
        rdf_type = assertion["object"]

        resource_types.setdefault(
            resource,
            set()
        ).add(rdf_type)

    return resource_types


# ---------------------------------------------------------------------
# Main validation
# ---------------------------------------------------------------------

def validate_assertions(
    resolved_assertions,
    resource_metadata,
):
    """
    Validate resolved assertions against the ontology schema.

    Validation stages
    -----------------
        • Predicate existence
        • Subject domain
        • Object range
        • Literal datatype

    Missing rdf:type assertions are treated as warnings,
    not errors.

    Modifiers are preserved unchanged and are not validated here.

    Returns
    -------
    dict
        {
            "validated_assertions": list[dict],
            "validation_errors": list[dict],
            "statistics": dict
        }
    """
    resource_types = build_resource_type_lookup(
        resolved_assertions
    )

    validated_assertions = list()
    validation_errors = list()
    statistics = Counter()

    for element in resolved_assertions:
        statistics["total"] += 1

        assertion = element["assertion"]

        subject = assertion["subject"]
        predicate = assertion["predicate"]
        obj = assertion["object"]

        errors = list()
        warnings = list()


        # -------------------------------------------------------------
        # Filter object-less assertions
        # -------------------------------------------------------------

        if obj is None:
            validation_errors.append({
                **element,
                "validation_status": "invalid",
                "warnings": [],
                "errors": ["missing_object"],
            })
            statistics["invalid"] += 1
            statistics["missing_object"] += 1
            continue


        # -------------------------------------------------------------
        # Built-in RDF predicates
        # -------------------------------------------------------------

        if predicate in BUILTIN_PREDICATES:
            updated = {
                **element,
                "validation_status": "valid",
                "warnings": [],
            }

            validated_assertions.append(updated)
            statistics["valid"] += 1

            continue

        # -------------------------------------------------------------
        # Predicate existence
        # -------------------------------------------------------------

        metadata = resource_metadata.get(
            str(predicate)
        )

        if metadata is None:
            warnings.append(
                "unknown_predicate"
            )

        else:

            # =========================================================
            # Domain validation
            # =========================================================

            expected_domains = metadata.get(
                "domain",
                set()
            )

            if expected_domains:
                subject_types = resource_types.get(
                    subject
                )

                if not subject_types:
                    warnings.append(
                        "missing_subject_type"
                    )

                elif subject_types.isdisjoint(
                    expected_domains
                ):
                    errors.append(
                        "domain_violation"
                    )

            # =========================================================
            # Range validation
            # =========================================================

            expected_ranges = metadata.get(
                "range",
                set()
            )

            property_type = metadata.get(
                "type"
            )

            # ---------------------------------------------------------
            # Object property
            # ---------------------------------------------------------

            if property_type == "object property":

                if not isinstance(
                    obj,
                    URIRef
                ):
                    errors.append(
                        "expected_resource"
                    )

                elif expected_ranges:
                    object_types = resource_types.get(
                        obj
                    )

                    if not object_types:
                        warnings.append(
                            "missing_object_type"
                        )

                    elif object_types.isdisjoint(
                        expected_ranges
                    ):
                        errors.append(
                            "range_violation"
                        )

            # ---------------------------------------------------------
            # Datatype property
            # ---------------------------------------------------------

            elif property_type == "datatype property":

                if not isinstance(
                    obj,
                    Literal
                ):
                    errors.append(
                        "expected_literal"
                    )

                elif expected_ranges:
                    literal_datatype = obj.datatype

                    if (
                        literal_datatype
                        not in expected_ranges
                    ):
                        errors.append(
                            "datatype_violation"
                        )

        # -------------------------------------------------------------
        # Finalise validation result
        # -------------------------------------------------------------

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
            status = (
                "warning"
                if warnings
                else "valid"
            )

            statistics[status] += 1

            for warning in warnings:
                statistics[warning] += 1

            updated = {
                **element,
                "validation_status": status,
                "warnings": warnings,
            }

            validated_assertions.append(updated)

    return {
        "validated_assertions": validated_assertions,
        "validation_errors": validation_errors,
        "statistics": dict(statistics),
    }


# ---------------------------------------------------------------------
# Module execution helper
# ---------------------------------------------------------------------

def run_assertion_validation(
    resolved_assertions,
    resource_metadata,
):
    """
    Run assertion validation and return the pipeline outputs.

    This function is the module-level entry point used by the
    pipeline orchestrator.
    """
    validation = validate_assertions(
        resolved_assertions,
        resource_metadata,
    )

    return (
        validation["validated_assertions"],
        validation["validation_errors"],
        validation["statistics"],
    )