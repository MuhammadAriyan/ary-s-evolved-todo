#!/usr/bin/env python3
"""MCP Server runner script.

This script runs the MCP server as a standalone process.
It's used by MCPServerStdio to spawn the server subprocess.

Usage:
    python -m app.services.ai.mcp_runner
"""
import sys
import os

# Add backend to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, backend_dir)

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = os.path.join(backend_dir, ".env")
load_dotenv(env_path)

from app.services.ai.mcp_server import mcp

if __name__ == "__main__":
    # Run MCP server with stdio transport
    mcp.run(transport="stdio")
