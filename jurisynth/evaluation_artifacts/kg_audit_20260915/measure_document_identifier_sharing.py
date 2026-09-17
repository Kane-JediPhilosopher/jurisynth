"""Measure document-URI sharing from the stored RDF labels, read-only."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from pyoxigraph import Store


QUERY = """
SELECT (COUNT(?doc) AS ?rdf_document_uris)
       (SUM(?labels) AS ?source_labels)
       (SUM(IF(?labels > 1, 1, 0)) AS ?shared_document_uris)
       (SUM(IF(?labels > 1, ?labels, 0)) AS ?source_docs_sharing_uri)
       (MAX(?labels) AS ?largest_group)
WHERE {
  {
    SELECT ?doc (COUNT(DISTINCT ?label) AS ?labels)
    WHERE {
      GRAPH ?g { ?doc <http://www.w3.org/2000/01/rdf-schema#label> ?label }
      FILTER(STRSTARTS(STR(?doc), "http://jurisynth/source/document/"))
    }
    GROUP BY ?doc
  }
}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", type=Path, default=Path("jurisynth/global_artifacts/oxigraph"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")

    started = time.perf_counter()
    store = Store.read_only(str(args.store))
    solutions = store.query(QUERY)
    variables = [str(getattr(variable, "value", variable)) for variable in solutions.variables]
    rows = list(solutions)
    if len(rows) != 1:
        raise RuntimeError(f"Expected one aggregate row; received {len(rows)}")
    counts = {
        name: int(str(getattr(value, "value", value)))
        for name, value in zip(variables, rows[0])
    }
    counts["seconds"] = round(time.perf_counter() - started, 6)
    args.output.write_text(json.dumps(counts, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
