"""Checkpointed local-only stage profiling; no production defaults or NIM calls."""
from __future__ import annotations

import argparse
import asyncio
import functools
import json
import os
from pathlib import Path
import threading
import time


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--maximum-seconds', type=float, default=300)
    args = parser.parse_args()
    if args.output.exists() or args.maximum_seconds <= 0:
        raise ValueError('Use a new output path and positive diagnostic deadline.')
    args.output.mkdir(parents=True)
    started = time.perf_counter()
    lock = threading.RLock()
    stage_totals = {}
    case = 'startup'

    def event(name, **payload):
        record = {'event': name, 'case': case, 'elapsed_seconds': round(time.perf_counter()-started, 3), **payload}
        with lock:
            with (args.output / 'events.jsonl').open('a', encoding='utf-8') as handle:
                handle.write(json.dumps(record)+'\n')
            print(json.dumps(record), flush=True)

    def add_time(name, elapsed):
        with lock:
            key = case + ':' + name
            item = stage_totals.setdefault(key, {'calls': 0, 'inclusive_seconds': 0.0})
            item['calls'] += 1
            item['inclusive_seconds'] += elapsed

    def stop():
        event('diagnostic_deadline', maximum_seconds=args.maximum_seconds)
        os._exit(124)

    watchdog = threading.Timer(args.maximum_seconds, stop)
    watchdog.daemon = True
    watchdog.start()
    event('diagnostic_started', api_calls=False, scope='hand-authored concept scaling; not an exact v10 concept replay')
    try:
        import psutil
        available = psutil.virtual_memory().available / 1024**3
        event('ram_preflight', available_gb=round(available, 3))
        if available < 5.5:
            raise RuntimeError('Diagnostic RAM guard: need at least 5.5 GB available.')
        from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
        from jurisynth.retrieval_mech.er_matcher import PersistedERIndices, ERMatcher, Concept
        from jurisynth.main import _load_community_guidance
        from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever
        from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
        from jurisynth.retrieval_mech.config import GLOBAL_MAX_QUADS_PER_SEED
        from jurisynth.contracts import RetrievalRequest
        from sentence_transformers import SentenceTransformer

        def instrument(cls, name, verbose=True):
            original = getattr(cls, name)
            @functools.wraps(original)
            def measured(self, *positional, **keywords):
                span_started = time.perf_counter()
                label = cls.__name__ + '.' + name
                if verbose:
                    extra = {'concept_count': len(positional[0])} if name == '_match' else {}
                    event('stage_started', stage=label, **extra)
                try:
                    return original(self, *positional, **keywords)
                finally:
                    elapsed = time.perf_counter() - span_started
                    add_time(label, elapsed)
                    if verbose:
                        event('stage_finished', stage=label, seconds=round(elapsed, 3))
            setattr(cls, name, measured)

        for cls, names in [(ERMatcher, ['_match']), (DirectRDFRetriever, ['_retrieve_sync', '_add_bounded_paths', '_add_three_hop_paths', '_select_evidence']), (RetrievalMechanism, ['_search_chunks', '_search_tables'])]:
            for name in names:
                instrument(cls, name)
        instrument(DirectRDFRetriever, '_resolve_chunk', verbose=False)
        event('stage_started', stage='load_global_artifacts')
        artifacts = load_global_artifacts('jurisynth/global_artifacts')
        event('stage_finished', stage='load_global_artifacts')
        indices = PersistedERIndices.load('jurisynth/global_artifacts/community/er_index')
        event('er_indices_loaded', metadata=indices.load_metadata)
        embedder = SentenceTransformer('all-MiniLM-L6-v2', local_files_only=True)
        selector, orientation, descriptors = _load_community_guidance(
            Path('jurisynth/global_artifacts/community/er_index'), indices,
            hierarchy_path='jurisynth/global_artifacts/community/community_hierarchy.json',
            descriptor_path='jurisynth/global_artifacts/community/community_descriptors.json')

        class FixedInterpreter:
            def __init__(self, entities, relations):
                self.entities, self.relations = entities, relations
            async def interpret(self, request):
                return self.entities, self.relations

        query = 'What pre-market and post-market obligations apply to the provider, importer, distributor and hospital deploying an AI medical device?'
        cases = [
            ('small', [Concept('e1', 'medical device'), Concept('e2', 'provider')], [Concept('r1', 'obligations')]),
            ('broader', [Concept('e1', 'medical device', ('AI medical device', 'medical equipment')), Concept('e2', 'provider', ('manufacturer', 'AI provider')), Concept('e3', 'importer'), Concept('e4', 'distributor'), Concept('e5', 'hospital', ('healthcare organisation', 'deployer'))], [Concept('r1', 'obligations', ('requirements', 'duties')), Concept('r2', 'conformity assessment'), Concept('r3', 'post-market monitoring'), Concept('r4', 'serious incident')]),
        ]
        results = []
        async def run_cases():
            nonlocal case
            for case, entities, relations in cases:
                event('case_started', entity_count=len(entities), relation_count=len(relations), term_count=sum(1+len(c.variants) for c in entities+relations))
                mechanism = RetrievalMechanism(embedder,
                    chunk_indices=[artifacts.chunk_index],
                    table_indices=[artifacts.table_index] if artifacts.table_index else [],
                    structured_retriever=DirectRDFRetriever(artifacts.dataset, ERMatcher(indices, embedder), artifacts.resolve_chunk,
                        interpreter=FixedInterpreter(entities, relations), community_selector=selector, max_quads_per_seed=GLOBAL_MAX_QUADS_PER_SEED),
                    community_orientation_builder=orientation, community_descriptors=descriptors,
                    community_summarizer=None, document_metadata=artifacts.document_metadata)
                span_started = time.perf_counter()
                bundle = await mechanism.retrieve_evidence(RetrievalRequest(case, query))
                row = {'case':case, 'seconds':round(time.perf_counter()-span_started,3), 'status':bundle.status,
                    'evidence_count':len(bundle.evidence_items), 'table_count':len(bundle.table_evidence),
                    'rss_gb':round(psutil.Process().memory_info().rss/1024**3,3)}
                results.append(row)
                event('case_finished', **{k:v for k,v in row.items() if k!='case'})
        asyncio.run(run_cases())
        summary = {'api_calls':False, 'results':results, 'stages':stage_totals,
            'caveats':['Hand-authored concepts, not captured v10 outputs.', 'Inclusive stage times overlap; do not sum them.', 'Sequential cases with process-local cache differences.', 'Existing adaptive index selection retained; no production defaults changed.']}
        (args.output/'results.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        event('diagnostic_finished', output=str(args.output/'results.json'))
    except Exception as exc:
        event('diagnostic_failed', error_type=type(exc).__name__, error=str(exc))
        raise
    finally:
        watchdog.cancel()


if __name__ == '__main__':
    main()
