#!/bin/bash
# Server Deployment Script for MCP Data Query Server
# This script handles common server environment issues

set -e  # Exit on error

# Configuration
MCP_TOKEN="eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMyMzM0NywiYWdlbnRJZCI6NTUyNTUyLCJlbmRwb2ludElkIjoiYWdlbnRfNTUyNTUyIiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc1NzI5NzYxMn0.Qw66VsLooShlL_sA9wD-oiKdcIzRpQrtt5AaleHM7l--DM-3IiMaMfOQp3hD1hZXK0Aq2ydkXjYGtUgugPZsAQ"
MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=$MCP_TOKEN"

echo "=== MCP Server Deployment Script ==="

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt >/dev/null 2>&1; then
            echo "ubuntu"
        elif command -v yum >/dev/null 2>&1; then
            echo "centos"
        elif command -v dnf >/dev/null 2>&1; then
            echo "fedora"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Install Python and pip based on OS
install_python() {
    local os_type=$(detect_os)
    echo "Detected OS: $os_type"
    
    case $os_type in
        "ubuntu")
            echo "Installing Python on Ubuntu/Debian..."
            sudo apt update
            sudo apt install -y python3 python3-pip python3-venv
            ;;
        "centos")
            echo "Installing Python on CentOS..."
            sudo yum install -y python3 python3-pip
            ;;
        "fedora")
            echo "Installing Python on Fedora..."
            sudo dnf install -y python3 python3-pip
            ;;
        "macos")
            echo "Installing Python on macOS..."
            if command -v brew >/dev/null 2>&1; then
                brew install python
            else
                echo "Please install Homebrew first: https://brew.sh/"
                exit 1
            fi
            ;;
        *)
            echo "Unknown OS. Please install Python 3.7+ manually."
            exit 1
            ;;
    esac
}

# Check and install Python
echo "Checking Python installation..."
PYTHON_CMD=""

if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Python not found. Installing..."
    install_python
    PYTHON_CMD="python3"
fi

echo "Using Python command: $PYTHON_CMD"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
echo "Python version: $PYTHON_VERSION"

# Check if pip is available
PIP_CMD=""
if command -v pip3 >/dev/null 2>&1; then
    PIP_CMD="pip3"
elif command -v pip >/dev/null 2>&1; then
    PIP_CMD="pip"
else
    echo "pip not found. Please install pip manually."
    exit 1
fi

echo "Using pip command: $PIP_CMD"

# Create virtual environment (recommended for servers)
echo "Creating virtual environment..."
if [[ ! -d "venv" ]]; then
    $PYTHON_CMD -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
if [[ -f "requirements.txt" ]]; then
    # Try with different index URLs if the default fails
    pip install -r requirements.txt || \
    pip install -r requirements.txt -i https://pypi.org/simple/ || \
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
else
    echo "requirements.txt not found. Installing core dependencies..."
    pip install mcp websockets pydantic python-dotenv mcp-proxy
fi

# Verify installation
echo "Verifying installation..."
python -c "import mcp, websockets, pydantic; print('All dependencies installed successfully')"

# Set environment variables
echo "Setting environment variables..."
export MCP_ENDPOINT="$MCP_ENDPOINT"
export MCP_CONFIG="./mcp_config.json"

# Create startup script
echo "Creating optimized startup script..."
cat > start_server.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
export MCP_ENDPOINT="wss://api.xiaozhi.me/mcp/?token=eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjMyMzM0NywiYWdlbnRJZCI6NTUyNTUyLCJlbmRwb2ludElkIjoiYWdlbnRfNTUyNTUyIiwicHVycG9zZSI6Im1jcC1lbmRwb2ludCIsImlhdCI6MTc1NzI5NzYxMn0.Qw66VsLooShlL_sA9wD-oiKdcIzRpQrtt5AaleHM7l--DM-3IiMaMfOQp3hD1hZXK0Aq2ydkXjYGtUgugPZsAQ"
export MCP_CONFIG="./mcp_config.json"
echo "Starting MCP Server..."
exec python mcp_pipe.py
EOF

chmod +x start_server.sh

echo "=== Deployment Complete ==="
echo ""
echo "To start the server:"
echo "  ./start_server.sh"
echo ""
echo "To run in background:"
echo "  nohup ./start_server.sh > mcp_server.log 2>&1 &"
echo ""
echo "To check logs:"
echo "  tail -f mcp_server.log"
echo ""
echo "Virtual environment is located in: ./venv"
echo "Activation command: source venv/bin/activate"
