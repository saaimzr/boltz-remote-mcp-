# Deployment Checklist

Use this checklist to ensure proper setup of your Boltz Remote MCP system.

## Pre-Deployment

### Lab Computer Requirements

- [ ] Python 3.8+ installed
- [ ] CUDA-capable GPU available
- [ ] ~10GB free disk space for models
- [ ] Network access (for ngrok)
- [ ] SSH access configured
- [ ] Can install Python packages without sudo (via pip --user or venv)

### Local Laptop Requirements

- [ ] Claude Desktop installed
- [ ] Internet connection
- [ ] Node.js/npm installed (for MCP client)
- [ ] SSH client available (for file transfer)

### Accounts & Credentials

- [ ] ngrok account created (https://dashboard.ngrok.com/signup)
- [ ] ngrok auth token obtained
- [ ] Lab computer SSH credentials available

---

## Phase 1: File Transfer

### Transfer server files to lab computer

**Method chosen:** ☐ SCP  ☐ rsync  ☐ Git  ☐ USB  ☐ Other: _______

- [ ] Copied `server/` directory to lab computer
- [ ] Verified all files transferred correctly
  ```bash
  ls ~/boltz-mcp-server/server/
  # Should see: boltz_mcp_server.py, requirements.txt, run_server.sh, etc.
  ```

---

## Phase 2: Lab Computer Setup

### SSH Connection

- [ ] Successfully connected to lab computer
  ```bash
  ssh username@lab-computer
  ```
- [ ] Navigated to server directory
  ```bash
  cd ~/boltz-mcp-server/server
  ```

### Python Environment

- [ ] Python 3.8+ verified
  ```bash
  python3 --version
  ```
- [ ] Virtual environment created
  ```bash
  python3 -m venv venv
  ```
- [ ] Virtual environment activated
  ```bash
  source venv/bin/activate
  ```
- [ ] Pip upgraded
  ```bash
  pip install --upgrade pip
  ```

### Dependency Installation

- [ ] Python packages installed
  ```bash
  pip install -r requirements.txt
  ```
- [ ] Boltz installed
  ```bash
  pip install git+https://github.com/jwohlwend/boltz.git
  ```
- [ ] Boltz CLI verified
  ```bash
  boltz --help
  ```

### GPU Verification

- [ ] CUDA drivers accessible
  ```bash
  nvidia-smi
  ```
- [ ] GPU(s) listed and available
- [ ] GPU indices noted: _______

### ngrok Installation

- [ ] ngrok binary downloaded
  ```bash
  wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
  ```
- [ ] ngrok extracted
  ```bash
  tar -xzf ngrok-v3-stable-linux-amd64.tgz
  ```
- [ ] ngrok moved to ~/bin
  ```bash
  mkdir -p ~/bin && mv ngrok ~/bin/
  ```
- [ ] ~/bin added to PATH
  ```bash
  echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
  source ~/.bashrc
  ```
- [ ] ngrok version verified
  ```bash
  ngrok version
  ```

### Configuration

- [ ] .env file created
  ```bash
  cp .env.example .env
  ```
- [ ] ngrok auth token added to .env
  ```bash
  nano .env
  # Added: NGROK_AUTH_TOKEN=your_token_here
  ```
- [ ] CUDA devices configured in .env
  ```bash
  # Added: CUDA_VISIBLE_DEVICES=0
  ```

### Scripts

- [ ] Scripts made executable
  ```bash
  chmod +x run_server.sh start_ngrok_tunnel.py
  ```

### Directory Structure

- [ ] Verified directory structure
  ```bash
  ls -la ~/.boltz_mcp/
  # Should have: uploads/, outputs/, models/
  ```

---

## Phase 3: Server Startup

### Test Run

- [ ] Server started successfully
  ```bash
  ./run_server.sh
  ```
- [ ] No error messages in output
- [ ] ngrok tunnel established
- [ ] ngrok URL displayed

### Record Information

- [ ] ngrok URL recorded: _______________________________
- [ ] Server port noted: _______
- [ ] Server process ID noted: _______

### Verify Server

- [ ] Server responds to requests
- [ ] No crash in first 5 minutes
- [ ] Logs look normal

---

## Phase 4: Local Laptop Setup

### Claude Desktop Installation

- [ ] Claude Desktop downloaded
- [ ] Claude Desktop installed
- [ ] Claude Desktop opened successfully

### Configuration Directory

- [ ] Configuration directory located
  - macOS: `~/Library/Application Support/Claude/`
  - Windows: `%APPDATA%\Claude\`
  - Linux: `~/.config/Claude/`
- [ ] Directory is writable

### Configuration File

- [ ] Backup created (if existing config)
  ```bash
  cp claude_desktop_config.json claude_desktop_config.json.backup
  ```
- [ ] New config file created
- [ ] ngrok URL added to config
  ```json
  {
    "mcpServers": {
      "boltz-remote": {
        "command": "npx",
        "args": [
          "-y",
          "@modelcontextprotocol/client-stdio",
          "tcp://YOUR_NGROK_URL_HERE"
        ]
      }
    }
  }
  ```
- [ ] JSON syntax validated (https://jsonlint.com)

### Claude Desktop Restart

- [ ] Claude Desktop fully quit
- [ ] Claude Desktop relaunched

---

## Phase 5: Testing

### Basic Connectivity

- [ ] Test 1: Server info requested in Claude Desktop
  ```
  Can you get server info from Boltz?
  ```
- [ ] Test 1 result: ☐ Success  ☐ Failed

If failed, stop and troubleshoot before continuing.

### Tool Availability

- [ ] Verified tools available:
  - [ ] `predict_structure_from_pdb`
  - [ ] `predict_structure_from_sequence`
  - [ ] `check_job_status`
  - [ ] `get_prediction_result`
  - [ ] `list_jobs`
  - [ ] `get_server_info`

### Simple Prediction

- [ ] Test 2: Sequence prediction
  ```
  Predict structure for sequence: MKTAYIAKQRQISFVKSHFSRQ
  ```
- [ ] Job ID received
- [ ] Job status checked
- [ ] Prediction completed (wait 5-15 min)
- [ ] Result file retrieved
- [ ] Test 2 result: ☐ Success  ☐ Failed

### File Upload

- [ ] Test 3: PDB file upload
  - [ ] Downloaded test PDB: https://files.rcsb.org/download/1UBQ.pdb
  - [ ] Uploaded to Claude Desktop
  - [ ] Prediction requested
  - [ ] Result received
- [ ] Test 3 result: ☐ Success  ☐ Failed

---

## Phase 6: Production Readiness

### Server Persistence

**Method chosen:** ☐ tmux  ☐ screen  ☐ nohup  ☐ systemd

- [ ] Server configured to run persistently
- [ ] Server survives SSH disconnection
- [ ] Tested reconnecting after disconnect

**tmux setup (recommended):**
```bash
# Start tmux session
tmux new -s boltz-server

# Run server
cd ~/boltz-mcp-server/server
./run_server.sh

# Detach: Ctrl+B then D

# Reattach later:
tmux attach -t boltz-server
```

### Monitoring

- [ ] Server logs location noted: _______________________________
- [ ] Log rotation configured (optional)
- [ ] Disk space monitoring set up
  ```bash
  # Add to crontab for daily disk usage email
  0 9 * * * df -h ~ | mail -s "Lab disk usage" you@email.com
  ```

### Documentation

- [ ] ngrok URL documented in safe place
- [ ] Lab computer hostname/IP documented
- [ ] SSH credentials documented securely
- [ ] Claude Desktop config backed up

### Security

- [ ] ngrok auth token kept secure (not committed to git)
- [ ] .env file permissions restricted
  ```bash
  chmod 600 .env
  ```
- [ ] SSH key-based authentication set up (recommended)
- [ ] Server logs monitored for unexpected access

---

## Phase 7: User Training

### Documentation Review

- [ ] Read `README.md`
- [ ] Read `docs/setup_guide.md`
- [ ] Read `docs/usage_examples.md`
- [ ] Read `docs/troubleshooting.md`

### Practice Workflows

- [ ] Completed Example 1 (sequence prediction)
- [ ] Completed Example 2 (PDB refinement)
- [ ] Know how to check job status
- [ ] Know how to retrieve results
- [ ] Know how to handle errors

### Troubleshooting Knowledge

- [ ] Know how to check if server is running
- [ ] Know how to restart server
- [ ] Know how to get new ngrok URL
- [ ] Know how to update Claude Desktop config
- [ ] Know where to find logs

---

## Ongoing Maintenance

### Daily

- [ ] Check server is running
  ```bash
  ssh user@lab-computer
  tmux attach -t boltz-server
  # Verify no errors
  ```

### Weekly

- [ ] Review disk space usage
  ```bash
  du -sh ~/.boltz_mcp/*
  ```
- [ ] Clean old prediction outputs
  ```bash
  # Keep last 30 days
  find ~/.boltz_mcp/outputs/ -mtime +30 -delete
  ```

### Monthly

- [ ] Update dependencies
  ```bash
  cd ~/boltz-mcp-server/server
  source venv/bin/activate
  pip install --upgrade -r requirements.txt
  ```
- [ ] Review and archive logs
- [ ] Check for Boltz updates
  ```bash
  pip install --upgrade git+https://github.com/jwohlwend/boltz.git
  ```

---

## Troubleshooting Quick Reference

### Server won't start
1. Check .env file exists and has auth token
2. Check venv is activated
3. Check ngrok is installed and in PATH
4. Review `docs/troubleshooting.md`

### Claude Desktop can't connect
1. Verify server is running on lab computer
2. Check ngrok URL in config matches server URL
3. Validate JSON syntax
4. Restart Claude Desktop completely

### Predictions failing
1. Check GPU availability: `nvidia-smi`
2. Check disk space: `df -h ~`
3. Review server logs
4. Reduce quality parameters for testing

---

## Success Criteria

System is fully deployed when:

- [x] Server runs on lab computer
- [x] ngrok tunnel is active
- [x] Claude Desktop connects successfully
- [x] All tools are available
- [x] Test predictions complete successfully
- [x] Server persists after SSH disconnect
- [x] User can independently run predictions

---

## Support Resources

- **Project documentation:** `boltz-remote-mcp/docs/`
- **Boltz GitHub:** https://github.com/jwohlwend/boltz
- **FastMCP docs:** https://gofastmcp.com/
- **ngrok docs:** https://ngrok.com/docs
- **MCP protocol:** https://modelcontextprotocol.io/

---

## Notes

_Use this space for deployment-specific notes, issues encountered, or customizations made:_

```






```

---

**Deployment Date:** ______________

**Deployed By:** ______________

**System Status:** ☐ Fully Operational  ☐ Partially Working  ☐ Troubleshooting

**Known Issues:** _______________________________________________________________

________________________________________________________________________________
