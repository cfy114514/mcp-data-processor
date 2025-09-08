# Data Query MCP Server Startup Script (Windows PowerShell)
# UTF-8 Encoding

# Set environment variables
$env:MCP_ENDPOINT = "wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMyMzM0NywiYWdlbnRJZCI6NTUyNTUyLCJlbmRwb2ludElkIjoiYWdlbnRfNTUyNTUyIiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc1NzI5NzYxMn0.Qw66VsLooShlL_sA9wD-oiKdcIzRpQrtt5AaleHM7l--DM-3IiMaMfOQp3hD1hZXK0Aq2ydkXjYGtUgugPZsAQ"
$env:MCP_CONFIG = "./mcp_config.json"

Write-Host "Starting Data Query MCP Server..." -ForegroundColor Green
Write-Host "Endpoint: $env:MCP_ENDPOINT" -ForegroundColor Yellow

# Check if Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Error: Python not found. Please ensure Python is installed and added to PATH." -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host "Checking Python dependencies..." -ForegroundColor Blue
python -c "import mcp, websockets, pydantic" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing dependencies..." -ForegroundColor Blue
    pip install -r requirements.txt
}

# Start MCP server
Write-Host "Starting MCP pipe server..." -ForegroundColor Green
python mcp_pipe.py
