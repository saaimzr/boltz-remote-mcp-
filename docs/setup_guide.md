# Boltz Remote MCP Server - Complete Setup Guide

This guide covers three deployment options for your Boltz MCP server, from easiest to most customizable.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Deployment Options Overview](#deployment-options-overview)
3. [Option 1: FastMCP Cloud (Recommended - Easiest)](#option-1-fastmcp-cloud-recommended---easiest)
4. [Option 2: Self-Hosted with Direct HTTP](#option-2-self-hosted-with-direct-http)
5. [Option 3: Self-Hosted with Reverse Proxy](#option-3-self-hosted-with-reverse-proxy)
6. [Testing Your Deployment](#testing-your-deployment)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### On Lab Computer (GPU Server)
- Python 3.10, 3.11, or 3.12 (⚠️ NOT 3.13+)
- CUDA-capable GPU with drivers installed
- ~10GB disk space for Boltz models
- Network access

### On Local Laptop
- Claude Desktop installed ([download here](https://claude.ai/download))
- Internet connection

---

## Deployment Options Overview

| Option | Ease of Setup | Best For | Pros | Cons |
|--------|---------------|----------|------|------|
| **FastMCP Cloud** | ⭐⭐⭐⭐⭐ Easiest | Quick deployment, testing | Automatic HTTPS, no network config | Requires GitHub repo, beta features |
| **Direct HTTP** | ⭐⭐⭐ Moderate | Lab servers with public IP | Simple, direct connection | Need to manage firewall, no HTTPS |
| **Reverse Proxy** | ⭐⭐ Advanced | Production deployments | HTTPS, auth, custom domain | More complex setup |

**Recommendation:** Start with FastMCP Cloud for fastest setup, then migrate to self-hosted if you need more control.

---

## Option 1: FastMCP Cloud (Recommended - Easiest)

FastMCP Cloud is the fastest way to deploy your server. It provides automatic deployment, HTTPS, and a public URL.

### Step 1: Prepare Your Repository

If you haven't already, push your code to GitHub:

```bash
# On your local machine or lab computer
cd boltz-remote-mcp

# Initialize git if needed
git init
git add .
git commit -m "Initial Boltz MCP server"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/boltz-remote-mcp.git
git push -u origin main
```

### Step 2: Deploy to FastMCP Cloud

1. Go to [https://cloud.fastmcp.com](https://cloud.fastmcp.com)
2. Sign in with your GitHub account
3. Click "New Project"
4. Select your `boltz-remote-mcp` repository
5. Configure project:
   - **Name:** `boltz-mcp` (or your choice)
   - **Server file:** `server/boltz_mcp_server.py`
   - **Requirements:** `server/requirements.txt`
6. Click "Deploy"

### Step 3: Wait for Build

FastMCP Cloud will:
- Clone your repository
- Install dependencies (including Boltz - this takes ~5-10 minutes)
- Start your server
- Provide a deployment URL

Your server will be available at: `https://your-project-name.fastmcp.app/mcp`

### Step 4: Configure Claude Desktop

On your local laptop:

**macOS:**
```bash
cd ~/Library/Application\ Support/Claude/
nano claude_desktop_config.json
```

**Windows:**
```powershell
cd $env:APPDATA\Claude
notepad claude_desktop_config.json
```

**Linux:**
```bash
cd ~/.config/Claude/
nano claude_desktop_config.json
```

Add this configuration:

```json
{
  "mcpServers": {
    "boltz-remote": {
      "url": "https://your-project-name.fastmcp.app/mcp"
    }
  }
}
```

Replace `your-project-name` with your actual FastMCP Cloud project name.

### Step 5: Restart Claude Desktop

Quit and relaunch Claude Desktop. You should see a 🔨 (hammer) icon indicating the server is connected.

**That's it!** Your Boltz server is now accessible from Claude Desktop.

---

## Option 2: Self-Hosted with Direct HTTP

This option runs the server directly on your lab computer. Best if your lab computer has a public IP or you're on the same network.

### Step 1: Transfer Files to Lab Computer

**Option A: Using Git**
```bash
# On lab computer
git clone https://github.com/YOUR_USERNAME/boltz-remote-mcp.git
cd boltz-remote-mcp/server
```

**Option B: Using SCP**
```bash
# On local machine
cd boltz-remote-mcp
scp -r server/ username@lab-computer:/home/username/boltz-mcp-server/
```

### Step 2: Setup Python Environment

```bash
# SSH into lab computer
ssh username@lab-computer
cd ~/boltz-mcp-server

# Check Python version (must be 3.10, 3.11, or 3.12)
python3 --version

# If Python 3.13+, use specific version
python3.12 --version  # Try 3.12
python3.11 --version  # Or 3.11
python3.10 --version  # Or 3.10

# Create virtual environment (use python3.12 if needed)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Boltz (takes 5-10 minutes)
pip install boltz[cuda] -U
```

### Step 3: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit configuration
nano .env
```

Update the following settings:

```bash
# Server Configuration
BOLTZ_TRANSPORT=http
BOLTZ_HOST=0.0.0.0
BOLTZ_PORT=8000

# GPU Configuration
CUDA_VISIBLE_DEVICES=0  # Adjust based on available GPUs

# Optional: Add authentication
# Generate token: python -c "import secrets; print(secrets.token_urlsafe(32))"
# BOLTZ_AUTH_TOKEN=your_secure_token_here
```

### Step 4: Configure Firewall

You need to open port 8000 for external access:

**If you have sudo access:**
```bash
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

**If you don't have sudo access:**
Ask your lab administrator to open port 8000.

### Step 5: Start the Server

```bash
# Load environment variables
source .env

# Start server
python boltz_mcp_server.py
```

You should see:
```
Starting Boltz MCP Server...
Upload directory: /home/username/.boltz_mcp/uploads
Output directory: /home/username/.boltz_mcp/outputs
Model cache directory: /home/username/.boltz_mcp/models

============================================================
Starting HTTP server on 0.0.0.0:8000
Server will be accessible at: http://0.0.0.0:8000/mcp/
============================================================
```

### Step 6: Keep Server Running

The server stops when you close SSH. Use `tmux` or `screen` to keep it running:

**Using tmux:**
```bash
# Start tmux session
tmux new -s boltz

# Run server
cd ~/boltz-mcp-server
source venv/bin/activate
python boltz_mcp_server.py

# Detach: Ctrl+B then D
# Reattach later: tmux attach -t boltz
```

**Using screen:**
```bash
# Start screen session
screen -S boltz

# Run server
cd ~/boltz-mcp-server
source venv/bin/activate
python boltz_mcp_server.py

# Detach: Ctrl+A then D
# Reattach later: screen -r boltz
```

### Step 7: Configure Claude Desktop

Get your lab computer's IP address:
```bash
# On lab computer
hostname -I
# Or
curl ifconfig.me
```

On your local laptop, edit Claude Desktop config:

```json
{
  "mcpServers": {
    "boltz-remote": {
      "url": "http://YOUR_LAB_IP:8000/mcp"
    }
  }
}
```

Replace `YOUR_LAB_IP` with your lab computer's actual IP address.

Restart Claude Desktop.

---

## Option 3: Self-Hosted with Reverse Proxy

This option adds a reverse proxy (nginx/caddy) for HTTPS and better security. **Advanced users only.**

### Prerequisites
- Domain name pointed to your server
- Server with sudo access
- Steps 1-3 from Option 2 completed

### Step 1: Install Caddy (Automatic HTTPS)

```bash
# Install Caddy
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

### Step 2: Configure Caddy

Create Caddyfile:

```bash
sudo nano /etc/caddy/Caddyfile
```

Add configuration:

```
boltz.yourdomain.com {
    reverse_proxy localhost:8000

    # Optional: Basic authentication
    # basicauth {
    #     username $2a$14$hashed_password
    # }
}
```

Replace `boltz.yourdomain.com` with your actual domain.

### Step 3: Start Services

```bash
# Reload Caddy
sudo systemctl reload caddy

# Start Boltz server (use systemd for production)
sudo nano /etc/systemd/system/boltz-mcp.service
```

Add systemd service file:

```ini
[Unit]
Description=Boltz MCP Server
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/boltz-mcp-server
Environment="PATH=/home/your_username/boltz-mcp-server/venv/bin"
EnvironmentFile=/home/your_username/boltz-mcp-server/.env
ExecStart=/home/your_username/boltz-mcp-server/venv/bin/python boltz_mcp_server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable boltz-mcp
sudo systemctl start boltz-mcp
sudo systemctl status boltz-mcp
```

### Step 4: Configure Claude Desktop

```json
{
  "mcpServers": {
    "boltz-remote": {
      "url": "https://boltz.yourdomain.com/mcp"
    }
  }
}
```

---

## Testing Your Deployment

Once Claude Desktop is configured and restarted:

### Test 1: Check Connection

In Claude Desktop:
```
Can you call the get_server_info tool from the Boltz server?
```

Expected: Server information including GPU details.

### Test 2: Simple Sequence Prediction

```
Can you predict the structure of this protein sequence:
MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL
```

This should:
1. Create a job
2. Return a job ID
3. Allow status checking
4. Eventually return a predicted structure

---

## Troubleshooting

### Server Won't Start

**Problem:** `ModuleNotFoundError: No module named 'fastmcp'`
```bash
pip install fastmcp>=2.0.0
```

**Problem:** `ModuleNotFoundError: No module named 'boltz'`
```bash
pip install boltz[cuda] -U
```

**Problem:** Python version incompatible
```bash
# Check version
python3 --version

# Use specific version
python3.12 -m venv venv
source venv/bin/activate
```

### Connection Issues

**Problem:** Claude Desktop can't connect

1. Check server is running:
   ```bash
   curl http://localhost:8000/mcp/
   ```

2. Check firewall allows port 8000

3. Verify IP address is correct

4. Try from same network first

### GPU Not Found

**Problem:** `nvidia-smi: command not found`

CUDA drivers not installed. Contact lab admin.

**Problem:** "No CUDA devices available"

```bash
# Check GPU visibility
echo $CUDA_VISIBLE_DEVICES

# Check nvidia-smi
nvidia-smi
```

### Performance Issues

**Problem:** Predictions too slow

Reduce parameters:
```python
recycling_steps=1    # Default: 3
sampling_steps=100   # Default: 200
```

**Problem:** Out of memory

Use smaller sequences or fewer GPUs:
```bash
CUDA_VISIBLE_DEVICES=0  # Use only 1 GPU
```

---

## Quick Reference

### Start Server (Self-Hosted)
```bash
cd ~/boltz-mcp-server
source venv/bin/activate
python boltz_mcp_server.py
```

### Stop Server
```bash
# If running in terminal: Ctrl+C

# If running in tmux/screen:
tmux attach -t boltz
# Then Ctrl+C

# Or kill process:
pkill -f boltz_mcp_server.py
```

### Update Server
```bash
cd ~/boltz-mcp-server
git pull
source venv/bin/activate
pip install -r requirements.txt --upgrade
```

### View Logs
```bash
# If using systemd:
sudo journalctl -u boltz-mcp -f

# If using tmux:
tmux attach -t boltz
```

### Generate Auth Token
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## Next Steps

- ✅ **Working?** See [Usage Examples](usage_examples.md) for workflows
- 🔒 **Need security?** Add authentication with bearer tokens
- 🚀 **Need scaling?** Consider containerization with Docker
- 📊 **Need monitoring?** Add logging and metrics

---

## Additional Resources

- [FastMCP Documentation](https://gofastmcp.com)
- [Boltz GitHub](https://github.com/jwohlwend/boltz)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Claude Desktop MCP Guide](https://docs.anthropic.com/claude/docs/mcp)

---

**Questions or issues?** Check [troubleshooting.md](troubleshooting.md) or open an issue on GitHub.
