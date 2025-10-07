#!/bin/bash
# Boltz MCP Server Startup Script
# This script sets up the environment and starts the MCP server with ngrok tunneling

# Exit on any error
# -e: exit if any command fails
# -u: exit if undefined variable is used
# -o pipefail: exit if any command in a pipe fails
set -euo pipefail

# Color codes for pretty output
# These ANSI escape codes colorize terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color - resets color

# Function to print colored messages
# Usage: print_info "message" - prints in blue
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Usage: print_success "message" - prints in green
print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Usage: print_error "message" - prints in red
print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Usage: print_warning "message" - prints in yellow
print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Get the directory where this script is located
# This allows us to reference other files relative to the script
# ${BASH_SOURCE[0]} = path to this script
# dirname = get directory part of path
# cd + pwd -P = resolve symlinks and get absolute path
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

print_info "Boltz MCP Server Startup"
print_info "Script directory: $SCRIPT_DIR"

# ============================================================================
# STEP 1: Check Python Installation
# ============================================================================

print_info "Checking Python installation..."

# Check if Python 3 is available
# command -v returns the path if command exists, empty if not
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed or not in PATH"
    exit 1
fi

# Get Python version
PYTHON_VERSION=$(python3 --version)
print_success "Found: $PYTHON_VERSION"

# ============================================================================
# STEP 2: Set up Python Virtual Environment (Optional but Recommended)
# ============================================================================

# Virtual environments isolate Python packages from system installation
# This prevents conflicts and allows installation without sudo
VENV_DIR="$SCRIPT_DIR/venv"

if [ ! -d "$VENV_DIR" ]; then
    print_info "Creating Python virtual environment..."
    # python3 -m venv creates a new virtual environment
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created at $VENV_DIR"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
# This modifies PATH to use venv's Python and pip
print_info "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# ============================================================================
# STEP 3: Install Dependencies
# ============================================================================

print_info "Installing Python dependencies..."

# Upgrade pip to latest version
# --quiet suppresses verbose output
pip install --quiet --upgrade pip

# Install FastMCP and other dependencies from requirements.txt
pip install --quiet -r "$SCRIPT_DIR/requirements.txt"

# Install Boltz from GitHub
# This is a separate step because it's not on PyPI
print_info "Installing Boltz (this may take a few minutes)..."
pip install --quiet git+https://github.com/jwohlwend/boltz.git

print_success "Dependencies installed"

# ============================================================================
# STEP 4: Check GPU Availability
# ============================================================================

print_info "Checking GPU availability..."

# nvidia-smi is the NVIDIA System Management Interface
# It shows GPU status, memory usage, temperature, etc.
if command -v nvidia-smi &> /dev/null; then
    # Run nvidia-smi and show GPU information
    nvidia-smi --query-gpu=index,name,memory.total --format=csv,noheader | while read -r line; do
        print_success "GPU: $line"
    done
else
    print_warning "nvidia-smi not found. Cannot verify GPU availability."
    print_warning "Boltz requires CUDA-capable GPU to run."
fi

# ============================================================================
# STEP 5: Load Environment Variables
# ============================================================================

# Load .env file if it exists
# .env files store configuration like ngrok auth tokens
ENV_FILE="$SCRIPT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    print_info "Loading environment variables from .env"
    # Export all variables from .env file
    # This makes them available to the Python script
    export $(grep -v '^#' "$ENV_FILE" | xargs)
else
    print_warning ".env file not found. Using default configuration."
fi

# ============================================================================
# STEP 6: Set up ngrok Tunnel
# ============================================================================

print_info "Setting up ngrok tunnel..."

# Check if NGROK_AUTH_TOKEN is set
# ${VAR:-default} syntax: use $VAR if set, otherwise use "default"
if [ -z "${NGROK_AUTH_TOKEN:-}" ]; then
    print_error "NGROK_AUTH_TOKEN not set"
    print_error "Please set it in .env file or environment"
    print_info "Get your auth token from: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

# Authenticate ngrok
# This stores the auth token in ~/.ngrok2/ngrok.yml (no sudo needed)
print_info "Authenticating with ngrok..."
ngrok config add-authtoken "$NGROK_AUTH_TOKEN"

# Start ngrok tunnel in background
# tcp 8000 = expose TCP port 8000
# We'll use this port for MCP communication
# --log=stdout sends logs to stdout
# & runs in background
print_info "Starting ngrok tunnel..."
ngrok tcp 8000 --log=stdout > "$SCRIPT_DIR/ngrok.log" 2>&1 &

# Save ngrok process ID so we can kill it later if needed
NGROK_PID=$!
echo $NGROK_PID > "$SCRIPT_DIR/ngrok.pid"

# Wait for ngrok to start and get the tunnel URL
# ngrok takes a few seconds to establish the tunnel
print_info "Waiting for ngrok to start..."
sleep 3

# Get the public ngrok URL from the API
# ngrok runs a local API on port 4040 that shows tunnel info
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # ngrok API returns list of tunnels
    # We want the public_url of the first tunnel
    print(data['tunnels'][0]['public_url'])
except:
    print('ERROR')
")

if [ "$NGROK_URL" = "ERROR" ] || [ -z "$NGROK_URL" ]; then
    print_error "Failed to get ngrok URL"
    print_error "Check ngrok.log for details"
    # Kill ngrok process
    kill $NGROK_PID 2>/dev/null || true
    exit 1
fi

print_success "ngrok tunnel established!"
print_success "Public URL: $NGROK_URL"

# Save URL to file for easy access
echo "$NGROK_URL" > "$SCRIPT_DIR/ngrok_url.txt"

# Display connection information for Claude Desktop configuration
print_info "═══════════════════════════════════════════════════════════"
print_success "MCP Server is ready!"
print_info "Copy this URL for Claude Desktop configuration:"
echo ""
echo "    $NGROK_URL"
echo ""
print_info "This URL will remain active while the server is running."
print_info "═══════════════════════════════════════════════════════════"

# ============================================================================
# STEP 7: Start MCP Server
# ============================================================================

print_info "Starting Boltz MCP Server..."
print_info "Press Ctrl+C to stop the server"

# Cleanup function - called when script exits
# This ensures ngrok process is killed even if script crashes
cleanup() {
    print_info "\nShutting down..."
    # Kill ngrok process
    if [ -f "$SCRIPT_DIR/ngrok.pid" ]; then
        NGROK_PID=$(cat "$SCRIPT_DIR/ngrok.pid")
        kill $NGROK_PID 2>/dev/null || true
        rm "$SCRIPT_DIR/ngrok.pid"
    fi
    print_success "Server stopped"
}

# Register cleanup function to run on EXIT signal
# This catches Ctrl+C, script errors, normal exit, etc.
trap cleanup EXIT

# Start the Python MCP server
# python3 -u = unbuffered output (print immediately, don't wait for newline)
# This ensures we see logs in real-time
cd "$SCRIPT_DIR"
python3 -u boltz_mcp_server.py

# If we get here, the server has exited
# The cleanup function will run automatically
