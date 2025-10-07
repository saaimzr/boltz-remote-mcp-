# Troubleshooting Guide

Common issues and solutions for the Boltz Remote MCP system.

## Table of Contents

1. [Server Issues](#server-issues)
2. [Client Issues](#client-issues)
3. [Network Issues](#network-issues)
4. [Performance Issues](#performance-issues)
5. [Boltz-Specific Issues](#boltz-specific-issues)
6. [Advanced Debugging](#advanced-debugging)

---

## Server Issues

### "NGROK_AUTH_TOKEN not set"

**Problem:** Server startup fails with auth token error.

**Solution:**
```bash
# Check if .env file exists
cd ~/boltz-mcp-server/server
ls -la .env

# If missing, create from example
cp .env.example .env

# Edit and add your token
nano .env
# Add: NGROK_AUTH_TOKEN=your_actual_token_here

# Get token from: https://dashboard.ngrok.com/get-started/your-authtoken
```

### "Command 'boltz' not found"

**Problem:** Boltz CLI not installed or not in PATH.

**Solution:**
```bash
# Activate virtual environment
cd ~/boltz-mcp-server/server
source venv/bin/activate

# Check if boltz is installed
pip list | grep boltz

# If not found, install
pip install git+https://github.com/jwohlwend/boltz.git

# Verify
boltz --help
```

### "nvidia-smi: command not found"

**Problem:** CUDA drivers not installed or not in PATH.

**Diagnosis:**
- GPU drivers missing
- PATH not configured correctly
- No GPU on system

**Solutions:**

**Check if GPUs exist:**
```bash
lspci | grep -i nvidia
```

**If GPUs exist but nvidia-smi missing:**
```bash
# Check if drivers installed
ls /usr/lib/nvidia-*

# Add to PATH (temporary)
export PATH="/usr/lib/nvidia-current/bin:$PATH"

# Permanent fix: ask lab admin to configure PATH
```

**No sudo access?**
- Contact lab administrator
- Boltz requires CUDA-capable GPU
- Cannot install drivers without sudo

### "Permission denied" errors

**Problem:** Cannot execute scripts or access directories.

**Solutions:**

**For script execution:**
```bash
chmod +x run_server.sh
chmod +x start_ngrok_tunnel.py
```

**For directory access:**
```bash
# Check permissions
ls -la ~/boltz-mcp-server/server/

# Fix ownership (if needed and allowed)
# This should work without sudo for your own files
chmod -R u+rw ~/boltz-mcp-server/
```

**For system directories (need sudo):**
- Contact lab admin
- Use alternative directories in your home folder

### "Port 8000 already in use"

**Problem:** Another process is using the MCP server port.

**Solutions:**

**Find what's using the port:**
```bash
# Without sudo
lsof -i :8000  # may not work without sudo

# Alternative: check your own processes
ps aux | grep python
ps aux | grep ngrok
```

**Kill the conflicting process:**
```bash
# If you started it
pkill -f boltz_mcp_server.py
pkill -f ngrok

# Or find PID and kill
ps aux | grep python
kill <PID>
```

**Use a different port:**
```bash
# Edit boltz_mcp_server.py
# Change MCP_SERVER_PORT = 8000 to another port
# Also update ngrok tunnel configuration
```

### "Out of disk space"

**Problem:** No space left for model cache or outputs.

**Diagnosis:**
```bash
# Check disk usage
df -h ~

# Check Boltz directories
du -sh ~/.boltz_mcp/
du -sh ~/.cache/boltz/
```

**Solutions:**

**Clean old outputs:**
```bash
cd ~/.boltz_mcp/outputs/
ls -lt  # list by time
rm -rf old_job_id_here  # remove old predictions
```

**Clean model cache (will re-download):**
```bash
# This is safe - models will re-download on next use
rm -rf ~/.cache/boltz/
```

**Move cache to larger disk:**
```bash
# If you have access to a larger disk
mkdir /path/to/large/disk/boltz_cache
ln -s /path/to/large/disk/boltz_cache ~/.cache/boltz
```

### "ModuleNotFoundError: No module named 'mcp'"

**Problem:** FastMCP not installed or wrong Python environment.

**Solutions:**

**Check Python environment:**
```bash
# Make sure venv is activated
which python
# Should show: /home/user/boltz-mcp-server/server/venv/bin/python

# If not, activate
source ~/boltz-mcp-server/server/venv/bin/activate
```

**Reinstall dependencies:**
```bash
pip install -r requirements.txt
```

### Server crashes on startup

**Problem:** Server starts then immediately crashes.

**Diagnosis:**
```bash
# Run server with verbose output
python3 -u boltz_mcp_server.py 2>&1 | tee server_debug.log

# Check for error messages
```

**Common causes:**

**Import errors:**
```bash
# Install missing dependencies
pip install fastmcp python-dotenv pyngrok
```

**Path errors:**
```bash
# Check directory permissions
ls -la ~/.boltz_mcp/
mkdir -p ~/.boltz_mcp/{uploads,outputs,models}
```

**GPU errors:**
```bash
# Check CUDA availability
python3 -c "import torch; print(torch.cuda.is_available())"
```

---

## Client Issues

### Claude Desktop doesn't see MCP server

**Problem:** No Boltz tools appear in Claude Desktop.

**Diagnosis checklist:**

1. **Config file location correct?**
   ```bash
   # macOS
   ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # Linux
   ls -la ~/.config/Claude/claude_desktop_config.json

   # Windows
   dir %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **JSON syntax valid?**
   - Copy config content
   - Paste into https://jsonlint.com
   - Fix any errors

3. **ngrok URL correct?**
   - Should start with `tcp://`
   - Should include port number
   - Example: `tcp://0.tcp.ngrok.io:12345`

4. **Claude Desktop fully restarted?**
   - Don't just close window - fully quit
   - macOS: Cmd+Q
   - Windows: System tray → Exit

**Solutions:**

**Verify config format:**
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

**Common JSON errors:**
- Missing comma between fields
- Extra comma after last field
- Mismatched brackets
- Using single quotes instead of double quotes

**Check Claude Desktop logs:**
```bash
# macOS
tail -f ~/Library/Logs/Claude/main.log

# Linux
tail -f ~/.config/Claude/logs/main.log

# Windows
type %APPDATA%\Claude\logs\main.log
```

### "Connection timeout" when using tools

**Problem:** Tools appear but timeout when called.

**Diagnosis:**

**Check server is running:**
```bash
# SSH to lab computer
ssh user@lab-computer

# Check process
ps aux | grep boltz_mcp_server.py

# Should show running Python process
```

**Check ngrok tunnel:**
```bash
# On lab computer
cat ~/boltz-mcp-server/server/ngrok_url.txt

# Verify this matches URL in Claude Desktop config
```

**Test network connectivity:**
```bash
# From local laptop
curl -v tcp://your-ngrok-url:port
```

**Solutions:**

**Server not running:** Restart server
**ngrok URL changed:** Update Claude Desktop config
**Network blocking ngrok:** Use VPN or different network

### MCP client fails to start

**Problem:** Error about npx or @modelcontextprotocol/client-stdio.

**Diagnosis:**
```bash
# Check if Node.js/npm installed
node --version
npm --version
```

**Solutions:**

**If Node.js missing:**
- Install from https://nodejs.org
- Or use alternative MCP client

**If npx fails:**
```bash
# Install MCP client globally
npm install -g @modelcontextprotocol/client-stdio

# Then use 'mcp-client-stdio' instead of npx in config
```

---

## Network Issues

### ngrok tunnel won't start

**Problem:** "Failed to start tunnel" error.

**Diagnosis:**

**Check auth token:**
```bash
# Verify token is set
echo $NGROK_AUTH_TOKEN

# Or check .env file
cat ~/boltz-mcp-server/server/.env
```

**Check ngrok process:**
```bash
ps aux | grep ngrok
```

**Check ngrok logs:**
```bash
cat ~/boltz-mcp-server/server/ngrok.log
```

**Common errors in logs:**

**"Invalid auth token":**
```bash
# Get new token from dashboard
# Update .env file
nano ~/boltz-mcp-server/server/.env
```

**"Account limit exceeded":**
- Free ngrok tier has limits (e.g., 1 tunnel at a time)
- Close other ngrok tunnels
- Upgrade to paid plan

**"Connection refused":**
- Network firewall blocking ngrok
- Try different network
- Contact network admin

### ngrok tunnel URL changes on restart

**Problem:** Every server restart gives new URL.

**Explanation:** This is normal on ngrok free tier.

**Solutions:**

**Option 1: Update config each time**
```bash
# On lab computer
cat ~/boltz-mcp-server/server/ngrok_url.txt

# Copy new URL

# On local laptop
# Edit claude_desktop_config.json with new URL
# Restart Claude Desktop
```

**Option 2: Upgrade to ngrok Pro**
- Get persistent URL that doesn't change
- Worth it if you use system regularly
- ~$8/month

**Option 3: Use SSH tunnel instead**
- No ngrok needed
- See "Alternative: SSH Tunnel" section below

### Cannot access lab computer

**Problem:** SSH connection fails.

**Diagnosis:**

**Check network connectivity:**
```bash
ping lab-computer-hostname
```

**Check SSH service:**
```bash
# If you can access physically
ssh localhost  # from lab computer

# Check if SSH running
ps aux | grep sshd
```

**Common issues:**

**Wrong hostname/IP:**
- Verify with lab admin
- Try IP address instead of hostname

**SSH key authentication:**
```bash
# Check if key-based auth required
ssh -v user@lab-computer

# Add your SSH key
ssh-copy-id user@lab-computer
```

**VPN required:**
- Some labs require VPN for SSH access
- Connect to VPN first

### Corporate firewall blocks ngrok

**Problem:** Company/university network blocks ngrok domains.

**Diagnosis:**
```bash
# Test ngrok connectivity
curl -v https://ngrok.io
curl -v https://api.ngrok.com

# If fails, network is blocking
```

**Solutions:**

**Use different network:**
- Mobile hotspot
- Home network
- VPN

**Use SSH tunnel (see below)**

**Request firewall exception:**
- Contact IT department
- Explain legitimate research use

---

## Performance Issues

### Predictions take too long

**Problem:** Structure prediction exceeds expected time.

**Diagnosis:**

**Check GPU usage:**
```bash
# On lab computer
nvidia-smi

# Should show:
# - GPU utilization > 90%
# - Memory usage increasing
# - boltz process listed
```

**Check system load:**
```bash
top
htop  # if available

# Look for CPU bottlenecks
```

**Check parameters:**
- Higher recycling_steps = longer time
- Higher sampling_steps = longer time
- Longer sequences = exponentially longer

**Expected times:**
- Short protein (<100 AA): 5-15 min
- Medium protein (100-300 AA): 15-45 min
- Long protein (>300 AA): 45+ min
- Large complex: hours

**Solutions:**

**Reduce quality for testing:**
```python
# In Claude Desktop
"Use faster parameters:
- recycling_steps: 1
- sampling_steps: 100"
```

**Use more GPUs:**
```python
# If multiple GPUs available
"Use GPUs 0,1 for prediction"
```

**Run overnight:**
```bash
# On lab computer, use tmux/screen
tmux new -s overnight-predictions
# Start server, submit jobs
# Detach with Ctrl+B, D
# Server keeps running
```

### Out of memory (OOM) errors

**Problem:** "CUDA out of memory" error during prediction.

**Diagnosis:**
```bash
# Check GPU memory
nvidia-smi

# Look at memory usage:
# - Total memory
# - Used memory
# - Available memory
```

**Solutions:**

**Use fewer GPUs:**
```python
# Sometimes using 1 GPU is more stable than multiple
devices: "0"
```

**Reduce batch size/parameters:**
```python
# Reduce memory usage
sampling_steps: 100  # instead of 200
```

**Close other GPU processes:**
```bash
# Check what's using GPU
nvidia-smi

# Kill unnecessary processes
kill <PID>
```

**Split large complexes:**
- Predict chains individually
- Dock separately

**Upgrade GPU:**
- Contact lab admin for more VRAM

### Slow file uploads

**Problem:** Large PDB files timeout during upload.

**Diagnosis:**
- Check file size
- Check network speed

**Solutions:**

**Compress files:**
```bash
gzip large_file.pdb
# Upload compressed version
```

**Increase timeout:**
- Edit MCP client timeout settings
- Or split into smaller jobs

**Alternative: Upload directly to server:**
```bash
# SCP file to server
scp large_file.pdb user@lab:/home/user/uploads/

# Then reference by filename
```

---

## Boltz-Specific Issues

### "Boltz model download failed"

**Problem:** First run fails to download models.

**Diagnosis:**
```bash
# Check model cache
ls ~/.cache/boltz/

# Check disk space
df -h ~

# Check internet connectivity
ping github.com
```

**Solutions:**

**Retry:**
- Models are large (~5GB)
- May timeout on slow connections
- Simply retry

**Manual download:**
```bash
# Clone Boltz repo
git clone https://github.com/jwohlwend/boltz.git
cd boltz

# Follow installation instructions
# Models will download during setup
```

**Use different cache directory:**
```bash
# If home directory has space issues
export BOLTZ_CACHE=/path/to/large/disk
```

### "Invalid sequence format"

**Problem:** Boltz rejects input sequence.

**Common causes:**

**Non-standard amino acids:**
```
# Invalid: contains X (unknown)
MKTAXIAKQR

# Solution: replace or remove X
MKTAAIAKQR
```

**Whitespace/formatting:**
```
# Invalid: has spaces
MKTA YIAK QRQI

# Solution: remove spaces
MKTAYIAKQRQI
```

**Non-protein characters:**
```
# Invalid: has numbers from alignment
1 MKTAYIAK 10

# Solution: clean sequence
MKTAYIAK
```

**Solutions:**

**Clean sequence:**
```python
# Remove non-amino acid characters
sequence = "".join(c for c in sequence if c in "ACDEFGHIKLMNPQRSTVWY")
```

**Use FASTA format:**
```
>protein_name
MKTAYIAKQRQISFVK
SHFSRQLEERLGLIE
```

### Prediction produces poor quality structure

**Problem:** Output structure looks wrong.

**Diagnosis:**

**Check confidence scores:**
- Boltz outputs confidence metrics
- Low confidence = unreliable prediction

**Compare with other tools:**
- AlphaFold2/3
- ESMFold
- RoseTTAFold

**Possible causes:**

**Sequence too short:**
- Need >30 AA for reliable prediction
- Very short peptides difficult to predict

**Sequence errors:**
- Check for typos
- Verify sequence is correct

**Intrinsically disordered:**
- Some proteins lack stable structure
- Prediction won't converge

**Solutions:**

**Increase quality parameters:**
```python
recycling_steps: 10
sampling_steps: 500
```

**Try multiple samples:**
```python
diffusion_samples: 5  # generate 5 different predictions
```

**Check input:**
- Verify sequence from database
- Check for sequencing errors

---

## Advanced Debugging

### Enable debug logging

**Server side:**
```bash
# Edit boltz_mcp_server.py
# Add at top of file:
import logging
logging.basicConfig(level=logging.DEBUG)

# Or set in .env
LOG_LEVEL=DEBUG
```

**Client side:**
```json
{
  "mcpServers": {
    "boltz-remote": {
      "command": "npx",
      "args": [...],
      "env": {
        "MCP_LOG_LEVEL": "debug"
      }
    }
  }
}
```

### Capture network traffic

```bash
# On server, monitor ngrok traffic
tail -f ~/boltz-mcp-server/server/ngrok.log

# Check ngrok dashboard
# https://dashboard.ngrok.com/observability/events
```

### Test server directly

```bash
# Bypass Claude Desktop, test server directly
cd ~/boltz-mcp-server/server
source venv/bin/activate

# Start Python interpreter
python3

# Import and test
from boltz_mcp_server import *
result = await get_server_info()
print(result)
```

### Verify Boltz installation

```bash
# Test Boltz directly
cd ~/boltz-mcp-server/server
source venv/bin/activate

# Create test FASTA
cat > test.fasta << EOF
>test
MKTAYIAKQRQISFVKSHFSRQ
EOF

# Run Boltz directly
boltz predict test.fasta --out_dir test_output --devices 0

# If this works, Boltz is fine
# If fails, problem is with Boltz installation
```

### Check MCP protocol communication

```bash
# Enable MCP protocol debugging
# See raw MCP messages

# In Claude Desktop config
{
  "mcpServers": {
    "boltz-remote": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/client-stdio",
        "--debug",
        "tcp://..."
      ]
    }
  }
}
```

---

## Getting Help

### Information to collect before asking for help

1. **System information:**
```bash
# OS and Python version
uname -a
python3 --version

# GPU information
nvidia-smi

# Disk space
df -h
```

2. **Installation details:**
```bash
# Boltz version
pip show boltz

# Dependencies
pip list
```

3. **Error messages:**
```bash
# Server logs
cat ~/boltz-mcp-server/server/ngrok.log

# Claude Desktop logs
# (see Client Issues section for locations)
```

4. **Configuration:**
```bash
# MCP config (remove sensitive tokens!)
cat claude_desktop_config.json
```

### Where to get help

- **Boltz issues:** https://github.com/jwohlwend/boltz/issues
- **MCP issues:** https://github.com/modelcontextprotocol/
- **ngrok issues:** https://ngrok.com/docs
- **FastMCP issues:** https://gofastmcp.com/

### Community support

- MCP Discord
- Boltz discussions
- Computational biology forums

---

## Alternative: SSH Tunnel (Instead of ngrok)

If ngrok doesn't work, use SSH tunneling:

**Setup:**

```bash
# From local laptop
ssh -L 8000:localhost:8000 user@lab-computer

# Keep this terminal open
```

**Claude Desktop config:**
```json
{
  "mcpServers": {
    "boltz-remote": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/client-stdio",
        "tcp://localhost:8000"
      ]
    }
  }
}
```

**Advantages:**
- No ngrok needed
- No third-party service
- More secure

**Disadvantages:**
- Requires SSH access
- Must keep SSH session alive
- More complex setup
