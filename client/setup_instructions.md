# Claude Desktop Client Setup Instructions

This guide walks you through configuring Claude Desktop to connect to your remote Boltz MCP server.

## Prerequisites

- Claude Desktop installed on your local laptop
- ngrok URL from your lab computer (should look like: `tcp://0.tcp.ngrok.io:12345`)

## Step-by-Step Setup

### Step 1: Locate Claude Desktop Configuration Directory

The configuration file location depends on your operating system:

**macOS:**
```bash
~/Library/Application Support/Claude/
```

**Windows:**
```
%APPDATA%\Claude\
```

**Linux:**
```bash
~/.config/Claude/
```

### Step 2: Create or Edit Configuration File

1. Navigate to the configuration directory
2. Look for `claude_desktop_config.json`
3. If it doesn't exist, create it
4. If it exists, back it up first: `cp claude_desktop_config.json claude_desktop_config.json.backup`

### Step 3: Add Boltz MCP Server Configuration

Edit `claude_desktop_config.json` to include the Boltz server:

```json
{
  "mcpServers": {
    "boltz-remote": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/client-stdio",
        "YOUR_NGROK_URL_HERE"
      ]
    }
  }
}
```

**Important:** Replace `YOUR_NGROK_URL_HERE` with the actual ngrok URL from your server.

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

### Step 4: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Relaunch Claude Desktop
3. The MCP server should now be available

### Step 5: Verify Connection

In Claude Desktop, try a simple test:

```
Can you check the Boltz server info?
```

Claude should be able to call the `get_server_info` tool and return information about your remote server.

## Alternative Setup (Windows PowerShell)

If you're on Windows, here's a PowerShell script to automatically configure Claude Desktop:

```powershell
# Set your ngrok URL here
$ngrokUrl = "tcp://0.tcp.ngrok.io:12345"

# Get Claude config directory
$claudeConfigDir = "$env:APPDATA\Claude"
$configFile = "$claudeConfigDir\claude_desktop_config.json"

# Create directory if it doesn't exist
if (-not (Test-Path $claudeConfigDir)) {
    New-Item -ItemType Directory -Path $claudeConfigDir -Force
}

# Create configuration
$config = @{
    mcpServers = @{
        "boltz-remote" = @{
            command = "npx"
            args = @(
                "-y",
                "@modelcontextprotocol/client-stdio",
                $ngrokUrl
            )
        }
    }
} | ConvertTo-Json -Depth 10

# Save configuration
$config | Out-File -FilePath $configFile -Encoding UTF8

Write-Host "Configuration saved to: $configFile"
Write-Host "Please restart Claude Desktop"
```

## Alternative Setup (macOS/Linux Bash)

```bash
#!/bin/bash

# Set your ngrok URL here
NGROK_URL="tcp://0.tcp.ngrok.io:12345"

# Determine config directory
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
else
    # Linux
    CONFIG_DIR="$HOME/.config/Claude"
fi

CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

# Create directory if needed
mkdir -p "$CONFIG_DIR"

# Create configuration
cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "boltz-remote": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/client-stdio",
        "$NGROK_URL"
      ]
    }
  }
}
EOF

echo "Configuration saved to: $CONFIG_FILE"
echo "Please restart Claude Desktop"
```

## Troubleshooting

### Claude Desktop doesn't see the MCP server

1. **Check the config file location**
   - Make sure you edited the file in the correct directory
   - Verify the file is named exactly `claude_desktop_config.json`

2. **Check JSON syntax**
   - Use a JSON validator (e.g., jsonlint.com)
   - Common errors: missing commas, extra commas, mismatched brackets

3. **Verify ngrok URL**
   - Make sure the URL starts with `tcp://`
   - Confirm the URL is active (check on lab computer)
   - Try accessing the URL from your laptop network

4. **Check Claude Desktop logs**
   - macOS: `~/Library/Logs/Claude/`
   - Windows: `%APPDATA%\Claude\logs\`
   - Linux: `~/.config/Claude/logs/`

### Connection timeouts

1. **Check network connectivity**
   - Verify your laptop can reach ngrok domains
   - Try: `curl -v https://ngrok.io`

2. **Firewall issues**
   - Ensure your laptop firewall allows outbound connections
   - Corporate networks may block ngrok

3. **Server not running**
   - Verify the MCP server is running on lab computer
   - Check server logs for errors

### Tools not appearing

1. **Restart Claude Desktop completely**
   - Don't just close the window, fully quit the application
   - On macOS: Cmd+Q
   - On Windows: Right-click system tray icon → Exit

2. **Check server logs**
   - Look for errors in server startup
   - Verify Boltz installation is complete

3. **Test with get_server_info tool first**
   - This is a simple tool that doesn't require Boltz
   - If this works, server connection is good

## Multiple MCP Servers

If you already have other MCP servers configured, add Boltz alongside them:

```json
{
  "mcpServers": {
    "existing-server": {
      "command": "...",
      "args": [...]
    },
    "boltz-remote": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/client-stdio",
        "tcp://0.tcp.ngrok.io:12345"
      ]
    },
    "another-server": {
      "command": "...",
      "args": [...]
    }
  }
}
```

## Updating ngrok URL

When you restart the server, ngrok generates a new URL (on free tier). To update:

1. Get new URL from server (check `ngrok_url.txt` on lab computer)
2. Edit `claude_desktop_config.json` with new URL
3. Restart Claude Desktop

**Tip:** Consider upgrading to ngrok Pro for persistent URLs that don't change.

## Security Notes

- ngrok free tier URLs are public (anyone with URL can access)
- Consider using ngrok authentication for production use
- Don't share your ngrok URLs publicly
- Monitor server logs for unexpected access

## Next Steps

Once configured, see `docs/usage_examples.md` for example workflows!
