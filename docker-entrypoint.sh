#!/bin/bash

# Allow running different commands based on first argument
if [ "$1" = "config" ]; then
    echo "Starting configuration interface..."
    exec python -m src.server.web_interface
elif [ "$1" = "mcp" ]; then
    echo "Starting MCP server..."
    exec python -m src.server.mcp_server
else
    # Default to MCP server if no command is provided
    echo "Starting MCP server (default)..."
    exec python -m src.server.mcp_server
fi 