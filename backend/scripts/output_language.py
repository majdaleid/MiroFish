"""Apply the requested output language before OASIS agents start acting."""
import json
import os
from pathlib import Path


def apply_output_language(agent_graph):
    locale = os.environ.get('MIROFISH_OUTPUT_LOCALE')
    if locale != 'ar':
        return
    registry = Path(__file__).resolve().parents[2] / 'locales' / 'languages.json'
    instruction = json.loads(registry.read_text(encoding='utf-8'))['ar']['llmInstruction']
    for _, agent in agent_graph.get_agents():
        # CAMEL's public setter appends this instruction and initializes memory.
        # Only call before the simulation starts, so no conversation is lost.
        agent.output_language = f'Arabic. {instruction}'
