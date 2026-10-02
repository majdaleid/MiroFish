#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
: "${LLM_API_KEY:?Add LLM_API_KEY as a Codespaces secret for majdaleid/MiroFish}"
: "${ZEP_API_KEY:?Add ZEP_API_KEY as a Codespaces secret for majdaleid/MiroFish}"
export PATH="$HOME/.local/bin:$PATH" UV_PYTHON=3.12 VITE_API_BASE_URL=/ BROWSER=none
if [[ -n "${CODESPACE_NAME:-}" ]]; then
  export __VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS="${CODESPACE_NAME}-3000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"
fi
if curl --max-time 5 -fsS http://127.0.0.1:5001/health >/dev/null 2>&1 &&
   curl --max-time 5 -fsS http://127.0.0.1:3000/api/graph/project/list >/dev/null 2>&1; then
  echo "MiroFish is already running. Open private port 3000 from the Ports panel."
  exit 0
fi
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
npm run setup:all
exec npm run dev
