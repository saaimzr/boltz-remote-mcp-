# Boltz Remote MCP Server

A FastMCP server that enables Claude Desktop to run [Boltz](https://github.com/jwohlwend/boltz) protein structure predictions on remote GPU servers.

## 🎯 What is This?

This project lets you:
- Run Boltz protein structure predictions from Claude Desktop
- Use your lab's powerful GPU server remotely
- Access predictions from any laptop without local GPU
- Handle PDB files and amino acid sequences
- Track long-running jobs asynchronously

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│ Claude Desktop  │ ◄─────► │ FastMCP HTTP │ ◄─────► │  Lab Computer   │
│  (Your Laptop)  │         │  Transport   │         │  (GPU Server)   │
│                 │         │              │         │                 │
│  MCP Client     │         │    HTTPS     │         │  Boltz Inference│
└─────────────────┘         └──────────────┘         └─────────────────┘
```

## ✨ Features

- **Remote GPU Access**: Run Boltz on lab GPUs from anywhere
- **Multiple Input Types**: PDB files or amino acid sequences
- **Async Job Queue**: Handle long-running predictions
- **Progress Tracking**: Monitor job status in real-time
- **Multiple Deployment Options**: FastMCP Cloud, self-hosted, or reverse proxy
- **No Local Setup**: Claude Desktop handles all client-side logic

## 🚀 Quick Start

### Option 1: ngrok Tunnel (No Sudo Required - RECOMMENDED)

**Best option if you don't have admin access on your lab computer.**

ngrok creates a public HTTPS URL that tunnels to your lab computer, bypassing firewall issues completely.

```bash
# On lab computer (via SSH)
cd ~/boltz-remote-mcp/server
source venv/bin/activate

# Start server
python boltz_mcp_server.py

# In another terminal, start ngrok
ngrok http 8000

# Copy the ngrok URL (like https://abc123.ngrok-free.app)
# Configure Claude Desktop to use that URL + /mcp
```

**See [docs/NGROK_SETUP.md](docs/NGROK_SETUP.md) for complete step-by-step instructions.**

### Option 2: Self-Hosted with Firewall Access

```bash
# On lab computer
git clone https://github.com/YOUR_USERNAME/boltz-remote-mcp.git
cd boltz-remote-mcp/server

# Setup environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install boltz[cuda] -U

# Configure and run
cp .env.example .env
nano .env  # Configure GPUs, port, etc.
python boltz_mcp_server.py
```

See [docs/setup_guide.md](docs/setup_guide.md) for complete instructions.

## 📋 Requirements

### Lab Computer (Server)
- Python 3.10, 3.11, or 3.12 (⚠️ NOT 3.13+)
- CUDA-capable GPU with drivers
- ~10GB disk space for models
- Network access

### Local Laptop (Client)
- Claude Desktop ([download](https://claude.ai/download))
- Internet connection

## 🛠️ Available Tools

The server exposes these MCP tools:

| Tool | Description |
|------|-------------|
| `predict_structure_from_pdb` | Predict structure from PDB file |
| `predict_structure_from_sequence` | Predict structure from amino acid sequence |
| `check_job_status` | Monitor prediction progress |
| `get_prediction_result` | Retrieve completed structure (CIF file) |
| `list_jobs` | View recent jobs |
| `get_server_info` | Get server/GPU information |

## 📖 Documentation

- **[docs/NGROK_SETUP.md](docs/NGROK_SETUP.md)** - **⭐ START HERE** for no-sudo setup (recommended, detailed step-by-step)
- **[docs/NO_SUDO_SETUP.md](docs/NO_SUDO_SETUP.md)** - Alternative: SSH tunneling method
- **[docs/setup_guide.md](docs/setup_guide.md)** - Complete setup for all deployment options
- **[QUICKSTART.md](QUICKSTART.md)** - Quick reference guide
- **[docs/usage_examples.md](docs/usage_examples.md)** - Example workflows
- **[docs/troubleshooting.md](docs/troubleshooting.md)** - Common issues and solutions
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migrating from old ngrok approach

## 🔧 Configuration

Server behavior is controlled via environment variables in `.env`:

```bash
# Server Configuration
BOLTZ_TRANSPORT=http        # "stdio" or "http"
BOLTZ_HOST=0.0.0.0         # Host to bind to
BOLTZ_PORT=8000            # Port to listen on

# GPU Configuration
CUDA_VISIBLE_DEVICES=0     # GPU device IDs

# Optional Authentication
BOLTZ_AUTH_TOKEN=...       # Bearer token for auth
```

See [server/.env.example](server/.env.example) for all options.

## 💡 Example Usage

Once configured, ask Claude Desktop:

```
Can you predict the structure of this protein sequence:
MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL
```

Claude will:
1. Call `predict_structure_from_sequence`
2. Poll `check_job_status` until complete
3. Retrieve result with `get_prediction_result`
4. Return the predicted structure (CIF file)

## 🏛️ Project Structure

```
boltz-remote-mcp/
├── server/
│   ├── boltz_mcp_server.py   # Main FastMCP server
│   ├── requirements.txt       # Python dependencies
│   └── .env.example          # Configuration template
├── docs/
│   ├── setup_guide.md        # Complete setup instructions
│   ├── usage_examples.md     # Example workflows
│   └── troubleshooting.md    # Problem solving
├── README.md                 # This file
└── QUICKSTART.md            # Fast deployment guide
```

## 🔐 Security Considerations

- **FastMCP Cloud**: Includes HTTPS automatically
- **Self-hosted**: Consider adding bearer token authentication
- **Production**: Use reverse proxy (nginx/caddy) with HTTPS
- **Firewall**: Only open necessary ports

See [docs/setup_guide.md](docs/setup_guide.md) for security best practices.

## 🐛 Troubleshooting

**Don't have sudo/admin access?**
- Use SSH tunneling method (see [docs/NO_SUDO_SETUP.md](docs/NO_SUDO_SETUP.md))
- No firewall configuration needed

**Server won't start?**
- Check Python version (3.10-3.12 required)
- Verify CUDA drivers with `nvidia-smi`
- Ensure dependencies installed: `pip install -r requirements.txt`

**Claude Desktop can't connect?**
- Verify server is running on lab computer
- Check SSH tunnel is active (if using SSH method)
- Confirm URL in config: `http://localhost:8000/mcp` for SSH tunnel
- Restart Claude Desktop after config changes

**Predictions failing?**
- Check GPU memory with `nvidia-smi`
- Reduce `recycling_steps` or `sampling_steps`
- View server logs for errors

See [docs/troubleshooting.md](docs/troubleshooting.md) and [docs/NO_SUDO_SETUP.md](docs/NO_SUDO_SETUP.md) for detailed solutions.

## 🙏 Acknowledgments

- [Boltz](https://github.com/jwohlwend/boltz) - Protein structure prediction
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [Model Context Protocol](https://modelcontextprotocol.io) - Protocol specification

## 📄 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

- **Documentation**: See [docs/](docs/) directory
- **Issues**: Open a GitHub issue
- **FastMCP**: https://gofastmcp.com
- **Boltz**: https://github.com/jwohlwend/boltz

---

**Ready to get started?** See [QUICKSTART.md](QUICKSTART.md) for the fastest deployment path.
