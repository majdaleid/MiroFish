import json
import threading
from types import SimpleNamespace

import pytest
from flask import Flask

from app import create_app
from app.config import Config
from app.utils.llm_settings import get_llm_provider, get_llm_settings, set_llm_provider
from app.utils.llm_client import LLMClient
from app.utils.openai_chat_compat import create_chat_completion
from app.services.oasis_profile_generator import OasisProfileGenerator
from app.services.simulation_config_generator import SimulationConfigGenerator
from app.services import simulation_runner as runner_module
from app.services.simulation_runner import SimulationRunner


@pytest.fixture
def credentials(monkeypatch):
    monkeypatch.setattr(Config, 'LLM_API_KEY', 'default-test-key')
    monkeypatch.setattr(Config, 'LLM_BASE_URL', 'https://default.example/v1')
    monkeypatch.setattr(Config, 'LLM_MODEL_NAME', 'gpt-4o-mini')
    monkeypatch.setattr(Config, 'DEEPSEEK_API_KEY', 'deepseek-test-key')
    monkeypatch.setattr(Config, 'ZEP_API_KEY', None)
    for module in ('app.utils.llm_client', 'app.services.oasis_profile_generator', 'app.services.simulation_config_generator'):
        monkeypatch.setattr(module + '.OpenAI', lambda **kwargs: SimpleNamespace(**kwargs))
    set_llm_provider('default')
    yield
    set_llm_provider('default')


@pytest.mark.parametrize('provider,expected_model,expected_key', [
    ('default', 'gpt-4o-mini', 'default-test-key'),
    ('deepseek', 'deepseek-flash', 'deepseek-test-key'),
])
def test_all_generators_use_selected_provider_without_mutating_default(credentials, provider, expected_model, expected_key):
    with Flask(__name__).test_request_context(headers={'X-MiroFish-Provider': provider}):
        clients = [LLMClient(), OasisProfileGenerator(), SimulationConfigGenerator()]
    for client in clients:
        assert client.api_key == expected_key
        assert getattr(client, 'model', getattr(client, 'model_name', None)) == expected_model
    assert Config.LLM_MODEL_NAME == 'gpt-4o-mini'
    assert get_llm_settings().api_key == 'default-test-key'


def test_background_job_keeps_captured_provider(credentials):
    with Flask(__name__).test_request_context(headers={'X-MiroFish-Provider': 'deepseek'}):
        captured = get_llm_provider()
    ready, proceed = threading.Event(), threading.Event()
    models = []
    def background():
        set_llm_provider(captured)
        ready.set()
        proceed.wait(timeout=5)
        models.append(LLMClient().model)
    worker = threading.Thread(target=background)
    worker.start()
    assert ready.wait(timeout=5)
    with Flask(__name__).test_request_context(headers={'X-MiroFish-Provider': 'default'}):
        assert LLMClient().model == 'gpt-4o-mini'
    proceed.set()
    worker.join(timeout=5)
    assert models == ['deepseek-flash']


def test_settings_api_does_not_expose_credentials(credentials, monkeypatch):
    monkeypatch.setattr(SimulationRunner, 'register_cleanup', classmethod(lambda _cls: None))
    client = create_app().test_client()
    response = client.get('/api/llm/providers')
    assert response.status_code == 200
    assert response.json['data']['deepseek_configured'] is True
    assert 'test-key' not in response.get_data(as_text=True)
    assert 'test-key' not in repr(get_llm_settings())
    assert client.get('/api/simulation/list', headers={'X-MiroFish-Provider': 'unknown'}).status_code == 400
    monkeypatch.setattr(Config, 'DEEPSEEK_API_KEY', None)
    missing = client.get('/api/simulation/list', headers={'X-MiroFish-Provider': 'deepseek'})
    assert missing.status_code == 400
    assert 'DEEPSEEK_API_KEY' in missing.json['error']
    assert client.get('/api/llm/providers', headers={'X-MiroFish-Provider': 'deepseek'}).status_code == 200


def test_flash_requests_disable_thinking_for_existing_tool_protocol():
    calls = []
    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: calls.append(kwargs))))
    create_chat_completion(client, model='deepseek-flash', messages=[], temperature=.7, max_tokens=100)
    assert calls[0]['extra_body'] == {'thinking': {'type': 'disabled'}}


@pytest.mark.parametrize('provider,expected_model', [('default', 'gpt-4o-mini'), ('deepseek', 'deepseek-flash')])
def test_simulation_process_receives_selected_model(credentials, monkeypatch, tmp_path, provider, expected_model):
    simulation_id = 'sim-provider'
    sim_dir, scripts_dir = tmp_path / 'runs' / simulation_id, tmp_path / 'scripts'
    sim_dir.mkdir(parents=True)
    scripts_dir.mkdir()
    (sim_dir / 'simulation_config.json').write_text(json.dumps({'time_config': {'total_simulation_hours': 1, 'minutes_per_round': 60}}))
    (scripts_dir / 'run_twitter_simulation.py').write_text('pass\n')
    monkeypatch.setattr(SimulationRunner, 'RUN_STATE_DIR', str(tmp_path / 'runs'))
    monkeypatch.setattr(SimulationRunner, 'SCRIPTS_DIR', str(scripts_dir))
    for name in ('_run_states', '_processes', '_graph_memory_enabled', '_action_queues', '_monitor_threads', '_stdout_files', '_stderr_files'):
        monkeypatch.setattr(SimulationRunner, name, {})
    captured = []
    def spawn(*_args, **kwargs):
        captured.append(kwargs['env'])
        return SimpleNamespace(pid=123, poll=lambda: None)
    monkeypatch.setattr(runner_module.subprocess, 'Popen', spawn)
    monkeypatch.setattr(runner_module.threading, 'Thread', lambda **_kwargs: SimpleNamespace(start=lambda: None))
    monkeypatch.setenv('LLM_BOOST_API_KEY', 'boost-test-key')
    with Flask(__name__).test_request_context(headers={'X-MiroFish-Provider': provider}):
        SimulationRunner.start_simulation(simulation_id, platform='twitter')
    try:
        assert captured[0]['LLM_MODEL_NAME'] == expected_model
        assert captured[0]['LLM_BOOST_API_KEY'] == ('' if provider == 'deepseek' else 'boost-test-key')
        assert captured[0]['LLM_API_KEY'] == ('deepseek-test-key' if provider == 'deepseek' else 'default-test-key')
    finally:
        for handle in SimulationRunner._stdout_files.values():
            handle.close()
