from pathlib import Path

from jurisynth.contracts import RetrievalRequest
from jurisynth.retrieval_mech.document_metadata import (
    DocumentMetadataStore,
    build_document_metadata_sidecar,
)


def _write_document(root: Path, batch: str, document_id: str, body: str) -> None:
    directory = root / batch / "processed_docs"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{document_id}.html").write_text(body, encoding="utf-8")


def _store(tmp_path: Path) -> DocumentMetadataStore:
    source = tmp_path / "eu_legislation"
    _write_document(source, "batch_0001", "L_202401689EN", """
        <p class="oj-doc-ti">REGULATION (EU) 2024/1689 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL</p>
        <p class="oj-doc-ti">laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)</p>
        <p class="oj-normal">ELI: http://data.europa.eu/eli/reg/2024/1689/oj</p>
    """)
    _write_document(source, "batch_0001", "L_2016119EN.01000101", """
        <p class="doc-ti">REGULATION (EU) 2016/679 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL</p>
        <p class="doc-ti">on the protection of personal data (General Data Protection Regulation)</p>
    """)
    _write_document(source, "batch_0001", "L_2018127EN.01000201", """
        <p class="doc-ti">Corrigendum to Regulation (EU) 2016/679</p>
        <p class="doc-ti">(General Data Protection Regulation)</p>
    """)
    _write_document(source, "batch_0001", "L_2018159EN.01003101", """
        <p class="doc-ti">COUNCIL DECISION (EU) 2018/893 concerning an EEA Agreement amendment</p>
        <p class="doc-ti">(General Data Protection Regulation)</p>
    """)
    _write_document(source, "batch_0001", "L_2017117EN.01017601", """
        <p class="doc-ti">REGULATION (EU) 2017/746 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL</p>
        <p class="doc-ti">on in vitro diagnostic medical devices</p>
    """)
    _write_document(source, "batch_0001", "L_202590901EN", """
        <p class="oj-doc-ti">Corrigendum to Regulation (EU) 2024/1679</p>
        <p class="oj-normal">ELI: http://data.europa.eu/eli/reg/2024/1679/corrigendum/2025-11-14/oj</p>
    """)
    _write_document(source, "batch_0001", "m8004", '<p class="doc-ti">Guidance on trustworthy systems</p>')
    _write_document(source, "batch_0001", "shared-reg", """
        <p class="doc-ti">REGULATION (EU) 2000/1 (Shared Code)</p>
    """)
    _write_document(source, "batch_0001", "shared-dec", """
        <p class="doc-ti">DECISION (EU) 2001/2 (Shared Code)</p>
    """)
    destination = tmp_path / "document_metadata.sqlite"
    result = build_document_metadata_sidecar(source, destination)
    assert result["documents"] == 9
    return DocumentMetadataStore(destination)


def test_sidecar_resolves_leaf_aliases_and_preserves_unknowns(tmp_path):
    store = _store(tmp_path)
    context = store.resolve_request_scope(RetrievalRequest("q", "What duties arise under the AI Act?"))

    assert context.explicitly_scoped
    assert "citation:regulation:2024:1689" in context.target_keys
    assert store.classify_document("L_202401689EN", context) == "in_scope"
    assert store.classify_document("L_2016119EN.01000101", context) == "cross_instrument"
    assert store.classify_document("m8004", context) == "unknown"


def test_gdpr_alias_resolves_one_canonical_instrument_despite_topical_collision(tmp_path):
    store = _store(tmp_path)
    context = store.resolve_request_scope(
        RetrievalRequest("q", "What obligations arise under the GDPR?")
    )

    assert context.target_keys == frozenset({"citation:regulation:2016:679"})
    assert store.classify_document("L_2016119EN.01000101", context) == "in_scope"
    assert store.classify_document("L_2018159EN.01003101", context) == "cross_instrument"


def test_multi_regime_leaf_preserves_ai_act_and_gdpr_scopes(tmp_path):
    store = _store(tmp_path)
    context = store.resolve_request_scope(
        RetrievalRequest("q", "How do the AI Act and GDPR interact?")
    )

    assert context.target_keys == frozenset({
        "citation:regulation:2024:1689",
        "citation:regulation:2016:679",
    })


def test_multi_regime_leaf_preserves_ai_act_and_ivdr_citations(tmp_path):
    store = _store(tmp_path)
    context = store.resolve_request_scope(RetrievalRequest(
        "q",
        "How do the AI Act and Regulation (EU) 2017/746 (IVDR) interact?",
    ))

    assert context.target_keys == frozenset({
        "citation:regulation:2024:1689",
        "citation:regulation:2017:746",
    })


def test_single_instrument_leaf_remains_authoritative_over_context_and_constraints(tmp_path):
    store = _store(tmp_path)
    context = store.resolve_request_scope(RetrievalRequest(
        "q",
        "What duties arise under the AI Act?",
        contextual_facts=["The same leaf also asks about Regulation (EU) 2016/679."],
        constraints={"legislation": ["Regulation (EU) 2000/1"]},
    ))

    assert context.target_keys == frozenset({"citation:regulation:2024:1689"})
    assert context.source == "leaf_query"


def test_multiple_leaf_local_facts_are_unioned_when_leaf_has_no_instrument(tmp_path):
    store = _store(tmp_path)
    context = store.resolve_request_scope(RetrievalRequest(
        "q",
        "How do the two regimes interact?",
        contextual_facts=[
            "The first regime is Regulation (EU) 2024/1689.",
            "The second regime is Regulation (EU) 2016/679.",
        ],
    ))

    assert context.target_keys == frozenset({
        "citation:regulation:2024:1689",
        "citation:regulation:2016:679",
    })
    assert context.source == "leaf_local_facts"


def test_truly_ambiguous_alias_remains_unresolved(tmp_path):
    store = _store(tmp_path)

    context = store.resolve_request_scope(
        RetrievalRequest("q", "What does the Shared Code require?")
    )

    assert not context.explicitly_scoped


def test_unrelated_text_does_not_broaden_scope(tmp_path):
    store = _store(tmp_path)

    context = store.resolve_request_scope(
        RetrievalRequest("q", "What obligations apply to an ordinary provider?")
    )

    assert not context.explicitly_scoped


def test_global_constraints_do_not_become_primary_leaf_scope(tmp_path):
    store = _store(tmp_path)
    request = RetrievalRequest(
        "q", "What obligations apply to the provider?",
        constraints={"legislation": ["AI Act (Regulation (EU) 2024/1689)"]},
    )
    assert not store.resolve_request_scope(request).explicitly_scoped


def test_contextual_fact_is_used_only_when_leaf_has_no_explicit_instrument(tmp_path):
    store = _store(tmp_path)
    request = RetrievalRequest(
        "q", "What obligations apply to the provider?",
        contextual_facts=["The question concerns Regulation (EU) 2024/1689."],
    )
    context = store.resolve_request_scope(request)
    assert context.source == "leaf_local_facts"
    assert store.classify_document("L_202401689EN", context) == "in_scope"


def test_corrigendum_identity_comes_from_eli_not_filename(tmp_path):
    store = _store(tmp_path)
    context = store.resolve_request_scope(
        RetrievalRequest("q", "What changed in Regulation (EU) 2024/1679?")
    )
    record = store.get("L_202590901EN")
    assert record is not None
    assert "citation:regulation:2024:1679" in record.canonical_keys
    assert store.classify_document("L_202590901EN", context) == "in_scope"
