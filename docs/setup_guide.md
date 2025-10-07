# Complete Setup Guide - Boltz Remote MCP

This guide provides step-by-step instructions for setting up the complete system: remote Boltz MCP server on your lab computer and Claude Desktop client on your local laptop.

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT WORKFLOW                      │
└─────────────────────────────────────────────────────────────┘

Step 1: Transfer files to lab computer
Step 2: Install dependencies on lab computer
Step 3: Configure ngrok
Step 4: Start MCP server on lab computer
Step 5: Configure Claude Desktop on local laptop
Step 6: Test the connection
```

## Part 1: Lab Computer Setup (Remote Server)

### Step 1.1: Transfer Server Files

From your local laptop, transfer the `server` directory to your lab computer.

**Option A: Using SCP (Secure Copy)**

```bash
# From your local laptop
cd boltz-remote-mcp
scp -r server/ username@lab-computer:/home/username/boltz-mcp-server/
```

**Option B: Using rsync**

```bash
# From your local laptop
cd boltz-remote-mcp
rsync -avz server/ username@lab-computer:/home/username/boltz-mcp-server/
```

**Option C: Using Git (if lab computer has internet)**

```bash
# On local laptop
cd boltz-remote-mcp
git init
git add .
git commit -m "Initial Boltz MCP server"
git push origin main

# On lab computer
git clone <your-repo-url> boltz-mcp-server
cd boltz-mcp-server/server
```

**Option D: Manual copy via USB/network drive**

1. Copy the entire `server` folder to a USB drive
2. Connect USB to lab computer
3. Copy to lab computer directory

### Step 1.2: SSH into Lab Computer

```bash
ssh username@lab-computer-hostname
cd ~/boltz-mcp-server
```

### Step 1.3: Install Python Dependencies

**No sudo required!** All installations will be in your user directory.

```bash
cd server

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install Boltz (this may take 5-10 minutes)
pip install git+https://github.com/jwohlwend/boltz.git
```

**Note:** Boltz installation will download ~3-5GB of dependencies including PyTorch, transformers, and scientific libraries.

### Step 1.4: Install ngrok (No Sudo Required)

```bash
# Download ngrok binary
cd ~/
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

# Extract (no sudo needed)
tar -xzf ngrok-v3-stable-linux-amd64.tgz

# Move to a directory in your PATH
mkdir -p ~/bin
mv ngrok ~/bin/

# Add to PATH (add this to ~/.bashrc or ~/.bash_profile)
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
ngrok version
```

### Step 1.5: Configure ngrok Authentication

1. **Sign up for ngrok account** (free): https://dashboard.ngrok.com/signup
2. **Get your auth token**: https://dashboard.ngrok.com/get-started/your-authtoken
3. **Configure ngrok:**

```bash
cd ~/boltz-mcp-server/server

# Create .env file
cp .env.example .env

# Edit .env file
nano .env  # or vim, emacs, etc.
```

4. **Add your ngrok token to .env:**

```bash
NGROK_AUTH_TOKEN=your_actual_token_here
CUDA_VISIBLE_DEVICES=0
```

Save and exit (Ctrl+X, then Y, then Enter in nano).

### Step 1.6: Verify GPU Access

```bash
# Check CUDA availability
nvidia-smi

# You should see your GPU(s) listed
# If you get "command not found", CUDA drivers may not be installed
# Contact your lab admin if GPUs aren't visible
```

### Step 1.7: Make Scripts Executable

```bash
chmod +x run_server.sh
chmod +x start_ngrok_tunnel.py
```

### Step 1.8: Test Boltz Installation

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Test Boltz CLI
boltz --help

# This should display Boltz help message
# If you get "command not found", Boltz installation failed
```

### Step 1.9: Start the MCP Server

**Option A: Using the bash script (recommended)**

```bash
./run_server.sh
```

**Option B: Manual startup**

```bash
# Activate virtual environment
source venv/bin/activate

# Start ngrok tunnel
python3 start_ngrok_tunnel.py &

# Wait a few seconds for tunnel to establish
sleep 3

# Get ngrok URL
cat ngrok_url.txt

# Start MCP server
python3 boltz_mcp_server.py
```

### Step 1.10: Copy the ngrok URL

After starting the server, you'll see output like:

```
[SUCCESS] ngrok tunnel established!
[SUCCESS] Public URL: tcp://0.tcp.ngrok.io:12345
```

**Copy this URL!** You'll need it for Claude Desktop configuration.

You can also retrieve it later:

```bash
cat ~/boltz-mcp-server/server/ngrok_url.txt
```

## Part 2: Local Laptop Setup (Claude Desktop Client)

### Step 2.1: Install Claude Desktop

Download and install Claude Desktop from: https://claude.ai/download

### Step 2.2: Locate Configuration Directory

**macOS:**
```bash
cd ~/Library/Application\ Support/Claude/
```

**Windows PowerShell:**
```powershell
cd $env:APPDATA\Claude
```

**Linux:**
```bash
cd ~/.config/Claude/
```

### Step 2.3: Create or Edit Configuration File

**macOS/Linux:**

```bash
# Navigate to config directory (see above)

# Backup existing config if present
if [ -f claude_desktop_config.json ]; then
    cp claude_desktop_config.json claude_desktop_config.json.backup
fi

# Create new config (replace YOUR_NGROK_URL with actual URL)
cat > claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "boltz-remote": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/client-stdio",
        "YOUR_NGROK_URL"
      ]
    }
  }
}
EOF
```

**Windows PowerShell:**

```powershell
# Navigate to config directory
cd $env:APPDATA\Claude

# Backup existing config
if (Test-Path claude_desktop_config.json) {
    Copy-Item claude_desktop_config.json claude_desktop_config.json.backup
}

# Create configuration object
$config = @{
    mcpServers = @{
        "boltz-remote" = @{
            command = "npx"
            args = @(
                "-y",
                "@modelcontextprotocol/client-stdio",
                "YOUR_NGROK_URL"
            )
        }
    }
} | ConvertTo-Json -Depth 10

# Save to file
$config | Out-File -FilePath claude_desktop_config.json -Encoding UTF8
```

**Replace `YOUR_NGROK_URL`** with the actual URL from Step 1.10!

Example:
```json
{
  "mcpServers": {
    "boltz-remote": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/client-stdio",
        "tcp://0.tcp.ngrok.io:12345"
      ]
    }
  }
}
```

### Step 2.4: Restart Claude Desktop

1. **Quit Claude Desktop completely** (not just close the window)
   - macOS: Cmd+Q or Claude menu → Quit
   - Windows: Right-click system tray icon → Exit
   - Linux: Close window or use quit menu
2. **Launch Claude Desktop again**

### Step 2.5: Verify Connection

Open Claude Desktop and try:

```
Can you call the get_server_info tool from the Boltz server?
```

If successful, you should see server information including GPU details!

## Part 3: Testing the System

### Test 1: Server Info

In Claude Desktop:
```
What information can you get about the Boltz server?
```

Expected response: GPU info, disk space, server version, etc.

### Test 2: Simple Protein Prediction (from sequence)

In Claude Desktop:
```
Can you predict the structure of this protein sequence:
MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL
```

This should:
1. Create a job
2. Return a job ID
3. Allow you to check status
4. Eventually return a predicted structure file

### Test 3: Upload PDB File

This requires a PDB file. You can download a test PDB:

```bash
# On local laptop
curl https://files.rcsb.org/download/1UBQ.pdb -o 1UBQ.pdb
```

Then in Claude Desktop:
```
I'm uploading a PDB file (1UBQ.pdb). Can you run a structure prediction on it?
```

## Troubleshooting

### Server Issues

**Problem: "NGROK_AUTH_TOKEN not set"**
- Solution: Check `.env` file exists and contains valid token
- Verify with: `cat ~/boltz-mcp-server/server/.env`

**Problem: "nvidia-smi not found"**
- Solution: CUDA drivers not installed or not in PATH
- Check with lab admin for GPU access
- Boltz requires CUDA-capable GPU

**Problem: "Boltz command not found"**
- Solution: Virtual environment not activated or Boltz not installed
- Activate venv: `source venv/bin/activate`
- Reinstall Boltz: `pip install git+https://github.com/jwohlwend/boltz.git`

**Problem: "Permission denied" when running scripts**
- Solution: Make scripts executable
- Run: `chmod +x run_server.sh start_ngrok_tunnel.py`

**Problem: ngrok tunnel fails to start**
- Solution: Check auth token is correct
- Verify network access (some networks block ngrok)
- Check ngrok.log for detailed errors

### Client Issues

**Problem: Claude Desktop doesn't see MCP server**
- Solution: Check config file location and JSON syntax
- Verify file is at correct path (see Step 2.2)
- Validate JSON at https://jsonlint.com

**Problem: "Connection timeout"**
- Solution:
  - Verify server is running on lab computer
  - Check ngrok URL is correct and still active
  - Test network connectivity: `curl -v https://ngrok.io`

**Problem: Tools not appearing in Claude Desktop**
- Solution:
  - Fully restart Claude Desktop (quit and relaunch)
  - Check server logs for errors
  - Try get_server_info tool first to verify connection

### Performance Issues

**Problem: Predictions taking too long**
- Adjust parameters:
  - Reduce `recycling_steps` (default: 3, min: 1)
  - Reduce `sampling_steps` (default: 200, min: 50)
- Check GPU utilization: `nvidia-smi` on server

**Problem: Out of memory errors**
- Use fewer GPUs or smaller sequences
- Close other GPU-intensive processes
- Contact lab admin for more GPU resources

## Keeping Server Running

The server runs in your SSH session. If you disconnect, it will stop.

**Option 1: Use tmux (recommended)**

```bash
# Install tmux (if not already installed)
# No sudo? Ask lab admin or use alternative methods

# Start tmux session
tmux new -s boltz-server

# Run server
cd ~/boltz-mcp-server/server
./run_server.sh

# Detach from session: Ctrl+B then D
# Server keeps running!

# Reattach later:
tmux attach -t boltz-server
```

**Option 2: Use screen**

```bash
# Start screen session
screen -S boltz-server

# Run server
cd ~/boltz-mcp-server/server
./run_server.sh

# Detach: Ctrl+A then D

# Reattach later:
screen -r boltz-server
```

**Option 3: Use nohup**

```bash
# Run in background
nohup ./run_server.sh > server.log 2>&1 &

# Server runs even after disconnecting

# Stop later:
pkill -f boltz_mcp_server.py
```

## Updating ngrok URL

**Free ngrok tier:** URL changes each restart.

When you restart the server:

1. Get new URL from server: `cat ngrok_url.txt`
2. Update Claude Desktop config (Step 2.3)
3. Restart Claude Desktop

**Pro tip:** Upgrade to ngrok Pro for persistent URLs.

## Security Best Practices

1. **Don't share ngrok URLs publicly** - they provide direct access to your server
2. **Monitor server logs** - watch for unexpected access
3. **Use strong lab computer password** - ngrok URL + server together = full access
4. **Consider ngrok authentication** - add password protection to tunnel
5. **Keep software updated** - regularly update Python packages and Boltz

## Next Steps

- See `usage_examples.md` for detailed workflow examples
- See `troubleshooting.md` for common issues
- Join the MCP community for support

## Quick Reference

**Start server on lab computer:**
```bash
cd ~/boltz-mcp-server/server
source venv/bin/activate
./run_server.sh
```

**Stop server:**
```bash
Ctrl+C
# Or if running in background:
pkill -f boltz_mcp_server.py
```

**Get ngrok URL:**
```bash
cat ~/boltz-mcp-server/server/ngrok_url.txt
```

**View server logs:**
```bash
tail -f ~/boltz-mcp-server/server/ngrok.log
```

**Claude Desktop config location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`
