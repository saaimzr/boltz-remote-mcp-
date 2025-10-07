# Boltz MCP Server - Quick Start Guide

Get your Boltz MCP server running in **under 10 minutes** using FastMCP Cloud.

## 🚀 Fastest Path to Deployment

### Prerequisites
- GitHub account
- Claude Desktop installed
- Your code in a GitHub repository

### Step 1: Push to GitHub (2 minutes)

```bash
cd boltz-remote-mcp

# Initialize and push
git add .
git commit -m "Deploy Boltz MCP server"
git push origin main
```

### Step 2: Deploy to FastMCP Cloud (5 minutes)

1. Go to **https://cloud.fastmcp.com**
2. Sign in with GitHub
3. Click **"New Project"**
4. Select your repository
5. Configure:
   - **Name:** `boltz-mcp`
   - **Server file:** `server/boltz_mcp_server.py`
   - **Requirements:** `server/requirements.txt`
6. Click **"Deploy"**

Wait ~5-10 minutes for dependencies to install (Boltz is large).

Your server URL: `https://your-project-name.fastmcp.app/mcp`

### Step 3: Connect Claude Desktop (2 minutes)

**On your laptop:**

Edit Claude Desktop config:

**macOS:**
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Windows:**
```powershell
notepad $env:APPDATA\Claude\claude_desktop_config.json
```

**Linux:**
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

**Add this:**
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

**Restart Claude Desktop.**

### Step 4: Test (1 minute)

In Claude Desktop:

```
Can you call the get_server_info tool?
```

✅ **Success!** You should see server info including GPU details.

---

## 🔧 Alternative: Self-Hosted (Lab Server)

If you prefer running on your own lab server with GPUs:

### Quick Setup

```bash
# On lab computer
git clone https://github.com/YOUR_USERNAME/boltz-remote-mcp.git
cd boltz-remote-mcp/server

# Setup Python environment
python3.12 -m venv venv  # Use Python 3.10-3.12
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install boltz[cuda] -U

# Configure
cp .env.example .env
nano .env  # Set CUDA_VISIBLE_DEVICES, etc.

# Run server
python boltz_mcp_server.py
```

**Get your server IP:**
```bash
hostname -I
```

**Configure Claude Desktop:**
```json
{
  "mcpServers": {
    "boltz-remote": {
      "url": "http://YOUR_LAB_IP:8000/mcp"
    }
  }
}
```

**Note:** You may need to open port 8000 in your firewall.

---

## 📚 Next Steps

- ✅ **Working?** Try a protein structure prediction
- 📖 **Need details?** See [docs/setup_guide.md](docs/setup_guide.md)
- 🐛 **Issues?** Check [docs/troubleshooting.md](docs/troubleshooting.md)
- 💡 **Examples?** See [docs/usage_examples.md](docs/usage_examples.md)

---

## 🧪 Example Usage

Once connected, ask Claude:

```
Predict the structure of this protein sequence:
MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL
```

Claude will:
1. Submit the job
2. Monitor progress
3. Return the predicted structure (CIF file)

---

**That's it!** You're ready to use Boltz through Claude Desktop. 🎉
