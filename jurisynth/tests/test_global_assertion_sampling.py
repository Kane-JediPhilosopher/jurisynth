import json
import pickle
import pytest
from types import SimpleNamespace

from jurisynth.contracts import RetrievalRequest, SourceChunk
from jurisynth.run_global_assertion_evaluation import (
    ControlledAssertionInterpreter,
    _batch_stratified_cases,
)
from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever
from jurisynth.table_rdf_enricher import chunk_uri


def test_sampler_selects_distinct_batches_with_document_qualified_gold(tmp_path):
    batches, sources = [], {}
    for number in range(3):
        document = f"doc_{number}"
        metadata = tmp_path / f"batch_{number}.pkl"
        with metadata.open("wb") as handle:
            pickle.dump({0: {"doc_id": document, "chunk_id": "chunk_1", "content": "An operator must retain records."}}, handle)
        batches.append({"batch_id": f"batch_{number}", "chunk_metadata": str(metadata)})
        sources[str(chunk_uri(document, "chunk_1"))] = SourceChunk("chunk_1", document, "An operator must retain records.")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"batches": batches}), encoding="utf-8")

    class Dataset:
        def select_rows(self, query):
            graph = next(identifier for identifier in sources if f"<{identifier}>" in query)
            return [("https://example.test/operator", "https://example.test/must_retain", "https://example.test/records", graph)]

    artifacts = SimpleNamespace(dataset=Dataset(), resolve_chunk=sources.get,
                                chunk_lookup=SimpleNamespace(has_ambiguous_provenance=lambda identifier: False))
    args = SimpleNamespace(manifest=manifest, seed=312, limit=2, chunk_trials_per_batch=8, query_style="subject-predicate")
    cases, plan = _batch_stratified_cases(args, artifacts)
    assert len(cases) == 2
    assert len({item["batch_id"] for item in plan["selections"]}) == 2
    assert {case.expected_document_id for case in cases} == {item["document_id"] for item in plan["selections"]}
    assert _batch_stratified_cases(args, artifacts)[0] == cases


@pytest.mark.asyncio
async def test_controlled_assertion_interpreter_extracts_fixed_subject_and_predicate_fields():
    interpreter = ControlledAssertionInterpreter()
    entities, relations = await interpreter.interpret(RetrievalRequest(
        "q1",
        "According to the source, what is stated about 'the provider' in relation to 'shall ensure'?",
    ))

    assert [(item.concept_id, item.text) for item in entities] == [("entity_1", "the provider")]
    assert [(item.concept_id, item.text) for item in relations] == [("relation_1", "shall ensure")]


@pytest.mark.asyncio
async def test_controlled_assertion_interpreter_rejects_queries_outside_fixed_template():
    with pytest.raises(ValueError, match="fixed subject/predicate template"):
        await ControlledAssertionInterpreter().interpret(RetrievalRequest("q1", "What must a provider do?"))


def test_experimental_conjunctive_lookup_short_circuits_independent_scan():
    class Store:
        independent_calls = 0

        def select_rows(self, query):
            raise AssertionError("The indexed refinement must not issue SPARQL.")

        def matching_subject_predicate_quads(self, subject, predicate, *, limit):
            return iter((("https://example.test/s", "https://example.test/p", "https://example.test/o",
                          "http://jurisynth/source/chunk/doc/chunk_1"),))

        def matching_quads(self, entities, relations, *, max_per_seed):
            self.independent_calls += 1
            return iter(())

    store = Store()
    retriever = DirectRDFRetriever(store, object(), lambda _graph: None, max_quads_per_seed=50)
    rows = list(retriever._matching_quads({"https://example.test/s"}, {"https://example.test/p"}))

    assert len(rows) == 1
    assert store.independent_calls == 0


def test_experimental_conjunctive_lookup_preserves_independent_fallback():
    fallback = ("https://example.test/s", "https://example.test/other", "https://example.test/o",
                "http://jurisynth/source/chunk/doc/chunk_1")

    class Store:
        independent_calls = 0

        def select_rows(self, query):
            raise AssertionError("The indexed refinement must not issue SPARQL.")

        def matching_subject_predicate_quads(self, subject, predicate, *, limit):
            return iter(())

        def matching_quads(self, entities, relations, *, max_per_seed):
            self.independent_calls += 1
            return iter((fallback,))

    store = Store()
    retriever = DirectRDFRetriever(store, object(), lambda _graph: None, max_quads_per_seed=50)

    assert list(retriever._matching_quads({"https://example.test/s"}, {"https://example.test/p"})) == [fallback]
    assert store.independent_calls == 1
