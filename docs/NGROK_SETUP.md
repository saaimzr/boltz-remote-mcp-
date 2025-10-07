# Boltz MCP Server with ngrok - Complete Setup Guide

**Best solution for remote access without sudo privileges.**

---

## Why ngrok?

If you don't have sudo/admin access on your lab computer, ngrok is the **best** solution because:

✅ **No sudo required** - Runs entirely in userspace
✅ **No firewall changes** - Works through existing network
✅ **Automatic HTTPS** - Secure by default
✅ **Always accessible** - Works even when your laptop is off
✅ **Simple setup** - Just one command: `ngrok http 8000`

---

## Architecture

```
┌─────────────────┐         ┌──────────────┐         ┌────────────────────┐
│  YOUR LAPTOP    │ HTTPS   │    ngrok     │  HTTP   │  LAB COMPUTER      │
│  (Windows)      │ ◄─────► │   Tunnel     │ ◄─────► │  (Linux/GPU)       │
│                 │         │              │         │                    │
│ Claude Desktop  │         │ Public URL   │         │ Boltz MCP Server   │
│                 │         │ (HTTPS)      │         │ localhost:8000     │
└─────────────────┘         └──────────────┘         └────────────────────┘
```

**Key insight:** ngrok creates a secure tunnel from a public URL to your localhost:8000, bypassing all firewall issues.

---

## PART 1: Lab Computer Setup

**Context:** All commands in this section run on your **lab computer** (via SSH).

### Step 1.1: SSH into Lab Computer

```bash
# From your Windows laptop, open PowerShell
ssh yourusername@lab-computer-hostname

# You should see a prompt like:
# yourusername@lab-computer:~$
```

### Step 1.2: Verify You Have the Project Files

```bash
# Check if you already have the project
cd ~/boltz-remote-mcp/server
ls

# You should see:
# boltz_mcp_server.py  requirements.txt  .env.example  venv/

# If you don't have these files, clone the repo:
cd ~
git clone https://github.com/YOUR_USERNAME/boltz-remote-mcp.git
cd boltz-remote-mcp/server
```

### Step 1.3: Verify Python Environment

**Important:** You mentioned you already have a venv with boltz installed. Let's verify it works:

```bash
# On lab computer
cd ~/boltz-remote-mcp/server

# Activate your existing venv
source venv/bin/activate

# Your prompt should show (venv)
# (venv) yourusername@lab-computer:~/boltz-remote-mcp/server$

# Verify Python version (must be 3.10-3.12)
python --version
# Should show: Python 3.10.x, 3.11.x, or 3.12.x

# Verify FastMCP is installed
pip show fastmcp
# If not installed or version is <2.0:
pip install fastmcp>=2.0.0 --upgrade

# Verify Boltz is installed
boltz --help
# Should show Boltz help message

# If boltz is not found:
pip install boltz[cuda] -U
```

### Step 1.4: Install ngrok (No Sudo Required)

```bash
# On lab computer (via SSH)
cd ~

# Download ngrok (no sudo needed)
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

# Extract it
tar -xzf ngrok-v3-stable-linux-amd64.tgz

# Create a bin directory in your home folder
mkdir -p ~/bin

# Move ngrok to your bin directory
mv ngrok ~/bin/

# Add ~/bin to your PATH
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc

# Reload your shell configuration
source ~/.bashrc

# Verify ngrok is installed
ngrok version
# Should show: ngrok version 3.x.x
```

### Step 1.5: Configure ngrok Authentication

```bash
# On lab computer (via SSH)

# Go to https://dashboard.ngrok.com/signup and sign up (free)
# After signup, go to: https://dashboard.ngrok.com/get-started/your-authtoken
# Copy your authtoken (looks like: 2abc123def456ghi789jkl...)

# Configure ngrok with your token
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE

# Example:
# ngrok config add-authtoken 2abc123def456ghi789jkl0mnop1qrst

# Verify configuration
cat ~/.config/ngrok/ngrok.yml
# Should show your authtoken
```

### Step 1.6: Configure Environment Variables

```bash
# On lab computer
cd ~/boltz-remote-mcp/server

# Create .env file if it doesn't exist
cp .env.example .env

# Edit configuration
nano .env

# Set these values:
# BOLTZ_TRANSPORT=http
# BOLTZ_HOST=127.0.0.1
# BOLTZ_PORT=8000
# CUDA_VISIBLE_DEVICES=0

# Save and exit (Ctrl+X, then Y, then Enter)

# Verify
cat .env
```

### Step 1.7: Test the Server (Without ngrok)

```bash
# On lab computer (via SSH, with venv activated)
cd ~/boltz-remote-mcp/server
source venv/bin/activate

# Start the server
python boltz_mcp_server.py

# You should see:
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

# If you see this, great! Server works.

# Stop the server: Press Ctrl+C
```

---

## PART 2: Running with ngrok

### Step 2.1: Start ngrok in a Separate Terminal

**Important:** You need TWO terminal sessions - one for the server, one for ngrok.

**Terminal 1 (Server):**
```bash
# SSH to lab computer
ssh yourusername@lab-computer-hostname

# Start tmux session for the server
tmux new -s boltz-server

# Activate venv and start server
cd ~/boltz-remote-mcp/server
source venv/bin/activate
python boltz_mcp_server.py

# Server is now running
# Detach from tmux: Press Ctrl+B, then press D
```

**Terminal 2 (ngrok):**
```bash
# Open NEW SSH session to lab computer
ssh yourusername@lab-computer-hostname

# Start tmux session for ngrok
tmux new -s ngrok-tunnel

# Start ngrok tunnel to port 8000
ngrok http 8000

# You should see:
# ngrok
#
# Session Status                online
# Account                       your-email@example.com (Plan: Free)
# Version                       3.x.x
# Region                        United States (us)
# Latency                       20ms
# Web Interface                 http://127.0.0.1:4040
# Forwarding                    https://abc123def456.ngrok-free.app -> http://localhost:8000
#
# Connections                   ttl     opn     rt1     rt5     p50     p90
#                               0       0       0.00    0.00    0.00    0.00

# IMPORTANT: Copy the "Forwarding" URL!
# Example: https://abc123def456.ngrok-free.app

# Detach from tmux: Press Ctrl+B, then press D
```

### Step 2.2: Save the ngrok URL

```bash
# The ngrok URL looks like:
# https://abc123def456.ngrok-free.app

# This is your public URL!
# Save it - you'll need it for Claude Desktop configuration

# You can always see it again:
curl http://localhost:4040/api/tunnels | grep public_url

# Or reattach to the ngrok tmux session:
tmux attach -t ngrok-tunnel
```

### Step 2.3: Verify ngrok Tunnel Works

```bash
# From your Windows laptop (PowerShell)
# Test the ngrok URL
curl https://abc123def456.ngrok-free.app/mcp/

# Or open in browser:
start https://abc123def456.ngrok-free.app/mcp/

# You should see a JSON response
# This confirms the tunnel is working!
```

---

## PART 3: Configure Claude Desktop

**Context:** These steps run on YOUR LAPTOP (Windows).

### Step 3.1: Edit Claude Desktop Configuration

```powershell
# On YOUR LAPTOP (Windows PowerShell)

# Navigate to Claude config directory
cd $env:APPDATA\Claude

# Check if config exists
ls claude_desktop_config.json

# If not, create it:
New-Item -Path claude_desktop_config.json -ItemType File

# Edit the file
notepad claude_desktop_config.json
```

### Step 3.2: Add Configuration

Add this to the file (replace with YOUR ngrok URL):

```json
{
  "mcpServers": {
    "boltz-remote": {
      "url": "https://abc123def456.ngrok-free.app/mcp"
    }
  }
}
```

**Important:**
- Use YOUR actual ngrok URL (from Step 2.1)
- Make sure it starts with `https://`
- Make sure it ends with `/mcp`

Save and close the file.

### Step 3.3: Restart Claude Desktop

```powershell
# Close Claude Desktop completely
# 1. Close all windows
# 2. Check system tray (bottom-right)
# 3. Right-click Claude icon if present -> Quit

# Or use Task Manager:
# Press Ctrl+Shift+Esc
# Find "Claude" process
# Right-click -> End Task

# Wait 5 seconds

# Restart Claude Desktop
# Click Claude icon or search in Start menu
```

---

## PART 4: Testing

### Step 4.1: Verify Connection

1. Open Claude Desktop
2. Look for 🔨 (hammer) icon - indicates MCP server connected
3. Start a new conversation

Type:
```
Can you use the get_server_info tool?
```

**Expected:** Claude calls the tool and returns:
- Server version
- GPU information
- Disk space
- Active jobs

If this works: **SUCCESS!** 🎉

### Step 4.2: Test Protein Prediction

Type in Claude:
```
Can you predict the structure of this protein sequence:

MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL
```

Claude will:
1. Call `predict_structure_from_sequence`
2. Return a job_id
3. Periodically check status
4. Eventually return the predicted structure (CIF file)

**Note:** First prediction downloads model weights (~3GB), takes 10-20 minutes.

---

## PART 5: Daily Usage Workflow

### Starting Everything

```bash
# On lab computer (via SSH)

# Reattach to server tmux session
tmux attach -t boltz-server
# Server should still be running
# If not, start it:
cd ~/boltz-remote-mcp/server
source venv/bin/activate
python boltz_mcp_server.py

# Detach: Ctrl+B then D

# Reattach to ngrok tmux session
tmux attach -t ngrok-tunnel
# ngrok should still be running
# If not, start it:
ngrok http 8000

# Detach: Ctrl+B then D
```

### Checking Status

```bash
# Check if server is running
tmux attach -t boltz-server

# Check if ngrok is running
tmux attach -t ngrok-tunnel

# Check ngrok URL
curl http://localhost:4040/api/tunnels
```

### Stopping Everything

```bash
# Stop server
tmux attach -t boltz-server
# Press Ctrl+C
exit

# Stop ngrok
tmux attach -t ngrok-tunnel
# Press Ctrl+C
exit
```

---

## PART 6: Keeping It Running Permanently

### Option A: Use tmux (Already Setup Above)

✅ Already done if you followed Part 2!

tmux keeps sessions running even when you disconnect SSH.

### Option B: Use systemd User Service (No Sudo)

Create user service files:

**Server service:**
```bash
mkdir -p ~/.config/systemd/user
nano ~/.config/systemd/user/boltz-server.service
```

Add:
```ini
[Unit]
Description=Boltz MCP Server
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/yourusername/boltz-remote-mcp/server
Environment="PATH=/home/yourusername/boltz-remote-mcp/server/venv/bin"
EnvironmentFile=/home/yourusername/boltz-remote-mcp/server/.env
ExecStart=/home/yourusername/boltz-remote-mcp/server/venv/bin/python boltz_mcp_server.py
Restart=always

[Install]
WantedBy=default.target
```

**ngrok service:**
```bash
nano ~/.config/systemd/user/ngrok-tunnel.service
```

Add:
```ini
[Unit]
Description=ngrok Tunnel
After=network.target

[Service]
Type=simple
ExecStart=/home/yourusername/bin/ngrok http 8000
Restart=always
RestartSec=10

[Install]
WantedBy=default.target
```

**Enable and start:**
```bash
# Reload systemd user daemon
systemctl --user daemon-reload

# Enable services (start on boot)
systemctl --user enable boltz-server
systemctl --user enable ngrok-tunnel

# Start services
systemctl --user start boltz-server
systemctl --user start ngrok-tunnel

# Check status
systemctl --user status boltz-server
systemctl --user status ngrok-tunnel

# View logs
journalctl --user -u boltz-server -f
journalctl --user -u ngrok-tunnel -f
```

---

## Troubleshooting

### ngrok URL Changes

**Problem:** Free ngrok URLs change every restart

**Solutions:**
1. **Paid ngrok plan** ($8/month) - Get static URLs
2. **Update Claude config** - Update URL each restart
3. **Webhook/script** - Auto-update Claude config when URL changes

### ngrok Connection Refused

**Check 1: Is server running?**
```bash
tmux attach -t boltz-server
# Should see server logs
```

**Check 2: Is ngrok pointing to right port?**
```bash
tmux attach -t ngrok-tunnel
# Should show: Forwarding ... -> http://localhost:8000
```

**Check 3: Test locally**
```bash
curl http://localhost:8000/mcp/
# Should return JSON
```

### Claude Can't Connect

**Check 1: Correct URL in config?**
```powershell
cat $env:APPDATA\Claude\claude_desktop_config.json
```

**Check 2: URL format**
- ✅ `https://abc123.ngrok-free.app/mcp`
- ❌ `https://abc123.ngrok-free.app` (missing /mcp)
- ❌ `http://abc123.ngrok-free.app/mcp` (http not https)

**Check 3: Test URL in browser**
```powershell
start https://your-url.ngrok-free.app/mcp/
# Should show JSON response
```

**Check 4: Restart Claude Desktop**
- Fully quit (check system tray)
- Restart

### GPU Out of Memory

```bash
# On lab computer, check GPU usage
nvidia-smi

# If memory is full, reduce parameters in prediction:
# - recycling_steps: 3 -> 1
# - sampling_steps: 200 -> 100
```

### Server Crashes

```bash
# Check server logs
tmux attach -t boltz-server

# Or if using systemd:
journalctl --user -u boltz-server -n 100
```

---

## Summary

**What you set up:**
1. ✅ Boltz MCP Server running on lab computer
2. ✅ ngrok tunnel exposing server publicly
3. ✅ Claude Desktop connected via ngrok URL
4. ✅ Everything runs without sudo

**Benefits:**
- Works from anywhere (internet required)
- No laptop needed (runs on lab computer)
- Automatic HTTPS
- No firewall configuration

**Costs:**
- ngrok free tier: Free (URL changes on restart)
- ngrok paid: $8/month (static URLs)

**Next steps:**
- Try protein structure predictions
- Set up systemd services for auto-start
- Consider upgrading ngrok for static URLs

---

## Quick Reference

**Start everything:**
```bash
tmux attach -t boltz-server  # Verify server running
tmux attach -t ngrok-tunnel  # Get ngrok URL
```

**Get ngrok URL:**
```bash
curl http://localhost:4040/api/tunnels | grep public_url
```

**Update Claude config:**
```powershell
notepad $env:APPDATA\Claude\claude_desktop_config.json
```

**Check logs:**
```bash
tmux attach -t boltz-server  # Server logs
tmux attach -t ngrok-tunnel  # ngrok logs
```

---

**Questions?** See [troubleshooting.md](troubleshooting.md) or open a GitHub issue.
