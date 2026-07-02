#!/bin/bash
# Multi-Agent Council — MCP Server Launcher
# Usage: bash run_mcp.sh
#
# Dependencies: pip install -r backend/requirements.txt
# Model: set via .env or env vars (default: ollama)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load .env if present
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

echo "Multi-Agent Council MCP Server" >&2
echo "  Provider: ${llm_provider:-ollama}" >&2
echo "  Model: ${llm_model:-qwen2.5-coder:7b}" >&2
echo "  Tools: review_code chat analyze_file generate_code implement_fix" >&2

exec python3 -u -m backend.mcp_server
