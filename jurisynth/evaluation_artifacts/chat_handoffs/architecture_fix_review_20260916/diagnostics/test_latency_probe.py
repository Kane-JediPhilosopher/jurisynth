import asyncio
from dataclasses import asdict
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from jurisynth.diagnostics.latency_probe import MODES, parse_args, validate_capture, plan_request
from jurisynth.diagnostics.tracing import Recorder, Instrumentation, TimedLock, make_mechanism


def test_instrumentation_restores_partial_install_on_error(tmp_path, monkeypatch):
    recorder = Recorder(tmp_path/'partial_install', 'q003')
    owner = SimpleNamespace(value='original')
    instrumentation = Instrumentation(recorder)
    def fail_install():
        instrumentation.patch(owner, 'value', 'patched')
        raise RuntimeError('synthetic installation failure')
    monkeypatch.setattr(instrumentation, '_install', fail_install)
    try:
        with pytest.raises(RuntimeError, match='installation failure'):
            with instrumentation:
                pytest.fail('Failed installation must not enter the context')
        assert owner.value == 'original'
    finally:
        recorder.close()


def test_timed_lock_preserves_acquisition_error_without_release(tmp_path):
    recorder = Recorder(tmp_path/'lock_failure', 'q003')
    class FailedLock:
        def acquire(self):
            raise RuntimeError('synthetic acquisition failure')
        def release(self):
            pytest.fail('An unacquired lock must not be released')
    try:
        with pytest.raises(RuntimeError, match='acquisition failure'):
            with TimedLock(FailedLock(), recorder):
                pytest.fail('Failed acquisition must not enter the context')
    finally:
        recorder.close()


def test_recorder_separates_api_duration_from_run_clock(tmp_path):
    recorder = Recorder(tmp_path/'clocks', 'q003')
    try:
        event = recorder.record('nim_request_completed', elapsed_seconds=123.0)
        assert event['elapsed_seconds'] == 123.0
        assert 0 <= event['run_elapsed_seconds'] < 123.0
    finally:
        recorder.close()


def example_capture():
    return {'schema_version':1,'capture_kind':'synthetic_test_fixture',
            'request':{'query_id':'q003','leaf_query':'What obligations apply?'},
            'entity_concepts':[{'concept_id':'e1','text':'provider','variants':[]}],
            'relation_concepts':[]}


def test_capture_refuses_live_without_explicit_opt_in(tmp_path):
    with pytest.raises(SystemExit):
        parse_args(['capture','--query-file','missing.txt','--output',str(tmp_path/'capture')])
    assert not (tmp_path/'capture').exists()


@pytest.mark.parametrize('mode', MODES)
def test_replay_modes_are_explicit_and_zero_live_flag(mode):
    args=parse_args(['replay','--capture','capture.json','--mode',mode])
    assert args.command=='replay' and not hasattr(args,'allow_live_nim')


@pytest.mark.parametrize('field,value', [('schema_version',2),('entity_concepts','bad'),('relation_concepts',None)])
def test_invalid_capture_fails_before_artifact_loading(field,value):
    data=example_capture()
    data[field]=value
    with pytest.raises(ValueError):
        validate_capture(data)


def test_variants_preserved_and_invalid_variants_rejected():
    data=example_capture()
    data['entity_concepts'][0]['variants']=['maker','manufacturer']
    assert validate_capture(data)['entity_concepts'][0]['variants']==['maker','manufacturer']
    data['entity_concepts'][0]['variants']=[1]
    with pytest.raises(ValueError):
        validate_capture(data)


def test_no_overwrite_and_every_event_has_correlation(tmp_path):
    directory=tmp_path/'probe'
    recorder=Recorder(directory,'q003')
    with recorder.span('outer'):
        with recorder.span('inner'):
            recorder.record('example')
    recorder.checkpoint('state.json',{'a':1})
    recorder.checkpoint('state.json',{'a':2})
    recorder.close()
    events=[json.loads(x) for x in (directory/'events.jsonl').read_text().splitlines()]
    assert all(x['query_id']=='q003' and x['call_id'] for x in events)
    assert any(x['parent_call_id'] for x in events)
    assert json.loads((directory/'state.json').read_text())=={'a':2}
    assert not list(directory.glob('*.tmp'))
    with pytest.raises(FileExistsError):
        Recorder(directory,'q003')


def test_plan_stops_before_retrieval_preserves_normal_facts_and_dependencies(tmp_path):
    class Model:
        async def complete(self,**kwargs):
            name=kwargs['response_schema']['name']
            responses={
                'request_analysis':{'action':'proceed','route':'complex','contextual_facts':['hospital','health data'],'constraints':{'jurisdiction':'EU','conditional':True},'clarification_question':None},
                'qcompiler_ast':{'ast':{'type':'dependent','left':{'type':'query','query':'Which actors?'},'right':{'type':'query','query':'What obligations apply to the resolved actors?'}}},
            }
            assert name in responses, 'No interpretation/answer/model call allowed in planning-only test'
            return json.dumps(responses[name])
    recorder=Recorder(tmp_path/'plan','q001')
    try:
        request=asyncio.run(plan_request('A hospital uses an AI device. Who and what duties?','q001',Model(),recorder))
        assert request.contextual_facts==['hospital','health data']
        assert request.constraints['jurisdiction']=='EU' and request.constraints['conditional']
        leaves=json.loads((recorder.directory/'planned_leaves.json').read_text())
        assert leaves[1]['dependency_ids']==['q001']
    finally:
        recorder.close()


def fixture_mechanism(recorder,mode):
    from jurisynth.contracts import SourceChunk
    from jurisynth.retrieval_mech.er_matcher import ERMatchResult
    class Store:
        def matching_quads(self,*args,**kwargs):
            return iter([])
        def select_rows(self,*args):
            return iter([])
    class Matcher:
        calls=0
        def match(self,*args,**kwargs):
            self.calls+=1
            return ERMatchResult((),())
    class Interpreter:
        async def interpret(self,request):
            return [],[]
    class ChunkIndex:
        def search(self,*args,**kwargs):
            return [SourceChunk('chunk_1','doc_1','A weak matching excerpt.',0.1)]
    class Selector:
        def select(self,matches):
            return []
        def expand_for_orientation(self,selected):
            return ()
    artifacts=SimpleNamespace(dataset=Store(),resolve_chunk=lambda _:None,
                              chunk_index=ChunkIndex(),table_index=None,image_index=None)
    matcher=Matcher()
    mechanism=make_mechanism(recorder=recorder,mode=mode,embedder=object(),artifacts=artifacts,
        matcher=matcher,interpreter=Interpreter(),selector=Selector(),orientation=None,descriptors={})
    return mechanism,matcher


def test_no_escalation_retains_real_weak_status_and_first_pass_sources(tmp_path):
    from jurisynth.contracts import RetrievalRequest
    recorder=Recorder(tmp_path/'no_escalation','q003')
    try:
        mechanism,matcher=fixture_mechanism(recorder,'no_escalation')
        bundle=asyncio.run(mechanism.retrieve_evidence(RetrievalRequest('q003','What duties?')))
        assert bundle.status=='weak'
        assert matcher.calls==1
        assert bundle.retrieval_metadata['escalation_stages']==['normal']
        assert bundle.evidence_items[0].source_chunks[0].document_id=='doc_1'
    finally:
        recorder.close()


def test_baseline_retains_escalation_and_one_hop_skips_traversal_only(tmp_path,monkeypatch):
    from jurisynth.contracts import RetrievalRequest
    from jurisynth.retrieval_mech.rdf_retriever import DirectRDFRetriever
    calls=[]
    def two(*args):
        calls.append(2)
        return 0
    def three(*args):
        calls.append(3)
        return 0
    monkeypatch.setattr(DirectRDFRetriever,'_add_bounded_paths',two)
    monkeypatch.setattr(DirectRDFRetriever,'_add_three_hop_paths',three)
    for mode in ('baseline','one_hop','no_three_hop'):
        calls.clear()
        recorder=Recorder(tmp_path/mode,'q003')
        try:
            mechanism,matcher=fixture_mechanism(recorder,mode)
            bundle=asyncio.run(mechanism.retrieve_evidence(RetrievalRequest('q003','What duties?')))
            assert bundle.status=='weak' and matcher.calls==2
            assert bundle.retrieval_metadata['escalation_stages']==['normal','broaden_candidates']
            if mode=='baseline':
                assert calls==[2,2,3]
            elif mode=='one_hop':
                assert calls==[]
            else:
                assert calls==[2,2]
        finally:
            recorder.close()


def test_shard_instrumentation_preserves_results_locks_and_global_functions(tmp_path):
    import faiss
    import numpy as np
    from jurisynth.retrieval_mech.er_shards import IndexShard, LazyShardedFlatIndex
    rows=[np.array([[1,0],[0,1]],dtype=np.float32),np.array([[.5,.5]],dtype=np.float32)]
    shards=[]
    offset=0
    for i,vectors in enumerate(rows):
        path=tmp_path/f'shard_{i}.index'
        index=faiss.IndexFlatIP(2)
        index.add(vectors)
        faiss.write_index(index,str(path))
        shards.append(IndexShard(path,offset,len(vectors),path.stat().st_size))
        offset+=len(vectors)
    index=LazyShardedFlatIndex(tuple(shards),2)
    original_read,original_lock=faiss.read_index,index._search_lock
    recorder=Recorder(tmp_path/'traced','q003')
    try:
        with Instrumentation(recorder) as tracing:
            tracing.instrument_index_locks(SimpleNamespace(entity_index=index,relation_index=None))
            scores,ids=index.search(np.array([[1,0]],dtype=np.float32),2)
        assert ids.tolist()==[[0,2]]
        assert np.allclose(scores,[[1,.5]])
        assert faiss.read_index is original_read and index._search_lock is original_lock
    finally:
        recorder.close()
    events=[json.loads(x) for x in (recorder.directory/'events.jsonl').read_text().splitlines()]
    stages={x.get('stage') for x in events}
    assert {'shard_lock_wait','faiss_shard_load','faiss_shard_search'} <= stages


def test_launcher_binds_localhost_and_has_no_query_submission():
    root=Path(__file__).resolve().parents[2]
    script=(root/'RUN_JURISYNTH_UI.ps1').read_text(encoding='utf-8')
    assert "'--host','127.0.0.1'" in script and "'--strictPort'" in script
    assert 'WindowStyle Hidden' in script and 'Stop-OwnedService' in script
    assert '-Method Post' not in script and '-m jurisynth.run_' not in script


def test_capture_checkpoint_preserves_real_interpreter_shape_with_fake_transport(tmp_path,monkeypatch):
    """Fake transport only: this test is NOT a live NIM capture."""
    from jurisynth.agentic_reasoner import llm
    from jurisynth.diagnostics.latency_probe import capture
    config=SimpleNamespace(model='fake_model_no_network',request_timeout_seconds=None)
    monkeypatch.setattr(llm.NIMConfig,'from_environment',classmethod(lambda cls:config))
    class FakeNIM:
        def __init__(self,config,reasoning_log):
            self.log=reasoning_log
        async def complete(self,**kwargs):
            assert kwargs['response_schema']['name']=='retrieval_concepts'
            self.log.record('nim_request_started',call_id='fake_test_call',schema_name='retrieval_concepts',model='fake_model_no_network')
            self.log.record('nim_request_completed',call_id='fake_test_call',elapsed_seconds=.01,prompt_tokens=20,completion_tokens=10,finish_reason='stop')
            return json.dumps({'entity_concepts':[{'concept':'provider','variants':['AI provider']}], 'relation_concepts':[]})
        async def aclose(self):
            pass
    monkeypatch.setattr(llm,'OpenAICompatibleNIM',FakeNIM)
    request=tmp_path/'request.json'
    request.write_text(json.dumps({'query_id':'q003','leaf_query':'What are provider duties?',
        'contextual_facts':['non-EU manufacturer'],'constraints':{'jurisdiction':'EU'}}))
    recorder=Recorder(tmp_path/'capture','q003')
    try:
        asyncio.run(capture(SimpleNamespace(request_file=request),recorder))
        data=validate_capture(json.loads((recorder.directory/'capture.json').read_text()))
        assert data['entity_concepts'][0]['variants']==['AI provider']
        assert data['request']['contextual_facts']==['non-EU manufacturer']
        assert data['interpretation_request_metrics'][0]['prompt_tokens']==20
        assert data['interpretation_logical_calls']==1
    finally:
        recorder.close()


def test_failure_checkpoint_is_not_left_running(tmp_path,monkeypatch):
    import jurisynth.diagnostics.latency_probe as module
    path=tmp_path/'fixture.json'
    path.write_text(json.dumps(example_capture()))
    output=tmp_path/'failed_probe'
    async def fail(*args):
        raise RuntimeError('Synthetic test failure')
    monkeypatch.setattr(module,'replay',fail)
    with pytest.raises(RuntimeError):
        module.main(['replay','--capture',str(path),'--output',str(output),'--maximum-seconds','0'])
    assert json.loads((output/'result.json').read_text())['status']=='failed'
    assert (output/'failure.json').exists()
