# Migration Guide: From ngrok to Native HTTP

This document explains the changes made to modernize the Boltz MCP server and simplify deployment.

## What Changed?

### Before (ngrok-based)
- ❌ Required ngrok installation and configuration
- ❌ Manual tunnel setup with Python scripts
- ❌ URL changes on every restart (free tier)
- ❌ Complex setup with multiple moving parts
- ❌ Used FastMCP 1.x with `from mcp import FastMCP`

### After (FastMCP 2.0 HTTP)
- ✅ Native HTTP transport built into FastMCP
- ✅ Direct server deployment
- ✅ Multiple deployment options (Cloud, self-hosted, proxy)
- ✅ Simplified configuration
- ✅ Uses FastMCP 2.x with `from fastmcp import FastMCP`

## Key Changes

### 1. Server Code (`server/boltz_mcp_server.py`)

**Import statement:**
```python
# Before
from mcp import FastMCP

# After
from fastmcp import FastMCP
```

**Server startup:**
```python
# Before
if __name__ == "__main__":
    mcp.run()  # Only stdio

# After
if __name__ == "__main__":
    transport = os.getenv("BOLTZ_TRANSPORT", "http")
    if transport == "http":
        host = os.getenv("BOLTZ_HOST", "0.0.0.0")
        port = int(os.getenv("BOLTZ_PORT", "8000"))
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.run()  # stdio for local dev
```

### 2. Dependencies (`server/requirements.txt`)

**Before:**
```
fastmcp>=0.1.0
pyngrok>=7.0.0  # ngrok wrapper
```

**After:**
```
fastmcp>=2.0.0  # FastMCP 2.0 with HTTP support
# pyngrok removed - no longer needed
```

### 3. Configuration (`server/.env.example`)

**Before:**
```bash
NGROK_AUTH_TOKEN=your_token_here
```

**After:**
```bash
# Server Configuration
BOLTZ_TRANSPORT=http
BOLTZ_HOST=0.0.0.0
BOLTZ_PORT=8000

# Optional: Bearer token authentication
# BOLTZ_AUTH_TOKEN=your_secure_token
```

### 4. Removed Files

These files are no longer needed:
- ~~`server/start_ngrok_tunnel.py`~~ - Native HTTP replaces ngrok
- ~~`server/run_server.sh`~~ - Simplified startup

### 5. Claude Desktop Configuration

**Before (ngrok):**
```json
{
  "mcpServers": {
    "boltz-remote": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/client-stdio",
        "tcp://0.tcp.ngrok.io:12345"  // URL changes frequently
      ]
    }
  }
}
```

**After (HTTP):**
```json
{
  "mcpServers": {
    "boltz-remote": {
      "url": "http://YOUR_SERVER_IP:8000/mcp"  // Stable URL
    }
  }
}
```

Or with FastMCP Cloud:
```json
{
  "mcpServers": {
    "boltz-remote": {
      "url": "https://your-project.fastmcp.app/mcp"  // HTTPS included
    }
  }
}
```

## Migration Steps

If you have an existing deployment:

### Step 1: Update Server Code

```bash
cd boltz-remote-mcp
git pull  # Get latest changes
```

### Step 2: Update Python Environment

```bash
cd server
source venv/bin/activate

# Update FastMCP
pip install fastmcp>=2.0.0 --upgrade

# Remove ngrok (if installed)
pip uninstall pyngrok -y
```

### Step 3: Update Configuration

```bash
# Backup old config
cp .env .env.backup

# Copy new template
cp .env.example .env

# Edit with new settings
nano .env
```

Update to:
```bash
BOLTZ_TRANSPORT=http
BOLTZ_HOST=0.0.0.0
BOLTZ_PORT=8000
CUDA_VISIBLE_DEVICES=0
```

### Step 4: Restart Server

```bash
# Stop old server
pkill -f boltz_mcp_server.py

# Start new server
python boltz_mcp_server.py
```

You should see:
```
============================================================
Starting HTTP server on 0.0.0.0:8000
Server will be accessible at: http://0.0.0.0:8000/mcp/
============================================================
```

### Step 5: Update Claude Desktop Config

Edit your Claude Desktop config file and replace the ngrok URL with:

```json
{
  "mcpServers": {
    "boltz-remote": {
      "url": "http://YOUR_SERVER_IP:8000/mcp"
    }
  }
}
```

Get your server IP:
```bash
hostname -I  # On server
```

### Step 6: Restart Claude Desktop

Quit and relaunch Claude Desktop.

## New Deployment Options

With FastMCP 2.0, you now have three deployment options:

### Option 1: FastMCP Cloud ⭐ Recommended
- Easiest setup
- Automatic HTTPS
- No network configuration
- Free during beta

See [QUICKSTART.md](QUICKSTART.md)

### Option 2: Self-Hosted HTTP
- Direct deployment on your server
- Simple configuration
- Good for lab networks
- Requires firewall configuration

See [docs/setup_guide.md](docs/setup_guide.md#option-2-self-hosted-with-direct-http)

### Option 3: Reverse Proxy
- Production-grade deployment
- HTTPS with Let's Encrypt
- Custom domain support
- Advanced security

See [docs/setup_guide.md](docs/setup_guide.md#option-3-self-hosted-with-reverse-proxy)

## Advantages of New Approach

### Performance
- **Faster**: Direct HTTP is faster than tunneling
- **Lower latency**: No intermediate proxy
- **More reliable**: No dependency on external tunnel service

### Security
- **Better auth**: Native bearer token support
- **HTTPS ready**: Easy to add with reverse proxy
- **No third-party**: No ngrok account/token needed

### Maintenance
- **Simpler code**: Fewer moving parts
- **Easier debugging**: Standard HTTP logs
- **Better monitoring**: Native health checks

### Cost
- **Free**: No ngrok subscription needed
- **Flexible**: Use any hosting provider
- **Scalable**: Easy to add load balancing

## Backward Compatibility

The core MCP tools remain the same:
- `predict_structure_from_pdb`
- `predict_structure_from_sequence`
- `check_job_status`
- `get_prediction_result`
- `list_jobs`
- `get_server_info`

Your Claude Desktop prompts and workflows don't need to change - just update the configuration.

## Troubleshooting Migration

### Problem: Server won't start

**Error:** `ModuleNotFoundError: No module named 'fastmcp'`

```bash
pip install fastmcp>=2.0.0
```

### Problem: Import error

**Error:** `ImportError: cannot import name 'FastMCP' from 'mcp'`

Check the import statement:
```python
# Should be:
from fastmcp import FastMCP

# Not:
from mcp import FastMCP
```

### Problem: Claude Desktop can't connect

**Error:** Connection timeout

1. Verify server is running:
   ```bash
   curl http://localhost:8000/mcp/
   ```

2. Check firewall:
   ```bash
   sudo firewall-cmd --list-ports
   ```

3. Test from laptop:
   ```bash
   curl http://YOUR_SERVER_IP:8000/mcp/
   ```

## Getting Help

- **Documentation**: [docs/setup_guide.md](docs/setup_guide.md)
- **Quick start**: [QUICKSTART.md](QUICKSTART.md)
- **Troubleshooting**: [docs/troubleshooting.md](docs/troubleshooting.md)
- **FastMCP docs**: https://gofastmcp.com
- **GitHub issues**: Open an issue in the repository

## Rollback (if needed)

If you need to revert to the old ngrok-based approach:

```bash
# Checkout previous version
git checkout <previous-commit-hash>

# Reinstall old dependencies
pip install -r server/requirements.txt
pip install pyngrok

# Use old configuration
cp .env.backup .env
```

However, we recommend using the new approach as it's significantly simpler and more maintainable.
