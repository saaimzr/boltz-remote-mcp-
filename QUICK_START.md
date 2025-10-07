# Quick Start Guide

Get your Boltz Remote MCP system running in under 30 minutes.

## What You'll Build

```
Your Laptop (Claude Desktop) ←→ Internet (ngrok) ←→ Lab Computer (Boltz + GPU)
```

## Prerequisites Checklist

- [ ] Lab computer with GPU and Python 3.8+
- [ ] SSH access to lab computer
- [ ] No sudo required (we work in userspace)
- [ ] Claude Desktop on your laptop
- [ ] 30 minutes of time

## 5-Minute Overview

**On Lab Computer:**
1. Transfer files
2. Install dependencies (Python packages, Boltz, ngrok)
3. Configure ngrok token
4. Start server

**On Your Laptop:**
1. Get ngrok URL from server
2. Configure Claude Desktop
3. Restart Claude Desktop
4. Test!

---

## Step-by-Step (30 Minutes)

### PART 1: Lab Computer (20 minutes)

**1. Transfer Files (2 min)**

From your laptop, in the `boltz-remote-mcp` directory:

```bash
scp -r server/ username@lab-computer:~/boltz-mcp-server/
```

**2. SSH to Lab Computer (1 min)**

```bash
ssh username@lab-computer
cd ~/boltz-mcp-server/server
```

**3. Create Python Environment (2 min)**

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

**4. Install Python Dependencies (5 min)**

```bash
pip install -r requirements.txt
pip install git+https://github.com/jwohlwend/boltz.git
```

*Note: Boltz installation downloads ~3GB, may take a few minutes*

**5. Install ngrok (3 min)**

```bash
cd ~/
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
mkdir -p ~/bin
mv ngrok ~/bin/
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
ngrok version  # verify it works
```

**6. Configure ngrok (2 min)**

Get your ngrok token from: https://dashboard.ngrok.com/get-started/your-authtoken

```bash
cd ~/boltz-mcp-server/server
cp .env.example .env
nano .env  # or vim, emacs, etc.
```

Add your token:
```
NGROK_AUTH_TOKEN=your_actual_token_here
CUDA_VISIBLE_DEVICES=0
```

Save and exit (Ctrl+X, Y, Enter in nano).

**7. Make Scripts Executable (1 min)**

```bash
chmod +x run_server.sh start_ngrok_tunnel.py
```

**8. Start Server (1 min)**

```bash
./run_server.sh
```

You should see:
```
[SUCCESS] ngrok tunnel established!
[SUCCESS] Public URL: tcp://0.tcp.ngrok.io:12345
```

**Copy this URL!** You'll need it in the next part.

**Keep this terminal open** (or use tmux/screen to run in background).

---

### PART 2: Your Laptop (10 minutes)

**1. Install Claude Desktop (5 min)**

Download from: https://claude.ai/download

Install and open it once.

**2. Find Config Directory (1 min)**

**macOS:**
```bash
cd ~/Library/Application\ Support/Claude/
```

**Windows (PowerShell):**
```powershell
cd $env:APPDATA\Claude
```

**Linux:**
```bash
cd ~/.config/Claude/
```

**3. Create Config File (2 min)**

Create or edit `claude_desktop_config.json`:

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

**Replace `tcp://0.tcp.ngrok.io:12345` with YOUR actual ngrok URL from Step 8 above!**

**4. Restart Claude Desktop (1 min)**

- Fully quit Claude Desktop (not just close window)
- macOS: Cmd+Q
- Windows: System tray → Exit
- Relaunch Claude Desktop

**5. Test! (1 min)**

In Claude Desktop, type:

```
Can you get info about the Boltz server?
```

If you see server information (GPU details, disk space, etc.), **success!** 🎉

---

## First Prediction

Try a simple protein structure prediction:

```
Predict the structure of this protein sequence:

MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL
```

Claude will:
1. Submit the job to your lab GPU
2. Give you a job ID
3. Monitor progress
4. Return the predicted structure when done

This may take 10-20 minutes. You can close Claude Desktop and check back later!

---

## Keeping Server Running

The server runs in your SSH session. If you disconnect, it stops.

**Use tmux to keep it running:**

```bash
# On lab computer, before starting server:
tmux new -s boltz-server

# Now start server:
cd ~/boltz-mcp-server/server
./run_server.sh

# Detach from tmux: Press Ctrl+B, then D
# Server keeps running!

# Later, reconnect:
ssh username@lab-computer
tmux attach -t boltz-server
```

---

## Troubleshooting

**Problem: "NGROK_AUTH_TOKEN not set"**
- Check `.env` file exists and has valid token

**Problem: "Command 'boltz' not found"**
- Activate venv: `source venv/bin/activate`
- Reinstall: `pip install git+https://github.com/jwohlwend/boltz.git`

**Problem: Claude Desktop doesn't see server**
- Verify ngrok URL in config is correct
- Check JSON syntax at https://jsonlint.com
- Fully restart Claude Desktop

**Problem: "nvidia-smi not found"**
- Contact lab admin - need GPU drivers
- Boltz requires CUDA-capable GPU

**More help:** See `docs/troubleshooting.md`

---

## What's Next?

- **Explore workflows:** `docs/usage_examples.md`
- **Full setup guide:** `docs/setup_guide.md`
- **Deployment checklist:** `DEPLOYMENT_CHECKLIST.md`

---

## Daily Use

**Start server:**
```bash
ssh username@lab-computer
cd ~/boltz-mcp-server/server
source venv/bin/activate
./run_server.sh
# Copy the ngrok URL
```

**Update Claude Desktop config** (if ngrok URL changed):
- Edit `claude_desktop_config.json` with new URL
- Restart Claude Desktop

**Use normally:**
- Just talk to Claude Desktop
- Ask it to predict structures
- Claude handles everything else!

---

## Key Points

✅ **No sudo required** - Everything runs in userspace

✅ **GPU access** - Uses lab GPUs remotely

✅ **Simple interface** - Just talk to Claude Desktop

✅ **Persistent** - Use tmux to keep server running

✅ **Secure** - ngrok provides encrypted tunnel

✅ **Free** - All tools are free (ngrok free tier sufficient for testing)

---

## Support

- **Documentation:** `boltz-remote-mcp/docs/`
- **Boltz issues:** https://github.com/jwohlwend/boltz/issues
- **MCP protocol:** https://modelcontextprotocol.io/

---

**Enjoy your remote GPU-powered protein structure predictions!** 🧬🚀
