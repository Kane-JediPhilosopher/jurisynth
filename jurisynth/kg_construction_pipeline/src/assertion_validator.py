from collections import Counter
import re

from rdflib import Literal, URIRef
from rdflib.namespace import RDF, RDFS, XSD


# ---------------------------------------------------------------------
# Built-in predicates
# ---------------------------------------------------------------------

BUILTIN_PREDICATES = {
    RDF.type,
    RDFS.label,
    RDFS.comment,
}

# ---------------------------------------------------------------------
# Objectless assertion heuristic
# ---------------------------------------------------------------------

INCOMPLETE_PREDICATE_SUFFIXES = {
    "for",
    "from",
    "to",
    "of",
    "with",
    "by",
    "according_to",
    "based_on",
    "in",
    "on",
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
# Objectless assertion heuristic
# ---------------------------------------------------------------------

def is_proposition_complete(predicate):
    """
    Determine whether an objectless predicate expresses a
    semantically complete proposition.

    Returns
    -------
    bool
        True if the predicate can reasonably stand as a
        complete proposition without an explicit object.

    Notes
    -----
    This is intentionally deterministic and conservative.
    It does not attempt to infer a missing object.
    """

    predicate = str(predicate).strip()

    if not predicate:
        return False

    # Predicates containing explicit relational/complement
    # constructions are treated as incomplete.
    incomplete_patterns = (
        r"\bas_between\b",
        r"\baccording_to\b",
        r"\bfrom_whom\b",
        r"\bto_whom\b",
        r"\bwith_whom\b",
        r"\bfor_whom\b",
        r"\bin_which\b",
        r"\bon_which\b",
        r"\bunder_which\b",
        r"\bderived_from\b",
        r"\bobtained_from\b",
        r"\bdependent_on\b",
        r"\bsubject_to\b",
        r"\bapplicable_to\b",
        r"\brefer_to\b",
        r"\brelate_to\b",
        r"\bconsist_of\b",
        r"\bcomposed_of\b",
    )

    if any(
        re.search(pattern, predicate)
        for pattern in incomplete_patterns
    ):
        return False

    # A predicate containing an explicit interrogative/complement
    # structure is unlikely to be a complete proposition.
    if re.search(
        r"\b(what|which|whom|whose|where|when|how)\b",
        predicate,
    ):
        return False

    # Otherwise, treat the predicate as a proposition.
    return True



def is_structurally_incomplete_predicate(predicate):
    """
    Determine whether an objectless assertion appears structurally
    incomplete based on the predicate's final lexical component.

    This is deliberately conservative. It does not attempt to infer
    legal semantics or decompose custom predicates.
    """
    predicate_text = str(predicate)

    final_component = predicate_text.rsplit("/", 1)[-1]

    return any(
        final_component.endswith(f"_{suffix}")
        or final_component == suffix
        for suffix in INCOMPLETE_PREDICATE_SUFFIXES
    )


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
    OBJECTLESS_DEBUG_LIMIT = 50
    objectless_debug_count = 0

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
        # Handle object-less assertions
        # -------------------------------------------------------------

        if obj is None:

            if is_structurally_incomplete_predicate(predicate):
                validation_errors.append({
                    **element,
                    "validation_status": "invalid",
                    "warnings": [],
                    "errors": ["missing_object"],
                })

                statistics["invalid"] += 1
                statistics["missing_object"] += 1

                continue

            # The predicate appears to express a complete proposition.
            # Represent its truth value explicitly as xsd:boolean true.
            updated_assertion = {
                **assertion,
                "object": Literal(
                    True,
                    datatype=XSD.boolean,
                ),
            }

            updated = {
                **element,
                "assertion": updated_assertion,
                "validation_status": "valid",
                "warnings": [],
            }

            validated_assertions.append(updated)

            statistics["valid"] += 1
            statistics["objectless_true"] += 1

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