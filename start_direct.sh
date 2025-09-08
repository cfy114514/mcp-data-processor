#!/bin/bash
# Ultra Simple Direct Startup - bypasses config file issues
# Runs the data query server directly

# Set environment variables
export MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMyMzM0NywiYWdlbnRJZCI6NTUyNTUyLCJlbmRwb2ludElkIjoiYWdlbnRfNTUyNTUyIiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc1NzI5NzYxMn0.Qw66VsLooShlL_sA9wD-oiKdcIzRpQrtt5AaleHM7l--DM-3IiMaMfOQp3hD1hZXK0Aq2ydkXjYGtUgugPZsAQ"

echo "Starting MCP Server (Direct Mode)..."

# Find Python command
PYTHON=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
else
    echo "Error: Python not found"
    exit 1
fi

echo "Using: $PYTHON"

# Install dependencies if needed
if ! $PYTHON -c "import mcp" >/dev/null 2>&1; then
    echo "Installing dependencies..."
    if command -v pip3 >/dev/null 2>&1; then
        pip3 install -r requirements.txt
    elif command -v pip >/dev/null 2>&1; then
        pip install -r requirements.txt
    else
        echo "Error: pip not found"
        exit 1
    fi
fi

# Run using mcp_pipe.py with direct script path (bypasses config)
echo "Starting server directly..."
exec $PYTHON mcp_pipe.py data_query_server.py
