# Boltz Remote MCP Server

A distributed MCP (Model Context Protocol) system for running Boltz protein structure predictions on remote GPU servers, accessible from Claude Desktop.

## Architecture

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│ Claude Desktop  │ ◄─────► │    ngrok     │ ◄─────► │  Lab Computer   │
│  (Local Laptop) │         │   Tunnel     │         │  (GPU Server)   │
│                 │         │              │         │                 │
│  MCP Client     │         │  HTTPS/WSS   │         │  FastMCP Server │
│                 │         │              │         │  Boltz Inference│
└─────────────────┘         └──────────────┘         └─────────────────┘
```

## Components

### Server (Lab Computer)
- `server/boltz_mcp_server.py` - FastMCP server with Boltz integration
- `server/requirements.txt` - Python dependencies
- `server/run_server.sh` - Server startup script
- `server/.env.example` - Environment variables template

### Client (Local Laptop)
- `client/claude_desktop_config.json` - MCP configuration for Claude Desktop
- `client/setup_instructions.md` - Step-by-step setup guide

### Documentation
- `docs/setup_guide.md` - Complete setup walkthrough
- `docs/troubleshooting.md` - Common issues and solutions
- `docs/usage_examples.md` - Example workflows

## Quick Start

### On Lab Computer (Server)
1. Install dependencies (no sudo required)
2. Set up ngrok authentication
3. Run the MCP server
4. Copy the ngrok URL

### On Local Laptop (Client)
1. Install Claude Desktop
2. Configure MCP client with ngrok URL
3. Start using Boltz through Claude Desktop

See `docs/setup_guide.md` for detailed instructions.

## Features

- **Remote GPU Inference**: Run Boltz on lab GPUs from anywhere
- **No Sudo Required**: All components run in userspace
- **Secure Tunneling**: ngrok provides HTTPS encryption
- **File Management**: Upload PDB files, receive predictions
- **Async Processing**: Handle long-running inference jobs

## Requirements

### Lab Computer
- Python 3.8+
- CUDA-capable GPU
- Network access (for ngrok)
- ~10GB disk space (for Boltz models)

### Local Laptop
- Claude Desktop application
- Internet connection

## Security Notes

- ngrok provides free HTTPS tunneling with authentication
- Consider using ngrok's built-in authentication for production
- Keep your ngrok auth token secure
- Lab computer firewall: no inbound ports needed (ngrok handles this)
