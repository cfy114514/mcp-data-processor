#!/bin/bash
# Data Query MCP Server Startup Script (Linux/Mac)
# Encoding: UTF-8

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# Set environment variables
export MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMyMzM0NywiYWdlbnRJZCI6NTUyNTUyLCJlbmRwb2ludElkIjoiYWdlbnRfNTUyNTUyIiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc1NzI5NzYxMn0.Qw66VsLooShlL_sA9wD-oiKdcIzRpQrtt5AaleHM7l--DM-3IiMaMfOQp3hD1hZXK0Aq2ydkXjYGtUgugPZsAQ"
export MCP_CONFIG="./mcp_config.json"

print_info "Starting Data Query MCP Server..."
print_debug "Endpoint: $MCP_ENDPOINT"

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    print_error "Python not found. Please install Python 3.7+ and ensure it's in your PATH."
    exit 1
fi

# Determine Python command
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

print_info "Using Python command: $PYTHON_CMD"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d. -f2)

if [[ $MAJOR_VERSION -lt 3 ]] || [[ $MAJOR_VERSION -eq 3 && $MINOR_VERSION -lt 7 ]]; then
    print_error "Python version $PYTHON_VERSION is not supported. Please upgrade to Python 3.7 or higher."
    exit 1
fi

print_info "Python version: $PYTHON_VERSION ✓"

# Check if requirements.txt exists
if [[ ! -f "requirements.txt" ]]; then
    print_error "requirements.txt not found. Please ensure you're in the correct directory."
    exit 1
fi

# Check if mcp_pipe.py exists
if [[ ! -f "mcp_pipe.py" ]]; then
    print_error "mcp_pipe.py not found. Please ensure you're in the correct directory."
    exit 1
fi

# Check if data_query_server.py exists
if [[ ! -f "data_query_server.py" ]]; then
    print_error "data_query_server.py not found. Please ensure you're in the correct directory."
    exit 1
fi

# Check dependencies
print_info "Checking Python dependencies..."
if ! $PYTHON_CMD -c "import mcp, websockets, pydantic" 2>/dev/null; then
    print_warning "Some dependencies are missing. Installing..."
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        print_error "pip not found. Please install pip to manage Python packages."
        exit 1
    fi
    
    # Determine pip command
    PIP_CMD="pip3"
    if ! command -v pip3 &> /dev/null; then
        PIP_CMD="pip"
    fi
    
    print_info "Installing dependencies with $PIP_CMD..."
    if ! $PIP_CMD install -r requirements.txt; then
        print_error "Failed to install dependencies. Please check your internet connection and try again."
        exit 1
    fi
    
    print_info "Dependencies installed successfully ✓"
else
    print_info "All dependencies are available ✓"
fi

# Function to handle cleanup on exit
cleanup() {
    print_warning "Shutting down MCP server..."
    # Kill any background processes if needed
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

print_info "Starting MCP pipe server..."
print_warning "Press Ctrl+C to stop the server"

# Start MCP server
exec $PYTHON_CMD mcp_pipe.py
