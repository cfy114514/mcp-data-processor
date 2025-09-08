#!/bin/bash
# Smart Configuration Generator
# Automatically detects the correct Python command and updates config

echo "Detecting Python command..."

# Find the correct Python command
PYTHON_CMD=""
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
    echo "Found: python3"
elif command -v python >/dev/null 2>&1; then
    # Check if it's Python 3
    PYTHON_VERSION=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
    MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
    if [[ $MAJOR_VERSION -eq 3 ]]; then
        PYTHON_CMD="python"
        echo "Found: python (Python 3.x)"
    else
        echo "Error: Found python but it's Python 2.x. Python 3 is required."
        exit 1
    fi
else
    echo "Error: No Python installation found"
    exit 1
fi

echo "Using Python command: $PYTHON_CMD"

# Generate the correct config file
cat > mcp_config.json << EOF
{
  "mcpServers": {
    "data-query-server": {
      "type": "stdio",
      "command": "$PYTHON_CMD",
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

echo "Configuration updated successfully!"
echo "Python command in config: $PYTHON_CMD"
