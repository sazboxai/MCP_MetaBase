# Metabase MCP Server

A Model Control Protocol (MCP) server that enables AI assistants to interact with Metabase databases and actions.

![Metabase MCP Server](https://path-to-screenshot.png)

## Overview

The Metabase MCP Server provides a bridge between AI assistants and Metabase, allowing AI models to:

- List and explore databases configured in Metabase
- Retrieve detailed metadata about database schemas, tables, and fields
- Visualize relationships between tables in a database
- List and execute Metabase actions
- Perform operations on Metabase data through a secure API

This server implements the [Model Control Protocol (MCP)](https://github.com/anthropics/mcp) specification, making it compatible with AI assistants that support MCP tools.

## Features

- **Database Exploration**: List all databases and explore their schemas
- **Metadata Retrieval**: Get detailed information about tables, fields, and relationships
- **Relationship Visualization**: Generate visual representations of database relationships
- **Action Management**: List, view details, and execute Metabase actions
- **Secure API Key Handling**: Store API keys encrypted and prevent exposure
- **Web Interface**: Test and debug functionality through a user-friendly web interface
- **Docker Support**: Easy deployment with Docker and Docker Compose

## Prerequisites

- Metabase instance (v0.46.0 or higher recommended)
- Metabase API key with appropriate permissions
- Docker (for containerized deployment)
- Python 3.10+ (for local development)

## Installation

### Using Docker (Recommended)

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/metabase-mcp.git
   cd metabase-mcp
   ```

2. Build and run the Docker container:
   ```bash
   docker-compose up -d
   ```

3. Access the configuration interface at http://localhost:5001

### Manual Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/metabase-mcp.git
   cd metabase-mcp
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the configuration interface:
   ```bash
   python -m src.server.web_interface
   ```

4. Access the configuration interface at http://localhost:5000

## Configuration

1. Open the web interface in your browser
2. Enter your Metabase URL (e.g., http://localhost:3000)
3. Enter your Metabase API key
4. Click "Save Configuration" and test the connection

### Obtaining a Metabase API Key

1. Log in to your Metabase instance as an administrator
2. Go to Settings > Admin settings > API Keys
3. Create a new API key with appropriate permissions
4. Copy the generated key for use in the MCP server

## Usage

### Running the MCP Server

After configuration, you can run the MCP server:

```bash
# Using Docker
docker run -p 5001:5000 metabase-mcp

# Manually
python -m src.server.mcp_server
```

### Available Tools

The MCP server provides the following tools to AI assistants:

1. **list_databases**: List all databases configured in Metabase
2. **get_database_metadata**: Get detailed metadata for a specific database
3. **visualize_database_relationships**: Generate a visual representation of database relationships
4. **list_actions**: List all actions configured in Metabase
5. **get_action_details**: Get detailed information about a specific action
6. **execute_action**: Execute a Metabase action with parameters

### Testing Tools via Web Interface

The web interface provides a testing area for each tool:

1. **List Databases**: View all databases configured in Metabase
2. **Get Database Metadata**: View detailed schema information for a database
3. **Visualize Database Relationships**: Generate a visual representation of table relationships
4. **List Actions**: View all actions configured in Metabase
5. **Get Action Details**: View detailed information about a specific action
6. **Execute Action**: Test executing an action with parameters

## Security Considerations

- API keys are stored encrypted at rest
- The web interface never displays API keys in plain text
- All API requests use HTTPS when configured with a secure Metabase URL
- The server should be deployed behind a secure proxy in production environments

## Development

### Project Structure

```
metabase-mcp/
├── src/
│   ├── api/            # Metabase API client
│   ├── config/         # Configuration management
│   ├── server/         # MCP and web servers
│   └── tools/          # Tool implementations
├── templates/          # Web interface templates
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile          # Docker build configuration
├── requirements.txt    # Python dependencies
└── README.md           # Documentation
```

### Adding New Tools

To add a new tool:

1. Implement the tool function in `src/tools/`
2. Register the tool in `src/server/mcp_server.py`
3. Add a testing interface in `templates/config.html` (optional)
4. Add a route in `src/server/web_interface.py` (if adding a testing interface)

## Troubleshooting

### Common Issues

- **Connection Failed**: Ensure your Metabase URL is correct and accessible
- **Authentication Error**: Verify your API key has the necessary permissions
- **Docker Network Issues**: When using Docker, ensure proper network configuration

### Logs

Check the logs for detailed error information:

```bash
# Docker logs
docker logs metabase-mcp

# Manual execution logs
# Logs are printed to the console
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.


