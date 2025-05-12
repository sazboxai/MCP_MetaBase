#!/bin/bash

# Default behavior: Start both MCP server and Web Interface
echo "Starting MCP server in background..."
python -m src.server.mcp_server &
MCP_PID=$! # Get the Process ID of the backgrounded MCP server

echo "Starting Web Interface in foreground..."
# The FLASK_PORT environment variable should be set (e.g., in your .env file or Dockerfile)
# to the port exposed in the Dockerfile (5000).
# The Flask app in web_interface.py must be configured to bind to 0.0.0.0.
exec python -m src.server.web_interface

# Optional: A more robust script might wait for the MCP_PID to exit
# and handle cleanup, but for now, this keeps the web interface as the main process. 