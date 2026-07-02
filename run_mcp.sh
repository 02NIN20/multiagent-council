#!/bin/bash
# =============================================================================
# Qwen Council — MCP Server Launcher
# =============================================================================
# Usage:
#   Export QWEN_COUNCIL_API_URL or leave default (http://localhost:8000)
#   Then run: bash run_mcp.sh
#
# For OpenCode / Claude Desktop / Cursor:
#   Add this to your opencode.json:
#   {
#     "mcpServers": {
#       "qwen-council": {
#         "command": "bash",
#         "args": ["/path/to/qwen-council/run_mcp.sh"]
#       }
#     }
#   }
# =============================================================================

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Default API URL (change to your deployed instance)
export QWEN_COUNCIL_API_URL="${QWEN_COUNCIL_API_URL:-http://localhost:8000}"

# Ensure Python can find the backend module
export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"

echo "Qwen Council MCP Server" >&2
echo "  API: $QWEN_COUNCIL_API_URL" >&2
echo "  CWD: $SCRIPT_DIR" >&2

exec python3 -u -m backend.mcp_server
