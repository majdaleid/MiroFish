"""Language selection must reach reports and simulation agents independently of input."""
import importlib.util
import json
import re
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from flask import Flask
from app.services.report_agent import ReportAgent, ReportOutline, ReportSection
from app.utils.locale import get_language_instruction, set_locale, t

ROOT = Path(__file__).resolve().parents[2]


def test_arabic_catalog_has_every_translation_and_preserves_placeholders():
    english = json.loads((ROOT / 'locales/en.json').read_text(encoding='utf-8'))
    arabic = json.loads((ROOT / 'locales/ar.json').read_text(encoding='utf-8'))

    def check(a, b):
        if isinstance(a, dict):
            assert set(a) == set(b)
            for key in a:
                check(a[key], b[key])
        elif isinstance(a, list):
            assert len(a) == len(b)
            for x, y in zip(a, b):
                check(x, y)
        else:
            assert sorted(re.findall(r'\{\w+\}', a)) == sorted(re.findall(r'\{\w+\}', b))
            assert not re.search('[\u202a-\u202e\u2066-\u2069]', b)
    check(english, arabic)


def make_agent():
    agent = ReportAgent.__new__(ReportAgent)
    agent.graph_id = 'test_graph'
    agent.simulation_id = 'test_simulation'
    agent.simulation_requirement = 'Analyze demand for a digital calculator in Germany.'
    agent.report_logger = None
    agent.tools = {}
    agent.zep_tools = Mock()
    agent.zep_tools.get_simulation_context.return_value = {}
    agent.llm = Mock()
    return agent


def test_english_input_arabic_report_outline_and_fallback():
    agent = make_agent()
    agent.llm.chat_json.return_value = {'title': 'تقرير الطلب', 'summary': 'تحليل السوق', 'sections': [{'title': 'النتائج'}]}
    app = Flask(__name__)
    with app.test_request_context(headers={'Accept-Language': 'ar'}):
        outline = agent.plan_outline()
        messages = agent.llm.chat_json.call_args.kwargs['messages']
        assert 'Output language: Arabic' in messages[0]['content']
        assert agent.simulation_requirement in messages[1]['content']
        assert outline.title == 'تقرير الطلب'
        agent.llm.chat_json.side_effect = ValueError('provider unavailable')
        fallback = agent.plan_outline()
        assert fallback.title == 'تقرير التوقعات'
        assert all(re.search('[\u0600-\u06ff]', section.title) for section in fallback.sections)


def test_background_report_section_and_chat_keep_arabic(monkeypatch):
    agent = make_agent()
    set_locale('ar')
    try:
        # A section must exercise the normal tool / Final Answer parsing path.
        agent._execute_tool = Mock(return_value='English source evidence')
        agent.llm.chat.side_effect = [
            '<tool_call>{"name":"quick_search","parameters":{"query":"demand"}}</tool_call>',
            '<tool_call>{"name":"panorama_search","parameters":{"query":"market"}}</tool_call>',
            '<tool_call>{"name":"insight_forge","parameters":{"query":"risks"}}</tool_call>',
            'Final Answer: تقرير عربي عن GraphRAG.',
        ]
        outline = ReportOutline(title='تقرير', summary='ملخص', sections=[])
        content = agent._generate_section_react(ReportSection(title='النتائج'), outline, [])
        assert content == 'تقرير عربي عن GraphRAG.'
        assert 'Output language: Arabic' in agent.llm.chat.call_args.kwargs['messages'][0]['content']
        monkeypatch.setattr('app.services.report_agent.ReportManager.get_report_by_simulation', lambda _: None)
        agent.llm.chat.side_effect = None
        agent.llm.chat.return_value = 'الإجابة بالعربية مع API.'
        result = agent.chat('Explain this in English.')
        assert result['response'] == 'الإجابة بالعربية مع API.'
        assert 'Output language: Arabic' in agent.llm.chat.call_args.kwargs['messages'][0]['content']
        assert t('common.ready') == 'جاهز'
    finally:
        set_locale('zh')


def test_oasis_agents_receive_arabic_before_start_without_changing_english(monkeypatch):
    spec = importlib.util.spec_from_file_location('output_language', ROOT / 'backend/scripts/output_language.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    agent = SimpleNamespace(output_language=None)
    graph = SimpleNamespace(get_agents=lambda: [(0, agent)])
    monkeypatch.setenv('MIROFISH_OUTPUT_LOCALE', 'ar')
    module.apply_output_language(graph)
    assert 'Arabic' in agent.output_language
    assert 'JSON keys' in agent.output_language
    agent.output_language = None
    monkeypatch.setenv('MIROFISH_OUTPUT_LOCALE', 'en')
    module.apply_output_language(graph)
    assert agent.output_language is None
