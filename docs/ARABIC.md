# Arabic in this fork

Choose **العربية** in the language selector before creating a simulation or generating a report. The interface and new generated prose use Arabic, even with English source files or an English prompt. The selection persists after a page reload.

Arabic pages use RTL. Inputs use automatic direction so an English prompt stays LTR. English technical names remain English; generated report/chat text isolates Latin fragments, and code stays LTR. JSON keys, enum values and tool protocol markers remain unchanged.

Existing reports and prepared personas are preserved in their original language. Start a new simulation in Arabic for a fully Arabic run. Changing language does not translate previously saved content.

## Codespaces

Create a Codespace from `majdaleid/MiroFish` (Python 3.12 is selected by the launcher). Add `LLM_API_KEY` and `ZEP_API_KEY` as GitHub Codespaces secrets with access to this fork. Optional `LLM_BASE_URL` and `LLM_MODEL_NAME` must match your provider. Do not copy the placeholder `.env.example` over working secrets.

Run this command each time you start or resume the Codespace:

```bash
bash -lc 'cd /workspaces/MiroFish && bash scripts/codespaces.sh'
```

Keep the terminal running and open private port **3000** from the Ports panel. The frontend proxies `/api` to backend port **5001**. First installation downloads the upstream Python dependencies and can take several minutes. Repeat launches detect an already-running app.

## Checks

```bash
npm run build
cd backend
uv run --with pytest pytest tests/test_arabic_locale.py
```

The language instruction asks the configured LLM for Arabic; model compliance is verified separately from the deterministic tests. Simulation results remain model-generated scenarios, not measured forecasts.

While the frontend dev server is running, open `/tests/rtl.html` to verify mixed Arabic/English prose, URL isolation, stable repeated rendering, unchanged copied text, LTR code and mirrored list padding without any API calls.
