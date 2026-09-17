"""Read-only structural audit of the global Jurisynth Oxigraph store."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from pyoxigraph import Store


QUERIES = {
    "graph_partition": """
        SELECT ?kind (COUNT(*) AS ?quads) (COUNT(DISTINCT ?g) AS ?graphs)
        WHERE {
          GRAPH ?g { ?s ?p ?o }
          BIND(IF(STRSTARTS(STR(?g), "http://jurisynth/source/chunk/"), "chunk",
               IF(STRSTARTS(STR(?g), "http://jurisynth/source/document/"), "document",
               IF(STR(?g) = "http://jurisynth/source/assertion/", "assertion", "other"))) AS ?kind)
        }
        GROUP BY ?kind
    """,
    "types": """
        SELECT ?o (COUNT(*) AS ?n)
        WHERE { GRAPH ?g { ?s a ?o } }
        GROUP BY ?o ORDER BY DESC(?n) LIMIT 30
    """,
    "chunk_shape": """
        SELECT (COUNT(*) AS ?triples)
               (COUNT(DISTINCT ?s) AS ?subjects)
               (COUNT(DISTINCT ?p) AS ?predicates)
               (COUNT(DISTINCT ?o) AS ?objects)
               (COUNT(DISTINCT ?g) AS ?chunks)
        WHERE {
          GRAPH ?g { ?s ?p ?o }
          FILTER(STRSTARTS(STR(?g), "http://jurisynth/source/chunk/"))
        }
    """,
    "chunk_object_kind": """
        SELECT ?kind (COUNT(*) AS ?n)
        WHERE {
          GRAPH ?g { ?s ?p ?o }
          FILTER(STRSTARTS(STR(?g), "http://jurisynth/source/chunk/"))
          BIND(IF(isIRI(?o), "iri", IF(isLiteral(?o), "literal", "other")) AS ?kind)
        }
        GROUP BY ?kind
    """,
    "predicate_namespace": """
        SELECT ?ns (COUNT(*) AS ?n) (COUNT(DISTINCT ?p) AS ?distinct)
        WHERE {
          GRAPH ?g { ?s ?p ?o }
          FILTER(STRSTARTS(STR(?g), "http://jurisynth/source/chunk/"))
          BIND(IF(STRSTARTS(STR(?p), "http://jurisynth/data/"), "jurisynth_data",
               IF(STRSTARTS(STR(?p), "http://publications.europa.eu/ontology/cdm#"), "cdm", "other")) AS ?ns)
        }
        GROUP BY ?ns
    """,
    "top_semantic_predicates": """
        SELECT ?p (COUNT(*) AS ?n)
        WHERE {
          GRAPH ?g { ?s ?p ?o }
          FILTER(STRSTARTS(STR(?g), "http://jurisynth/source/chunk/"))
        }
        GROUP BY ?p ORDER BY DESC(?n) LIMIT 100
    """,
    "top_subjects": """
        SELECT ?s (COUNT(*) AS ?n)
        WHERE {
          GRAPH ?g { ?s ?p ?o }
          FILTER(STRSTARTS(STR(?g), "http://jurisynth/source/chunk/"))
        }
        GROUP BY ?s ORDER BY DESC(?n) LIMIT 50
    """,
    "top_objects": """
        SELECT ?o (COUNT(*) AS ?n)
        WHERE {
          GRAPH ?g { ?s ?p ?o }
          FILTER(STRSTARTS(STR(?g), "http://jurisynth/source/chunk/"))
        }
        GROUP BY ?o ORDER BY DESC(?n) LIMIT 50
    """,
    "modifier_links": """
        SELECT (COUNT(*) AS ?links) (COUNT(DISTINCT ?a) AS ?assertions)
        WHERE {
          GRAPH <http://jurisynth/source/assertion/> {
            ?a <http://jurisynth/source/has_modifier> ?m .
          }
        }
    """,
    "assertion_component_counts": """
        SELECT ?component (COUNT(*) AS ?values) (COUNT(DISTINCT ?a) AS ?assertions)
        WHERE {
          VALUES (?property ?component) {
            (<http://jurisynth/source/subject> "subject")
            (<http://jurisynth/source/predicate> "predicate")
            (<http://jurisynth/source/object> "object")
            (<http://jurisynth/source/source_chunk> "source_chunk")
          }
          GRAPH <http://jurisynth/source/assertion/> { ?a ?property ?value }
        }
        GROUP BY ?component ORDER BY ?component
    """,
}


def normalize(value: object) -> str:
    return str(getattr(value, "value", value))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", type=Path, default=Path("jurisynth/global_artifacts/oxigraph"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")

    opened = time.perf_counter()
    store = Store.read_only(str(args.store))
    result: dict[str, object] = {
        "store": str(args.store),
        "quad_count": len(store),
        "open_seconds": round(time.perf_counter() - opened, 6),
        "queries": {},
    }
    for name, query in QUERIES.items():
        started = time.perf_counter()
        solutions = store.query(query)
        variables = [str(getattr(variable, "value", variable)) for variable in solutions.variables]
        rows = [
            {name: normalize(value) for name, value in zip(variables, row)}
            for row in solutions
        ]
        result["queries"][name] = {
            "seconds": round(time.perf_counter() - started, 6),
            "rows": rows,
        }
        print(json.dumps({"query": name, "seconds": result["queries"][name]["seconds"], "row_count": len(rows)}), flush=True)

    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
