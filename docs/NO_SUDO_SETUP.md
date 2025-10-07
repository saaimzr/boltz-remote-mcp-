# Boltz MCP Server Setup - No Sudo Required

**Complete step-by-step guide for setting up Boltz MCP server without administrator privileges.**

This guide is designed for users who:
- Don't have sudo/root access on their lab computer
- Need to run everything in userspace
- Want to expose their server to Claude Desktop remotely

---

## 📋 Overview

Since you don't have sudo, you can't:
- ❌ Install system packages
- ❌ Open firewall ports (need admin)
- ❌ Install reverse proxy servers (nginx/caddy)

But you CAN:
- ✅ Run Python servers in userspace
- ✅ Use SSH tunneling for remote access
- ✅ Deploy to FastMCP Cloud (recommended)

---

## 🎯 Recommended Approach: FastMCP Cloud

**This is the BEST option without sudo** - it bypasses all networking/firewall issues.

### Prerequisites
- GitHub account
- Git installed on lab computer (or ability to copy files)
- Lab computer has internet access

### The Three Machines Involved

Let's be clear about the architecture:

```
┌─────────────────────┐         ┌──────────────────┐         ┌────────────────────┐
│   YOUR LAPTOP       │         │  FASTMCP CLOUD   │         │  LAB COMPUTER      │
│   (Windows)         │ ◄─────► │  (Automatic)     │ ◄─────► │  (Linux/GPU)       │
│                     │         │                  │         │                     │
│  Claude Desktop     │  HTTPS  │  Your deployed   │  Runs   │  Boltz models      │
│  (MCP Client)       │         │  MCP server      │  on     │  (on GPUs)         │
└─────────────────────┘         └──────────────────┘         └────────────────────┘
```

**Important:** With FastMCP Cloud, your lab computer doesn't need to be network-accessible! FastMCP Cloud runs the MCP server, but it can't run Boltz (no GPUs). So this won't work for your use case.

---

## ✅ Working Solution: SSH Tunnel (No Sudo Required)

Since FastMCP Cloud doesn't have GPUs, and you need to run Boltz on your lab computer, we'll use **SSH tunneling** to expose your local HTTP server.

### Architecture

```
┌─────────────────────┐         ┌────────────────────┐
│   YOUR LAPTOP       │  SSH    │  LAB COMPUTER      │
│   (Windows)         │ Tunnel  │  (Linux/GPU)       │
│                     │ ◄─────► │                    │
│  Claude Desktop  ───┼────────►│  Boltz MCP Server  │
│  localhost:8000     │         │  localhost:8000    │
└─────────────────────┘         └────────────────────┘
```

**Key insight:** Use SSH to forward port 8000 from lab computer to your laptop. No firewall changes needed!

---

## 📝 Complete Setup Instructions

---

## PART 1: Lab Computer Setup (Linux/GPU Server)

**Context:** You will SSH into this computer to set everything up. All commands run here.

### Step 1.1: Check Your Current Location

```bash
# First, SSH into your lab computer from your Windows laptop
# Example: ssh yourusername@lab-server.university.edu
ssh yourusername@lab-computer-hostname

# After login, you should see a prompt like:
# yourusername@lab-computer:~$

# Verify you're on the lab computer
hostname
# Should show: lab-computer-hostname (or similar)

# Check where you are
pwd
# Should show: /home/yourusername (or your home directory)
```

### Step 1.2: Transfer Project Files to Lab Computer

**Option A: If you have Git on lab computer**

```bash
# On lab computer (via SSH)
cd ~
git clone https://github.com/YOUR_USERNAME/boltz-remote-mcp.git
cd boltz-remote-mcp

# Verify files are there
ls
# Should see: README.md, server/, docs/, etc.

cd server
ls
# Should see: boltz_mcp_server.py, requirements.txt, .env.example
```

**Option B: If no Git, use SCP from your Windows laptop**

```bash
# Open NEW terminal/PowerShell on YOUR LAPTOP (not SSH session)
# Navigate to project directory
cd C:\Users\saaim\boltz-remote-mcp

# Copy entire server directory to lab computer
scp -r server yourusername@lab-computer-hostname:~/boltz-mcp-server/

# This will prompt for your lab computer password
# Wait for transfer to complete

# Now go back to your SSH session and verify
cd ~/boltz-mcp-server
ls
# Should see: boltz_mcp_server.py, requirements.txt, .env.example, venv/ (if you copied it)
```

### Step 1.3: Verify Python Version

**Critical:** Boltz ONLY works with Python 3.10, 3.11, or 3.12. NOT 3.13+.

```bash
# On lab computer (via SSH)
# Check your default Python version
python3 --version

# Example outputs:
# Python 3.12.0  ✅ Good!
# Python 3.11.5  ✅ Good!
# Python 3.10.8  ✅ Good!
# Python 3.13.1  ❌ TOO NEW - Boltz won't work!
# Python 3.9.7   ❌ TOO OLD - Boltz won't work!
```

**If Python 3.13+, find an older version:**

```bash
# Check for other Python versions
ls /usr/bin/python3*

# You might see:
# /usr/bin/python3
# /usr/bin/python3.10
# /usr/bin/python3.11
# /usr/bin/python3.12
# /usr/bin/python3.13

# Try each one to find a compatible version
python3.12 --version
# If this works and shows 3.12.x, use python3.12 in all commands below

python3.11 --version
# Or use python3.11 if this works

python3.10 --version
# Or use python3.10 if this works
```

**If NO compatible Python version exists:**

You'll need to install Python 3.12 in userspace using `pyenv`:

```bash
# Install pyenv (no sudo required)
curl https://pyenv.run | bash

# Add to your shell configuration
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Reload shell configuration
source ~/.bashrc

# Install Python 3.12 (this takes 5-10 minutes)
pyenv install 3.12.8

# Set as default for this directory
cd ~/boltz-mcp-server
pyenv local 3.12.8

# Verify
python --version
# Should now show: Python 3.12.8
```

### Step 1.4: Create Python Virtual Environment

**What is a venv?** An isolated Python environment so packages don't conflict with system Python.

```bash
# On lab computer (via SSH)
cd ~/boltz-mcp-server

# If you already have a venv directory from before, skip to Step 1.5
# Otherwise, create a new virtual environment:

# Replace python3 with python3.12 (or whichever version you found above) if needed
python3 -m venv venv

# What this does:
# - Creates a directory called 'venv' with its own Python
# - Installs pip (package installer) in venv
# - Isolates packages from system Python

# Verify venv was created
ls -la
# You should see a 'venv' directory

ls venv/
# You should see: bin/ include/ lib/ lib64 pyvenv.cfg
```

### Step 1.5: Activate Virtual Environment

**IMPORTANT:** You must activate the venv EVERY time you open a new SSH session.

```bash
# On lab computer (via SSH)
cd ~/boltz-mcp-server

# Activate the virtual environment
source venv/bin/activate

# Your prompt will change to show (venv) at the beginning:
# Before: yourusername@lab-computer:~/boltz-mcp-server$
# After:  (venv) yourusername@lab-computer:~/boltz-mcp-server$

# Verify you're using the venv Python
which python
# Should show: /home/yourusername/boltz-mcp-server/venv/bin/python

which pip
# Should show: /home/yourusername/boltz-mcp-server/venv/bin/pip

python --version
# Should show your compatible Python version (3.10, 3.11, or 3.12)
```

**Troubleshooting:**
- If prompt doesn't change, the activate script didn't run
- Make sure you're in the right directory: `pwd` should show `/home/yourusername/boltz-mcp-server`
- Try: `ls venv/bin/activate` to verify the file exists

### Step 1.6: Upgrade Pip

```bash
# On lab computer (via SSH, with venv activated)
# You should see (venv) in your prompt

# Upgrade pip to latest version
pip install --upgrade pip

# Expected output:
# Successfully installed pip-24.x.x (or similar)

# Verify pip version
pip --version
# Should show: pip 24.x.x from /home/yourusername/boltz-mcp-server/venv/lib/python3.x/site-packages/pip (python 3.x)
```

### Step 1.7: Install FastMCP and Dependencies

```bash
# On lab computer (via SSH, with venv activated)
# Make sure you're in the server directory
pwd
# Should show: /home/yourusername/boltz-mcp-server

# Install dependencies from requirements.txt
pip install -r requirements.txt

# What this installs:
# - fastmcp>=2.0.0 (MCP server framework)
# - python-dotenv>=1.0.0 (for .env file loading)

# Expected output:
# Collecting fastmcp>=2.0.0
#   Downloading fastmcp-2.x.x-py3-none-any.whl
# ...
# Successfully installed fastmcp-2.x.x python-dotenv-1.x.x

# Verify FastMCP is installed
pip show fastmcp

# Should show:
# Name: fastmcp
# Version: 2.x.x
# Location: /home/yourusername/boltz-mcp-server/venv/lib/python3.x/site-packages
```

### Step 1.8: Install Boltz (This Takes Time!)

**Warning:** This step downloads ~3-5GB of dependencies including PyTorch. It takes 5-15 minutes depending on your internet speed.

```bash
# On lab computer (via SSH, with venv activated)
# Make sure you're in the right place
pwd
# Should show: /home/yourusername/boltz-mcp-server

# Install Boltz with CUDA support
pip install boltz[cuda] -U

# What this does:
# - Downloads Boltz from PyPI
# - Installs PyTorch with CUDA support (~2GB)
# - Installs transformers, scipy, numpy, rdkit, etc. (~3GB)
# - The [cuda] part ensures CUDA-compatible versions
# - The -U flag means upgrade if already installed

# This will show LOTS of output like:
# Collecting boltz
#   Downloading boltz-x.x.x-py3-none-any.whl
# Collecting torch>=2.0.0
#   Downloading torch-2.x.x-cp312-cp312-linux_x86_64.whl (755 MB)
#     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 755/755 MB 10.2 MB/s eta 0:00:00
# ... (many more packages)
# Successfully installed boltz-x.x.x torch-2.x.x ...

# IMPORTANT: If this fails with "Python version not supported", you need Python 3.10-3.12
# Go back to Step 1.3 and use a compatible version

# Verify Boltz is installed
pip show boltz

# Should show:
# Name: boltz
# Version: x.x.x

# Test Boltz command-line tool
boltz --help

# Should show:
# usage: boltz [-h] {predict} ...
# Boltz - Protein Structure Prediction
# ...

# If you see this, SUCCESS! Boltz is installed correctly.
```

**Common Issues:**

**Error: "Could not find a version that satisfies the requirement torch"**
- Your Python version might be incompatible
- Go back to Step 1.3

**Error: "No CUDA-capable device is detected"** (when testing later)
- CUDA drivers not installed (contact lab admin)
- Check with: `nvidia-smi`

**Error: "Killed" during installation**
- Out of memory during pip install
- Try: `pip install boltz[cuda] -U --no-cache-dir`

### Step 1.9: Verify GPU Access

```bash
# On lab computer (via SSH)
# Check if CUDA/GPUs are available

nvidia-smi

# Expected output (if GPUs are available):
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 525.x.x    Driver Version: 525.x.x    CUDA Version: 12.x       |
# |-------------------------------+----------------------+----------------------+
# | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
# | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
# |===============================+======================+======================|
# |   0  NVIDIA A100        Off  | 00000000:00:04.0 Off |                    0 |
# | N/A   30C    P0    45W / 250W |      0MiB / 40960MiB |      0%      Default |
# +-------------------------------+----------------------+----------------------+

# If you see this, SUCCESS! You have GPU access.

# Check which GPUs are visible to your user
echo $CUDA_VISIBLE_DEVICES
# If empty, all GPUs are visible
# If shows "0,1,2", you can access GPUs 0, 1, and 2
```

**If nvidia-smi fails:**
```bash
# Error: "nvidia-smi: command not found"
# This means:
# 1. CUDA drivers are not installed, OR
# 2. You don't have access to GPUs

# Contact your lab administrator and ask:
# "Can you verify I have access to GPUs? nvidia-smi command is not found."
```

### Step 1.10: Configure Environment Variables

```bash
# On lab computer (via SSH)
cd ~/boltz-mcp-server

# Copy the example environment file
cp .env.example .env

# Open the file in a text editor
# If you have nano:
nano .env

# If nano is not installed, try vim:
vim .env

# If neither works, use this:
cat > .env << 'EOF'
# Server Configuration
BOLTZ_TRANSPORT=http
BOLTZ_HOST=127.0.0.1
BOLTZ_PORT=8000

# GPU Configuration
CUDA_VISIBLE_DEVICES=0

# Boltz Parameters
DEFAULT_RECYCLING_STEPS=3
DEFAULT_SAMPLING_STEPS=200
DEFAULT_DIFFUSION_SAMPLES=1
EOF

# Verify file was created
cat .env

# Should show:
# # Server Configuration
# BOLTZ_TRANSPORT=http
# BOLTZ_HOST=127.0.0.1
# BOLTZ_PORT=8000
# ...
```

**Important configuration notes:**

- `BOLTZ_HOST=127.0.0.1` - This binds to localhost only (security)
- `BOLTZ_PORT=8000` - The port the server listens on
- `CUDA_VISIBLE_DEVICES=0` - Use GPU 0 (adjust if you have multiple GPUs)

**If you have multiple GPUs:**
```bash
# To use GPUs 0 and 1:
CUDA_VISIBLE_DEVICES=0,1

# To use only GPU 2:
CUDA_VISIBLE_DEVICES=2

# To see available GPUs:
nvidia-smi --list-gpus
```

### Step 1.11: Test Server Startup (Dry Run)

Let's make sure everything works before setting up the tunnel.

```bash
# On lab computer (via SSH, with venv activated)
cd ~/boltz-mcp-server

# Load environment variables
source .env

# Or use this to load .env automatically:
export $(cat .env | grep -v '^#' | xargs)

# Start the server
python boltz_mcp_server.py

# Expected output:
# Starting Boltz MCP Server...
# Upload directory: /home/yourusername/.boltz_mcp/uploads
# Output directory: /home/yourusername/.boltz_mcp/outputs
# Model cache directory: /home/yourusername/.boltz_mcp/models
#
# ============================================================
# Starting HTTP server on 127.0.0.1:8000
# Server will be accessible at: http://127.0.0.1:8000/mcp/
# ============================================================
# INFO:     Started server process [12345]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)

# If you see this, SUCCESS! The server is running.
```

**Test the server (open another SSH session):**

```bash
# Open a NEW terminal, SSH to lab computer again
ssh yourusername@lab-computer-hostname

# Test if server is responding
curl http://localhost:8000/mcp/

# You should get a JSON response (it might be an error, that's OK)
# The important thing is you get a response, not "connection refused"
```

**Stop the server:**
```bash
# Go back to the terminal where server is running
# Press Ctrl+C

# Server will stop:
# ^CINFO:     Shutting down
# INFO:     Finished server process [12345]
```

Great! Server works. Now let's set up the SSH tunnel.

---

## PART 2: Windows Laptop Setup (Your Local Machine)

**Context:** These commands run on YOUR laptop (Windows), NOT the lab computer.

### Step 2.1: Create SSH Tunnel

**What is SSH tunneling?** It creates a secure "tunnel" that forwards network traffic from your laptop to the lab computer. This bypasses firewall issues since you're using SSH (port 22), which is already open.

```bash
# On YOUR LAPTOP (Windows PowerShell or Command Prompt)

# Open PowerShell (NOT in SSH session)
# Press Windows Key + X, then select "Windows PowerShell" or "Terminal"

# Create SSH tunnel that forwards port 8000
ssh -L 8000:localhost:8000 yourusername@lab-computer-hostname

# What this does:
# -L 8000:localhost:8000 means:
#   - Forward connections to YOUR LAPTOP's port 8000
#   - To the lab computer's localhost:8000
#   - Through the SSH connection
#
# After running this, you'll be logged into the lab computer via SSH

# Now you're in an SSH session. Your prompt shows:
# yourusername@lab-computer:~$
```

**Keep this terminal window open!** The tunnel only works while this SSH session is active.

### Step 2.2: Start the Server (in the SSH tunnel session)

```bash
# In the SSH tunnel terminal (you're now on lab computer)
cd ~/boltz-mcp-server

# Activate venv
source venv/bin/activate

# Start the server
python boltz_mcp_server.py

# Expected output:
# Starting Boltz MCP Server...
# ...
# ============================================================
# Starting HTTP server on 127.0.0.1:8000
# Server will be accessible at: http://127.0.0.1:8000/mcp/
# ============================================================

# The server is now running!
# Leave this terminal open.
```

### Step 2.3: Test the Tunnel (from another terminal on laptop)

```bash
# Open a NEW PowerShell window on YOUR LAPTOP
# Press Windows Key + X, then "Windows PowerShell" (new window)

# Test connection to localhost:8000 (which tunnels to lab computer)
curl http://localhost:8000/mcp/

# Or open in browser:
start http://localhost:8000/mcp/

# You should see JSON response or a basic page
# This confirms the tunnel is working!
```

### Step 2.4: Configure Claude Desktop

```bash
# On YOUR LAPTOP
# Navigate to Claude config directory

cd $env:APPDATA\Claude

# Check if config file exists
ls

# You should see claude_desktop_config.json
# If not, create it:
New-Item -Path claude_desktop_config.json -ItemType File

# Edit the file
notepad claude_desktop_config.json
```

**Add this configuration:**

```json
{
  "mcpServers": {
    "boltz-remote": {
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

**Important:** Use `localhost:8000` because the SSH tunnel makes the remote server available locally.

**Save and close** the file.

### Step 2.5: Restart Claude Desktop

```bash
# On YOUR LAPTOP

# Close Claude Desktop completely
# - Click X on all windows
# - Check system tray (bottom-right, near clock)
# - Right-click Claude icon if present, select "Quit"

# Or use Task Manager:
# 1. Press Ctrl+Shift+Esc
# 2. Find "Claude" process
# 3. Right-click -> End Task

# Wait 5 seconds

# Restart Claude Desktop
# - Click Claude icon on desktop, or
# - Search for "Claude" in Start menu
```

### Step 2.6: Verify Connection in Claude Desktop

1. Open Claude Desktop
2. Look for a 🔨 (hammer) icon in the interface - this indicates MCP server is connected
3. Start a new conversation

Type in Claude:
```
Can you use the get_server_info tool to show me information about the Boltz server?
```

**Expected response:**
Claude should call the `get_server_info` tool and return:
- Server version
- GPU information
- Disk space
- Upload/output directories
- Active jobs count

**If this works, SUCCESS!** Your tunnel is working and Claude can talk to your Boltz server.

---

## PART 3: Daily Usage Workflow

Every time you want to use the Boltz server:

### On Your Laptop (Windows):

```powershell
# 1. Open PowerShell
# 2. Create SSH tunnel
ssh -L 8000:localhost:8000 yourusername@lab-computer-hostname

# 3. Once logged in, start the server
cd ~/boltz-mcp-server
source venv/bin/activate
python boltz_mcp_server.py

# 4. Leave this terminal open
# 5. Open Claude Desktop and use normally
```

### Keeping It Running in Background (tmux)

**Problem:** If you close PowerShell, the tunnel breaks and server stops.

**Solution:** Use `tmux` on the lab computer to keep the server running.

```bash
# In your SSH tunnel terminal (on lab computer)

# Start tmux session
tmux new -s boltz-server

# Now you're in a tmux session
# Start the server
cd ~/boltz-mcp-server
source venv/bin/activate
python boltz_mcp_server.py

# Server is running

# Detach from tmux: Press Ctrl+B, then press D
# You'll return to normal terminal, but server keeps running

# You can now close this SSH window

# Later, to reattach:
ssh yourusername@lab-computer-hostname
tmux attach -t boltz-server

# You'll see the server still running!
```

**Important:** You still need the SSH tunnel on your laptop:
```powershell
# On your laptop, keep this running:
ssh -L 8000:localhost:8000 yourusername@lab-computer-hostname

# The tunnel needs to stay active for Claude to connect
```

---

## PART 4: Testing with Real Predictions

### Test 1: Get Server Info

In Claude Desktop:
```
Use the get_server_info tool to show me the server status.
```

Claude should return GPU info, disk space, etc.

### Test 2: Predict from Sequence

In Claude Desktop:
```
Can you predict the structure of this protein sequence using Boltz:

MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL
```

Claude will:
1. Call `predict_structure_from_sequence` with the sequence
2. Get a job_id back
3. Poll `check_job_status` periodically
4. Once complete, call `get_prediction_result`
5. Return the CIF file to you

**Note:** First prediction will be slow (~10-20 minutes) because Boltz needs to download model weights (~3GB). Subsequent predictions will be faster.

### Test 3: Check Job Status

If a job is running:
```
What's the status of my Boltz prediction job?
```

Claude will call `list_jobs` to show recent jobs and their status.

---

## Troubleshooting

### Server won't start

**Error:** `ModuleNotFoundError: No module named 'fastmcp'`

```bash
# On lab computer, in venv
pip install fastmcp>=2.0.0
```

**Error:** `ModuleNotFoundError: No module named 'boltz'`

```bash
# On lab computer, in venv
pip install boltz[cuda] -U
```

**Error:** `Address already in use`

```bash
# Something is already running on port 8000
# Find what's using it:
lsof -i :8000

# Or kill it:
pkill -f boltz_mcp_server
```

### Claude can't connect

**Check 1: Is server running?**
```bash
# On lab computer
curl http://localhost:8000/mcp/
```

**Check 2: Is SSH tunnel active?**
```powershell
# On your laptop
curl http://localhost:8000/mcp/
```

**Check 3: Is Claude Desktop config correct?**
```powershell
# On your laptop
cat $env:APPDATA\Claude\claude_desktop_config.json

# Should show:
# {
#   "mcpServers": {
#     "boltz-remote": {
#       "url": "http://localhost:8000/mcp"
#     }
#   }
# }
```

**Check 4: Did you restart Claude Desktop?**
- Fully quit (check system tray)
- Restart the app

### GPU not working

**Check GPU access:**
```bash
# On lab computer
nvidia-smi

# Should show GPU info
# If not, contact lab admin
```

**Check CUDA visibility:**
```bash
# On lab computer
echo $CUDA_VISIBLE_DEVICES

# Should show GPU IDs (0, 0,1, etc.)
# If empty, all GPUs are visible
```

### Predictions failing

**Check server logs:**
```bash
# In the terminal where server is running
# Look for error messages after calling predict_structure_from_sequence

# Common errors:
# "CUDA out of memory" - GPU doesn't have enough RAM
#   Solution: Use smaller sequences or reduce sampling_steps
#
# "No CUDA devices available" - GPU not accessible
#   Solution: Check nvidia-smi, contact admin
```

### SSH tunnel disconnects

**Use autossh to keep tunnel alive:**

```powershell
# On Windows, in PowerShell
# Keep retrying SSH tunnel if it drops

while ($true) {
    ssh -L 8000:localhost:8000 yourusername@lab-computer-hostname
    Write-Host "Tunnel disconnected, reconnecting in 5 seconds..."
    Start-Sleep -Seconds 5
}
```

---

## Summary

**What you achieved:**
1. ✅ Installed Python environment without sudo
2. ✅ Installed FastMCP and Boltz
3. ✅ Set up HTTP server on lab computer
4. ✅ Created SSH tunnel to expose server to laptop
5. ✅ Connected Claude Desktop to use Boltz remotely

**The key insight:** SSH tunneling bypasses all firewall/networking issues because you're using SSH (which is already allowed) to forward traffic.

**Daily workflow:**
1. SSH tunnel from laptop to lab computer (with port forwarding)
2. Start Boltz server on lab computer
3. Use Claude Desktop on laptop (connects via localhost:8000)

**Next steps:**
- Try predicting protein structures
- Adjust GPU settings if needed
- Read [usage_examples.md](usage_examples.md) for workflows

---

**Questions?** See [troubleshooting.md](troubleshooting.md) or open a GitHub issue.
