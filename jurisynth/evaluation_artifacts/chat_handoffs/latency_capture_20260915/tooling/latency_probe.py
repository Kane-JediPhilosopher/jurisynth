"""Explicitly authorized live interpretation capture, then zero-NIM local replay."""
from __future__ import annotations

import argparse
import asyncio
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import threading
import time
from uuid import uuid4

from jurisynth.diagnostics.tracing import Recorder, TimedEmbedder, Instrumentation, make_mechanism

MODES = ('baseline', 'no_three_hop', 'no_escalation', 'one_hop', 'structured_only',
         'auxiliary_only', 'no_community', 'cold', 'warm')


def validate_capture(data):
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ValueError('Expected a schema-version-1 diagnostic capture.')
    request = data.get('request')
    if not isinstance(request, dict) or not isinstance(request.get('query_id'), str) or not request['query_id'].strip():
        raise ValueError('Capture needs a nonempty request.query_id.')
    if not isinstance(request.get('leaf_query'), str) or not request['leaf_query'].strip():
        raise ValueError('Capture needs a nonempty request.leaf_query.')
    for name in ('entity_concepts', 'relation_concepts'):
        values = data.get(name)
        if not isinstance(values, list):
            raise ValueError(f'Capture needs {name}.')
        for value in values:
            if not isinstance(value, dict) or not isinstance(value.get('text'), str) or not value['text'].strip():
                raise ValueError('Each concept needs nonempty text.')
            if not isinstance(value.get('concept_id'), str) or not value['concept_id'].strip():
                raise ValueError('Each concept needs a concept_id.')
            if not isinstance(value.get('variants', []), list) or not all(isinstance(x, str) for x in value.get('variants', [])):
                raise ValueError('Concept variants must be strings.')
    return data


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    capture = sub.add_parser('capture', help='NIM calls require --allow-live-nim AND owner approval.')
    source = capture.add_mutually_exclusive_group(required=True)
    source.add_argument('--query-file', type=Path, help='Run current intake/router/compiler/dependency planning, checkpoint before interpretation.')
    source.add_argument('--request-file', type=Path, help='Reuse an explicitly saved, complete materialized RetrievalRequest; no planning calls.')
    capture.add_argument('--leaf-id', default='q003')
    capture.add_argument('--output', type=Path, required=True)
    capture.add_argument('--allow-live-nim', action='store_true')
    replay = sub.add_parser('replay', help='Local-only: no NIM, vision expansion, or LLM merge calls.')
    replay.add_argument('--capture', type=Path, required=True)
    replay.add_argument('--mode', choices=MODES, default='baseline')
    replay.add_argument('--output', type=Path)
    replay.add_argument('--repeat', type=int, default=1)
    replay.add_argument('--artifact-root', type=Path, default=Path('jurisynth/global_artifacts'))
    replay.add_argument('--community-dir', type=Path, default=Path('jurisynth/global_artifacts/community'))
    replay.add_argument('--minimum-available-gb', type=float, default=5.5)
    replay.add_argument('--index-mode', choices=('auto','memory','mmap','sharded'), default='auto')
    replay.add_argument('--shard-count', type=int, choices=(2,3,4), help='Pin a diagnostic sharded layout across comparisons; requires --index-mode sharded.')
    replay.add_argument('--maximum-seconds', type=float, default=300,
                        help='Standalone local diagnostic safety bound only; 0 disables it. Not an API/production timeout.')
    args = parser.parse_args(argv)
    if args.command == 'capture' and not args.allow_live_nim:
        parser.error('Capture is live. Obtain owner approval and explicitly pass --allow-live-nim; nothing was started.')
    if args.command == 'replay' and (args.repeat < 1 or args.maximum_seconds < 0 or args.minimum_available_gb < 0):
        parser.error('Use repeat>=1 and nonnegative safety limits.')
    if args.command == 'replay' and args.shard_count is not None and args.index_mode != 'sharded':
        parser.error('--shard-count requires --index-mode sharded; adaptive production policy is otherwise retained.')
    return args


async def plan_request(query, leaf_id, model, recorder):
    """Reuse the normal workflow itself; stop before any leaf execution/load."""
    from jurisynth.agentic_reasoner.workflow import AgenticWorkflow, NIMTaskAnalyzer
    from jurisynth.agentic_reasoner.intake import NIMConversationIntake
    from jurisynth.agentic_reasoner.qcompiler_translator import QCompilerTranslator
    from jurisynth.agentic_reasoner.dependency_planner import SemanticDependencyPlanner
    from jurisynth.contracts import RetrievalRequest

    class Planned(Exception):
        pass
    class StopAfterPlan:
        async def execute_leaves(self, leaves):
            self.leaves = leaves
            recorder.checkpoint('planned_leaves.json', [asdict(x) for x in leaves])
            raise Planned()
    stop = StopAfterPlan()
    workflow = AgenticWorkflow(analyzer=NIMTaskAnalyzer(model), reasoner=stop,
        translator=QCompilerTranslator(model), dependency_planner=SemanticDependencyPlanner(model),
        intake=NIMConversationIntake(model), reasoning_log=recorder)
    try:
        result = await workflow.run(query)
    except Planned:
        result = None
    if result is not None:
        recorder.checkpoint('clarification.json', result.clarification)
        raise ValueError('Normal intake requested clarification; no interpretation was attempted.')
    leaf = next((x for x in stop.leaves if x.query_id == leaf_id), None)
    if leaf is None:
        raise ValueError(f'Planning did not produce {leaf_id}; see planned_leaves.json.')
    if '{' in leaf.query or '}' in leaf.query:
        raise ValueError('Leaf contains unresolved dependency placeholders. Supply a saved materialized --request-file; do not invent upstream answers.')
    return RetrievalRequest(leaf.query_id, leaf.query, contextual_facts=list(leaf.contextual_facts), constraints=leaf.constraints)


async def capture(args, recorder):
    # No global graph/model/index loads are needed to capture interpretation.
    from jurisynth.agentic_reasoner.llm import NIMConfig, OpenAICompatibleNIM
    from jurisynth.retrieval_mech.query_interpreter import NIMQueryInterpreter
    from jurisynth.contracts import RetrievalRequest
    config = NIMConfig.from_environment()
    recorder.record('capture_model_config', model=config.model,
                    request_timeout_seconds=config.request_timeout_seconds,
                    output_limit='provider_default', production_settings_unchanged=True)
    delegate = OpenAICompatibleNIM(config, reasoning_log=recorder)

    class CaptureModel:
        async def complete(self, **kwargs):
            schema = kwargs.get('response_schema') or {}
            stage = schema.get('name', 'unstructured_model_call')
            with recorder.span('nim_stage:' + stage):
                response = await delegate.complete(**kwargs)
                if stage == 'retrieval_concepts':
                    recorder.checkpoint('interpretation_raw_' + uuid4().hex + '.json', {'response': response})
                return response
    model = CaptureModel()
    try:
        if args.request_file is not None:
            source = json.loads(args.request_file.read_text(encoding='utf-8-sig'))
            payload = source.get('request', source)
            request = RetrievalRequest(**payload)
            recorder.query_id = request.query_id
            provenance = {'kind': 'saved_materialized_request', 'path': str(args.request_file)}
        else:
            query = args.query_file.read_text(encoding='utf-8-sig')
            recorder.checkpoint('original_query.json', {'query': query})
            with recorder.span('normal_planning_until_leaf'):
                request = await plan_request(query, args.leaf_id, model, recorder)
            provenance = {'kind': 'normal_current_planning', 'path': str(args.query_file),
                          'dependency_answers_generated': False}
        recorder.checkpoint('request.json', asdict(request))
        started = time.perf_counter()
        with recorder.span('query_interpretation'):
            entities, relations = await NIMQueryInterpreter(model).interpret(request)
        events = recorder.api_events
        concept_starts = {x['call_id'] for x in events if x['event']=='nim_request_started' and x.get('schema_name')=='retrieval_concepts'}
        metrics = [x for x in events if x['call_id'] in concept_starts and x['event'] in {'nim_request_completed', 'nim_retry_scheduled', 'nim_request_failed'}]
        data = {'schema_version':1, 'capture_kind':'live_nim', 'model':config.model,
                'request':asdict(request), 'provenance':provenance,
                'entity_concepts':[{**asdict(x),'variants':list(x.variants)} for x in entities],
                'relation_concepts':[{**asdict(x),'variants':list(x.variants)} for x in relations],
                'interpretation_seconds':round(time.perf_counter()-started,6), 'interpretation_request_metrics':metrics,
                'interpretation_logical_calls':len(concept_starts),
                'note':'One logical interpreter invocation; normal repair/retry behavior may issue multiple HTTP requests. No answering/retrieval executed.'}
        validate_capture(data)
        recorder.checkpoint('capture.json', data)
        recorder.checkpoint('result.json', {'status':'captured', 'query_id':request.query_id, 'answer_generation':False})
        print(json.dumps({'status':'captured','capture':str(recorder.directory/'capture.json')},indent=2))
    finally:
        await delegate.aclose()


async def replay(args, recorder, data):
    import psutil
    available = psutil.virtual_memory().available / 1024**3
    recorder.record('ram_preflight', available_gb=available, minimum_available_gb=args.minimum_available_gb)
    if available < args.minimum_available_gb:
        raise RuntimeError('Insufficient free RAM for this diagnostic; no global artifacts loaded.')
    # Models are cache-only; do not create NIM/vision clients in replay.
    from jurisynth.retrieval_mech.global_artifacts import load_global_artifacts
    from jurisynth.retrieval_mech.er_matcher import PersistedERIndices, ERMatcher, Concept
    from jurisynth.main import _load_community_guidance
    from jurisynth.contracts import RetrievalRequest
    from sentence_transformers import SentenceTransformer
    request = RetrievalRequest(**data['request'])
    entities = [Concept(x['concept_id'], x['text'], tuple(x.get('variants',[]))) for x in data['entity_concepts']]
    relations = [Concept(x['concept_id'], x['text'], tuple(x.get('variants',[]))) for x in data['relation_concepts']]
    class ReplayInterpreter:
        async def interpret(self, incoming):
            recorder.record('captured_interpretation_reused', escalation=incoming.retrieval_config.get('escalation_stage'), api_calls=0)
            return entities, relations
    mode = 'baseline' if args.mode in {'cold','warm'} else args.mode
    with Instrumentation(recorder) as instrumentation:
        with recorder.span('global_artifact_load'):
            artifacts = load_global_artifacts(args.artifact_root)
        with recorder.span('er_index_load'):
            previous_shards = os.environ.get('JURISYNTH_ER_SHARD_COUNT')
            try:
                if args.shard_count is not None:
                    os.environ['JURISYNTH_ER_SHARD_COUNT'] = str(args.shard_count)
                indices = PersistedERIndices.load(args.community_dir/'er_index', index_mode=args.index_mode)
            finally:
                if previous_shards is None:
                    os.environ.pop('JURISYNTH_ER_SHARD_COUNT', None)
                else:
                    os.environ['JURISYNTH_ER_SHARD_COUNT'] = previous_shards
            instrumentation.instrument_index_locks(indices)
            recorder.record('er_load_metadata', metadata=indices.load_metadata)
        with recorder.span('embedding_model_load'):
            embedder = TimedEmbedder(SentenceTransformer('all-MiniLM-L6-v2',local_files_only=True),recorder)
        with recorder.span('community_artifact_load'):
            selector, orientation, descriptors = _load_community_guidance(args.community_dir/'er_index',indices,
                hierarchy_path=args.community_dir/'community_hierarchy.json', descriptor_path=args.community_dir/'community_descriptors.json')
        mechanism = make_mechanism(recorder=recorder, mode=mode, embedder=embedder, artifacts=artifacts,
            matcher=ERMatcher(indices,embedder), interpreter=ReplayInterpreter(),selector=selector,orientation=orientation,descriptors=descriptors)
        recorder.checkpoint('configuration.json', {'request':asdict(request), 'entity_concepts':data['entity_concepts'],
            'relation_concepts':data['relation_concepts'], 'er_load_metadata':indices.load_metadata,
            'settings':asdict(mechanism.settings), 'max_quads_per_seed':getattr(mechanism.structured_retriever,'max_quads_per_seed',None),
            'mode':args.mode,'api_calls':0,'provider_operations_suppressed':True})
        results=[]
        for index in range(max(args.repeat,2 if args.mode=='warm' else 1)):
            recorder.record('replay_iteration_started', iteration=index, requested_mode=args.mode, local_mode=mode)
            started=time.perf_counter()
            bundle=await mechanism.retrieve_evidence(request)
            payload=asdict(bundle)
            recorder.checkpoint(f'bundle_{index:02d}.json',payload)
            row={'iteration':index,'seconds':round(time.perf_counter()-started,6),'status':bundle.status,
                 'evidence_ids':[x.evidence_id for x in bundle.evidence_items],
                 'sources':sorted({(s.document_id,s.chunk_id) for x in bundle.evidence_items for s in x.source_chunks}),
                 'tables':[{'document_id':x.document_id,'table_id':x.table_id} for x in bundle.table_evidence],
                 'image_ids':[x.image_id for x in bundle.image_evidence],
                 'metadata':bundle.retrieval_metadata,'rss_gb':psutil.Process().memory_info().rss/1024**3}
            results.append(row)
            recorder.checkpoint('result.json', {'status':'running','api_calls':0,'capture_sha256':hashlib.sha256(args.capture.read_bytes()).hexdigest(),
                'mode':args.mode,'iterations':results,'quality_adjudicated':False,
                'suppressed_provider_operations':['LLM community merge','vision expansion'],
                'caveat':'Local baseline only. Conditional broadening remains except no_escalation. cold means process-first, not OS cache eviction.'})
            recorder.record('replay_iteration_completed', iteration=index, seconds=row['seconds'],status=row['status'])
        result=json.loads((recorder.directory/'result.json').read_text(encoding='utf-8'))
        result['status']='finished'
        recorder.checkpoint('result.json',result)
        print(json.dumps({'status':'finished','mode':args.mode,'iterations':[{'seconds':x['seconds'],'status':x['status']} for x in results],
                          'output':str(recorder.directory/'result.json')},indent=2))


def main(argv=None):
    args=parse_args(argv)
    data=validate_capture(json.loads(args.capture.read_text(encoding='utf-8-sig'))) if args.command=='replay' else None
    query_id=data['request']['query_id'] if data else args.leaf_id
    if args.command=='replay' and args.output is None:
        stamp=datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        args.output=args.capture.parent/f'replay_{args.mode}_{stamp}_{uuid4().hex[:6]}'
    recorder=Recorder(args.output,query_id)
    recorder.checkpoint('result.json',{'status':'running','command':args.command,'query_id':query_id})
    watchdog=None
    if args.command=='replay' and args.maximum_seconds:
        def stop():
            recorder.record('diagnostic_deadline', maximum_seconds=args.maximum_seconds)
            recorder.checkpoint('deadline.json',{'status':'diagnostic_deadline','partial_evidence':'See events.jsonl and any completed bundle files; result.json may be a partial checkpoint.'})
            current=json.loads((recorder.directory/'result.json').read_text(encoding='utf-8'))
            recorder.checkpoint('result.json',{**current,'status':'diagnostic_deadline'})
            os._exit(124)
        watchdog=threading.Timer(args.maximum_seconds,stop)
        watchdog.daemon=True
        watchdog.start()
    try:
        recorder.record('probe_started',command=args.command,mode=getattr(args,'mode',None),live_nim_allowed=args.command=='capture')
        asyncio.run(capture(args,recorder) if args.command=='capture' else replay(args,recorder,data))
    except BaseException as exc:
        recorder.record('probe_failed',error_type=type(exc).__name__)
        recorder.checkpoint('failure.json',{'status':'failed','error_type':type(exc).__name__})
        current=json.loads((recorder.directory/'result.json').read_text(encoding='utf-8'))
        recorder.checkpoint('result.json',{**current,'status':'interrupted' if isinstance(exc,KeyboardInterrupt) else 'failed','error_type':type(exc).__name__})
        raise
    finally:
        if watchdog:
            watchdog.cancel()
        recorder.close()


if __name__=='__main__':
    main()
