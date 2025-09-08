#!/bin/bash
# Simple MCP Server Startup Script
# Minimal version with automatic Python detection

# Set environment variables
export MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMyMzM0NywiYWdlbnRJZCI6NTUyNTUyLCJlbmRwb2ludElkIjoiYWdlbnRfNTUyNTUyIiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc1NzI5NzYxMn0.Qw66VsLooShlL_sA9wD-oiKdcIzRpQrtt5AaleHM7l--DM-3IiMaMfOQp3hD1hZXK0Aq2ydkXjYGtUgugPZsAQ"
export MCP_CONFIG="./mcp_config.json"

echo "Starting MCP Server..."

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

# Update config file with correct Python command
echo "Updating configuration..."
cat > mcp_config.json << EOF
{
  "mcpServers": {
    "data-query-server": {
      "type": "stdio",
      "command": "$PYTHON",
      "args": ["data_query_server.py"],
      "description": "数据查询 MCP 服务器，提供用户、产品、订单数据的查询功能"
    },
    "remote-sse-server": {
      "type": "sse",
      "url": "https://api.example.com/sse",
      "disabled": true
    },
    "remote-http-server": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "disabled": true
    }
  }
}
EOF

# Install dependencies if needed
if ! $PYTHON -c "import mcp" >/dev/null 2>&1; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt || pip install -r requirements.txt || {
        echo "Failed to install dependencies"
        exit 1
    }
fi

# Start server
echo "Starting server..."
exec $PYTHON mcp_pipe.py
