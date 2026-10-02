"""Request-scoped model choice; credentials always stay on the server."""

import threading
from dataclasses import dataclass, field
from flask import has_request_context, request

from ..config import Config

_thread_local = threading.local()
DEEPSEEK_MODEL = 'deepseek-flash'
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'


@dataclass(frozen=True)
class LLMSettings:
    api_key: str | None = field(repr=False)
    base_url: str
    model: str


def get_llm_provider() -> str:
    if has_request_context():
        return request.headers.get('X-MiroFish-Provider', 'default')
    return getattr(_thread_local, 'provider', 'default')


def set_llm_provider(provider: str) -> None:
    get_llm_settings(provider)  # Validate before starting background work.
    _thread_local.provider = provider


def get_llm_settings(provider: str | None = None) -> LLMSettings:
    provider = provider if provider is not None else get_llm_provider()
    if provider == 'default':
        return LLMSettings(Config.LLM_API_KEY, Config.LLM_BASE_URL, Config.LLM_MODEL_NAME)
    if provider == 'deepseek':
        if not Config.DEEPSEEK_API_KEY:
            raise ValueError('Add DEEPSEEK_API_KEY to Codespaces secrets for majdaleid/MiroFish, then restart the backend.')
        return LLMSettings(Config.DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL)
    raise ValueError('Unknown model provider. Choose default or deepseek.')


def simulation_llm_environment(env: dict[str, str]) -> dict[str, str]:
    """Capture the selected provider before launching the simulation process."""
    settings = get_llm_settings()
    env.update(LLM_API_KEY=settings.api_key or '', LLM_BASE_URL=settings.base_url,
               LLM_MODEL_NAME=settings.model)
    if get_llm_provider() == 'deepseek':
        # Both platforms must use the explicit DeepSeek choice, even if an
        # optional acceleration provider is configured for the default setup.
        for name in ('LLM_BOOST_API_KEY', 'LLM_BOOST_BASE_URL', 'LLM_BOOST_MODEL_NAME'):
            env[name] = ''
    return env
