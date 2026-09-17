"""Process-local instrumentation, restored on exit; production source stays unchanged."""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import inspect
import json
from pathlib import Path
import threading
import time
from uuid import uuid4

_span_id = ContextVar('jurisynth_diagnostic_span', default=None)
_in_shard_search = ContextVar('jurisynth_diagnostic_shard_search', default=False)


class Recorder:
    def __init__(self, directory: Path, query_id: str):
        self.directory, self.query_id = directory, query_id
        directory.mkdir(parents=True, exist_ok=False)
        self.handle = (directory / 'events.jsonl').open('x', encoding='utf-8')
        self.lock = threading.RLock()
        self.started = time.perf_counter()
        self.api_events = []

    def record(self, event: str, **payload):
        run_elapsed = round(time.perf_counter() - self.started, 6)
        item = {'event': event, 'query_id': self.query_id,
                'call_id': payload.pop('call_id', None) or _span_id.get() or uuid4().hex,
                'parent_call_id': _span_id.get(),
                'elapsed_seconds': run_elapsed, **payload,
                'run_elapsed_seconds': run_elapsed}
        with self.lock:
            self.handle.write(json.dumps(item, ensure_ascii=False, default=str) + '\n')
            self.handle.flush()
            if event.startswith('nim_'):
                self.api_events.append(item)
        return item

    def checkpoint(self, filename, value):
        """Replace only this newly owned run's checkpoint, atomically."""
        with self.lock:
            target = self.directory / filename
            temporary = target.with_name(target.name + '.' + uuid4().hex + '.tmp')
            temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')
            temporary.replace(target)

    @contextmanager
    def span(self, stage, **metadata):
        span = uuid4().hex
        previous = _span_id.get()
        token = _span_id.set(span)
        started = time.perf_counter()
        self.record('stage_started', stage=stage, call_id=span, parent_call_id=previous, **metadata)
        try:
            yield span
        except BaseException as exc:
            self.record('stage_error', stage=stage, call_id=span, error_type=type(exc).__name__)
            raise
        finally:
            self.record('stage_finished', stage=stage, call_id=span,
                        seconds=round(time.perf_counter()-started, 6))
            _span_id.reset(token)

    def close(self):
        with self.lock:
            self.handle.close()


class TimedEmbedder:
    def __init__(self, delegate, recorder):
        self.delegate, self.recorder = delegate, recorder

    def encode(self, texts, **kwargs):
        with self.recorder.span('embedding', text_count=len(texts)):
            return self.delegate.encode(texts, **kwargs)

    def __getattr__(self, name):
        return getattr(self.delegate, name)


class TimedLock:
    def __init__(self, delegate, recorder):
        self.delegate, self.recorder = delegate, recorder

    def __enter__(self):
        with self.recorder.span('shard_lock_wait'):
            self.delegate.acquire()
        return self

    def __exit__(self, *args):
        self.delegate.release()


class TimedFlatIndex:
    """Only returned inside an already-selected sharded search, not loaders/type checks."""
    def __init__(self, delegate, recorder, path):
        self.delegate, self.recorder, self.path = delegate, recorder, str(path)

    def search(self, vectors, top_k):
        with self.recorder.span('faiss_shard_search', path=self.path, vector_count=len(vectors), top_k=top_k):
            return self.delegate.search(vectors, top_k)

    def __getattr__(self, name):
        return getattr(self.delegate, name)


class Instrumentation:
    def __init__(self, recorder):
        self.recorder, self.restore = recorder, []

    def patch(self, owner, name, value):
        original = inspect.getattr_static(owner, name)
        self.restore.append((owner, name, original))
        setattr(owner, name, value)

    def method(self, owner, name, stage, *, static=False):
        original = getattr(owner, name)
        @wraps(original)
        def measured(*args, **kwargs):
            with self.recorder.span(stage):
                return original(*args, **kwargs)
        self.patch(owner, name, staticmethod(measured) if static else measured)

    def __enter__(self):
        try:
            return self._install()
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def _install(self):
        from jurisynth.retrieval_mech.er_matcher import ERMatcher
        from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever
        from jurisynth.retrieval_mech.community_selector import CommunitySelector
        from jurisynth.retrieval_mech.community_hierarchy import CommunityOrientationBuilder
        from jurisynth.retrieval_mech.er_shards import LazyShardedFlatIndex
        from jurisynth.retrieval_mech import mechanism, er_shards
        for owner, name, stage in [
            (ERMatcher, 'match', 'er_matcher'),
            (CommunitySelector, 'select', 'community_selection'),
            (CommunitySelector, 'expand_for_orientation', 'community_region_expansion'),
            (CommunityOrientationBuilder, 'build', 'orientation_descriptor_build'),
            (DirectRDFRetriever, '_retrieve_sync', 'structured_pass'),
            (DirectRDFRetriever, '_resolve_chunk', 'chunk_resolution'),
            (DirectRDFRetriever, '_add_bounded_paths', 'two_hop'),
            (DirectRDFRetriever, '_add_three_hop_paths', 'three_hop'),
            (DirectRDFRetriever, '_compare_direct_sparql', 'direct_sparql_comparison'),
            (DirectRDFRetriever, '_select_evidence', 'evidence_selection'),
        ]:
            self.method(owner, name, stage)
        self.method(ERMatcher, '_exact_label_matches', 'exact_label_lookup', static=True)
        for name in ('_merge_evidence_items', '_attach_coherence', '_chunk_evidence_items'):
            self.method(mechanism, name, 'evidence_normalization:' + name)

        original_quads = DirectRDFRetriever._matching_quads
        def quads(retriever, entities, relations):
            count, active = 0, 0.0
            with self.recorder.span('quad_enumeration', entity_seed_count=len(entities), relation_seed_count=len(relations)):
                iterator = iter(original_quads(retriever, entities, relations))
                try:
                    while True:
                        started = time.perf_counter()
                        try:
                            row = next(iterator)
                        except StopIteration:
                            active += time.perf_counter() - started
                            break
                        active += time.perf_counter() - started
                        count += 1
                        yield row
                finally:
                    if hasattr(iterator, 'close'):
                        iterator.close()
                    self.recorder.record('quad_enumeration_work', rows=count, active_seconds=round(active, 6))
        self.patch(DirectRDFRetriever, '_matching_quads', quads)

        original_search = LazyShardedFlatIndex.search
        def search(index, vectors, top_k):
            token = _in_shard_search.set(True)
            try:
                with self.recorder.span('sharded_index_total', vector_count=len(vectors), top_k=top_k):
                    return original_search(index, vectors, top_k)
            finally:
                _in_shard_search.reset(token)
        self.patch(LazyShardedFlatIndex, 'search', search)
        if er_shards.faiss is not None:
            original_read = er_shards.faiss.read_index
            def read(path, *args):
                stage = 'faiss_shard_load' if _in_shard_search.get() else 'faiss_index_load'
                with self.recorder.span(stage, path=str(path)):
                    index = original_read(path, *args)
                return TimedFlatIndex(index, self.recorder, path) if _in_shard_search.get() else index
            self.patch(er_shards.faiss, 'read_index', read)
        return self

    def instrument_index_locks(self, indices):
        for kind in ('entity_index', 'relation_index'):
            index = getattr(indices, kind)
            if hasattr(index, '_search_lock'):
                self.patch(index, '_search_lock', TimedLock(index._search_lock, self.recorder))
            else:
                self.recorder.record('shard_spans_not_applicable', index_kind=kind, index_type=type(index).__name__)

    def __exit__(self, *args):
        for owner, name, original in reversed(self.restore):
            setattr(owner, name, original)


def make_mechanism(*, recorder, mode, embedder, artifacts, matcher, interpreter,
                   selector, orientation, descriptors):
    """All policy overrides are confined to this diagnostic object/process."""
    import asyncio
    from jurisynth.retrieval_mech.mechanism import RetrievalMechanism
    from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever
    from jurisynth.retrieval_mech.config import GLOBAL_MAX_QUADS_PER_SEED

    class NoCommunity:
        def select(self, matches):
            recorder.record('community_selection_skipped', reason='diagnostic_no_community')
            return []
        def expand_for_orientation(self, selected):
            return ()

    class SuppressedLLMMerge:
        async def summarize(self, community_id, inputs):
            recorder.record('llm_community_merge_skipped', reason='zero_api_replay', input_count=len(inputs))
            return None

    class DiagnosticRDF(DirectRDFRetriever):
        def _add_bounded_paths(self, *args):
            if mode == 'one_hop':
                recorder.record('traversal_skipped', hops=2, reason='diagnostic_one_hop')
                return 0
            return super()._add_bounded_paths(*args)
        def _add_three_hop_paths(self, *args):
            if mode in {'one_hop', 'no_three_hop'}:
                recorder.record('traversal_skipped', hops=3, reason='diagnostic_' + mode)
                return 0
            return super()._add_three_hop_paths(*args)

    class DiagnosticMechanism(RetrievalMechanism):
        _actual_status = None
        async def _run_operation(self, operation):
            frame = getattr(operation, 'cr_frame', None)
            function = frame.f_locals.get('func') if frame is not None else None
            label = getattr(function, '__name__', None) or getattr(getattr(operation, 'cr_code', None), 'co_name', 'operation')
            acquired = False
            try:
                with recorder.span('operation_semaphore_wait', operation=label):
                    await self._operation_semaphore.acquire()
                    acquired = True
                with recorder.span('operation', operation=label):
                    if self.settings.operation_timeout_seconds is None:
                        return await operation
                    return await asyncio.wait_for(operation, timeout=self.settings.operation_timeout_seconds)
            finally:
                if acquired:
                    self._operation_semaphore.release()
                elif hasattr(operation, 'close'):
                    operation.close()
        def _search_chunks(self, *args):
            with recorder.span('chunk_search'):
                return super()._search_chunks(*args)
        def _search_tables(self, *args):
            with recorder.span('table_search'):
                return super()._search_tables(*args)
        def _search_images(self, *args):
            with recorder.span('image_search'):
                return super()._search_images(*args)
        async def _search_structured(self, request):
            escalation = request.retrieval_config.get('escalation_stage') == 'broaden_candidates'
            with recorder.span('escalation_total' if escalation else 'structured_retrieval', escalation=escalation):
                if escalation:
                    recorder.record('escalation_started', reason='weak_or_empty_first_pass')
                return await super()._search_structured(request)
        def _status_for(self, *args):
            with recorder.span('weak_evidence_status_decision'):
                actual = super()._status_for(*args)
                recorder.record('status_decided', status=actual)
                self._actual_status = actual
                if mode == 'no_escalation' and actual in {'weak', 'empty'}:
                    recorder.record('escalation_skipped', reason='diagnostic_no_escalation', actual_status=actual)
                    # Parent checks this value solely to choose fallback. Restore
                    # actual status in the returned bundle below, never call it success.
                    return 'success'
                return actual
        async def _community_orientation(self, metadata):
            with recorder.span('community_orientation'):
                result = await super()._community_orientation(metadata)
                provenance = result[1].get('community_orientation', {})
                count = len(provenance.get('contributing_communities', []))
                distance = provenance.get('average_tree_distance', 0.0)
                trigger = ('community_count' if count >= self.community_summary_min_communities else
                           'tree_dispersion' if distance >= self.community_summary_min_average_distance else None)
                warning = result[1].get('community_summary_warning')
                reason = ('no_orientation' if not provenance else 'threshold_not_met' if trigger is None else
                          'descriptors_unavailable' if not descriptors else 'insufficient_descriptors' if warning and 'sufficient' in warning else
                          'zero_api_replay')
                recorder.record('community_summary_decision', trigger=trigger, skip_reason=reason,
                                input_community_count=count, average_tree_distance=distance)
                return result
        async def retrieve_evidence(self, request):
            with recorder.span('retrieve_evidence_total'):
                bundle = await super().retrieve_evidence(request)
                if mode == 'no_escalation' and self._actual_status is not None:
                    bundle.status = self._actual_status
                return bundle

    structured = None if mode == 'auxiliary_only' else DiagnosticRDF(
        artifacts.dataset, matcher, artifacts.resolve_chunk, interpreter=interpreter,
        community_selector=NoCommunity() if mode == 'no_community' else selector,
        max_quads_per_seed=GLOBAL_MAX_QUADS_PER_SEED)
    auxiliary = mode != 'structured_only'
    return DiagnosticMechanism(embedder,
        chunk_indices=[artifacts.chunk_index] if auxiliary else [],
        table_indices=[artifacts.table_index] if auxiliary and artifacts.table_index is not None else [],
        image_indices=[artifacts.image_index] if auxiliary and artifacts.image_index is not None else [],
        image_expander=None, structured_retriever=structured,
        community_orientation_builder=orientation if mode not in {'no_community', 'auxiliary_only'} else None,
        community_descriptors=descriptors,
        community_summarizer=SuppressedLLMMerge() if descriptors else None,
        document_metadata=artifacts.document_metadata)
