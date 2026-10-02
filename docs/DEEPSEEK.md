# Optional DeepSeek V4.1 Flash

The **Model** selector beside the language selector offers **Current default**
and **DeepSeek V4.1 Flash**. Current default preserves your existing
`LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL_NAME` configuration.

1. Create a key at https://platform.deepseek.com/api_keys.
2. In https://github.com/settings/codespaces, add `DEEPSEEK_API_KEY` and grant
   access to `majdaleid/MiroFish`. For local use, add it to the ignored root `.env`.
3. Restart the Codespace/backend so it receives the new secret. Start MiroFish
   with the usual command:

   ```bash
   bash -lc 'cd /workspaces/MiroFish && bash scripts/codespaces.sh'
   ```

4. Open the Model menu and select **DeepSeek V4.1 Flash**. Choose **Current
   default** to switch back. If you added a secret to an existing Codespace,
   accept GitHub's restart/update prompt so the secret reaches new processes.

Only the provider name is stored in the browser. Keys stay on the backend and
are never returned by the settings API. DeepSeek is unavailable until its key
is configured; requests never silently fall back to another provider.

The choice applies to new ontology, preparation, simulation, report, and chat
requests. Background jobs capture their provider when they start, and running
agents keep their existing model. Select your preferred model before starting
a new project for a consistent workflow. This selection controls MiroFish's LLM
calls; Zep Cloud retains its own graph-processing configuration.

The API uses `https://api.deepseek.com` and model `deepseek-flash`, the official
alias for V4.1 Flash. Non-thinking mode keeps the existing JSON and CAMEL tool
conversation compatible without adding a reasoning-history implementation.

Official references:
- https://deepseek.com/en/news/deepseek-v4-1-flash/
- https://api-docs.deepseek.com/guides/thinking_mode/
