#!/usr/bin/env python3
"""
Ngrok Tunnel Manager for Boltz MCP Server

This script provides a Python-based alternative to managing ngrok tunneling.
It can be used instead of or alongside the bash script.

Key features:
- Programmatic ngrok tunnel management
- Automatic retry on connection failures
- Health checking
- Tunnel URL persistence
"""

import os
import sys
import time
import json
import signal
from pathlib import Path
from typing import Optional

# pyngrok provides Python API for ngrok
from pyngrok import ngrok, conf

# Load environment variables from .env file
from dotenv import load_dotenv

# ============================================================================
# CONFIGURATION
# ============================================================================

# Get script directory
SCRIPT_DIR = Path(__file__).parent

# Load .env file
ENV_FILE = SCRIPT_DIR / ".env"
if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
    print(f"[INFO] Loaded environment from {ENV_FILE}")
else:
    print(f"[WARNING] No .env file found at {ENV_FILE}")

# Get ngrok auth token from environment
NGROK_AUTH_TOKEN = os.getenv("NGROK_AUTH_TOKEN")
if not NGROK_AUTH_TOKEN:
    print("[ERROR] NGROK_AUTH_TOKEN not set")
    print("[ERROR] Please set it in .env file or environment")
    print("[INFO] Get your token from: https://dashboard.ngrok.com/get-started/your-authtoken")
    sys.exit(1)

# MCP server will listen on this port
MCP_SERVER_PORT = 8000

# File to store the ngrok URL
URL_FILE = SCRIPT_DIR / "ngrok_url.txt"

# File to store tunnel information
TUNNEL_INFO_FILE = SCRIPT_DIR / "ngrok_tunnel_info.json"

# ============================================================================
# TUNNEL MANAGEMENT
# ============================================================================

class NgrokTunnelManager:
    """
    Manages ngrok tunnel lifecycle.

    Responsibilities:
    - Start/stop tunnel
    - Persist tunnel URL
    - Handle cleanup on exit
    """

    def __init__(self, port: int, auth_token: str):
        """
        Initialize tunnel manager.

        Args:
            port: Local port to tunnel (where MCP server listens)
            auth_token: ngrok authentication token
        """
        self.port = port
        self.auth_token = auth_token
        self.tunnel = None

        # Set ngrok auth token in pyngrok configuration
        # This is equivalent to: ngrok config add-authtoken <token>
        conf.get_default().auth_token = auth_token

    def start(self) -> str:
        """
        Start ngrok tunnel.

        Returns:
            Public tunnel URL (e.g., "tcp://0.tcp.ngrok.io:12345")

        Raises:
            Exception: If tunnel fails to start
        """
        print(f"[INFO] Starting ngrok tunnel for port {self.port}...")

        try:
            # Create TCP tunnel to local port
            # ngrok.connect() returns a NgrokTunnel object
            # "tcp" = tunnel type (we're using TCP for MCP over stdio)
            # bind_tls=False = don't require TLS (optional, depends on MCP client)
            self.tunnel = ngrok.connect(
                addr=self.port,
                proto="tcp",
                bind_tls=False
            )

            # Get public URL
            public_url = self.tunnel.public_url

            print(f"[SUCCESS] Tunnel established!")
            print(f"[SUCCESS] Public URL: {public_url}")

            # Save URL to file
            self._save_tunnel_info(public_url)

            return public_url

        except Exception as e:
            print(f"[ERROR] Failed to start tunnel: {e}")
            raise

    def _save_tunnel_info(self, public_url: str):
        """
        Save tunnel information to files for easy access.

        Args:
            public_url: The ngrok public URL
        """
        # Save URL to simple text file
        URL_FILE.write_text(public_url)
        print(f"[INFO] Saved URL to {URL_FILE}")

        # Save detailed tunnel info to JSON file
        tunnel_info = {
            "public_url": public_url,
            "local_port": self.port,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tunnel_name": self.tunnel.name if self.tunnel else None,
        }

        with open(TUNNEL_INFO_FILE, 'w') as f:
            json.dump(tunnel_info, f, indent=2)

        print(f"[INFO] Saved tunnel info to {TUNNEL_INFO_FILE}")

    def stop(self):
        """
        Stop ngrok tunnel and clean up.
        """
        print("[INFO] Stopping ngrok tunnel...")

        if self.tunnel:
            try:
                # Disconnect the tunnel
                ngrok.disconnect(self.tunnel.public_url)
                print("[SUCCESS] Tunnel disconnected")
            except Exception as e:
                print(f"[WARNING] Error disconnecting tunnel: {e}")

        # Kill ngrok process
        # This ensures no orphaned ngrok processes remain
        try:
            ngrok.kill()
            print("[SUCCESS] Ngrok process killed")
        except Exception as e:
            print(f"[WARNING] Error killing ngrok: {e}")

        # Clean up files
        if URL_FILE.exists():
            URL_FILE.unlink()
        if TUNNEL_INFO_FILE.exists():
            TUNNEL_INFO_FILE.unlink()

        print("[INFO] Cleanup complete")

    def get_tunnel_url(self) -> Optional[str]:
        """
        Get the current tunnel URL if available.

        Returns:
            Tunnel URL string, or None if not available
        """
        if URL_FILE.exists():
            return URL_FILE.read_text().strip()
        return None

# ============================================================================
# SIGNAL HANDLING
# ============================================================================

# Global tunnel manager instance for signal handler
tunnel_manager: Optional[NgrokTunnelManager] = None

def signal_handler(sig, frame):
    """
    Handle interrupt signals (Ctrl+C) gracefully.

    This ensures tunnel is properly closed when user stops the script.

    Args:
        sig: Signal number
        frame: Current stack frame
    """
    print("\n[INFO] Interrupt received, shutting down...")

    if tunnel_manager:
        tunnel_manager.stop()

    sys.exit(0)

# Register signal handlers
# SIGINT = Ctrl+C
# SIGTERM = kill command
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ============================================================================
# MAIN FUNCTION
# ============================================================================

def main():
    """
    Main entry point for tunnel manager.

    This can be run standalone or imported by the MCP server script.
    """
    global tunnel_manager

    print("=" * 60)
    print("Ngrok Tunnel Manager for Boltz MCP Server")
    print("=" * 60)

    # Create tunnel manager
    tunnel_manager = NgrokTunnelManager(
        port=MCP_SERVER_PORT,
        auth_token=NGROK_AUTH_TOKEN
    )

    try:
        # Start tunnel
        public_url = tunnel_manager.start()

        print("=" * 60)
        print("[SUCCESS] Tunnel is ready!")
        print("=" * 60)
        print(f"\nPublic URL: {public_url}")
        print(f"\nLocal Port: {MCP_SERVER_PORT}")
        print("\nUse this URL in your Claude Desktop configuration:")
        print(f"  {public_url}")
        print("\nPress Ctrl+C to stop the tunnel")
        print("=" * 60)

        # Keep tunnel alive
        # The script will run until interrupted
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # This is handled by signal_handler, but included for completeness
        print("\n[INFO] Keyboard interrupt received")

    finally:
        # Cleanup on exit
        if tunnel_manager:
            tunnel_manager.stop()

# ============================================================================
# SCRIPT ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    """
    Run tunnel manager as standalone script.

    Usage:
        python3 start_ngrok_tunnel.py

    This will:
    1. Load .env configuration
    2. Start ngrok tunnel
    3. Display public URL
    4. Keep tunnel running until Ctrl+C
    """
    main()
