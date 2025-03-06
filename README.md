# Metabase MCP Server

A Model Context Protocol (MCP) server for interacting with the Metabase API, providing tools for AI assistants to work with Metabase.

## Features

- Database tools:
  - List all databases configured in Metabase
  - View detailed metadata for a specific database
- Action tools:
  - List all actions configured in Metabase
  - View detailed information about a specific action
  - Execute actions with parameters
- Web interface for configuration and testing

## Setup and Usage

### Build the Docker Image 

```docker build -t metabase-mcp .```

### Run the Docker Container

```docker run -d -p 8000:8000 metabase-mcp```

hen visit http://localhost:5000 in your browser to:
- Configure your Metabase URL and API key
- Test your connection to Metabase
- Test the MCP tools

### Run the MCP Server

After configuration, run the MCP server:
```docker run -e METABASE_URL=http://your-metabase-url \
-e METABASE_API_KEY=your_api_key \
metabase-mcp mcp```

### Integrate with Claude for Desktop

1. Configure Claude for Desktop by editing the configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add the following configuration:
```
{
"mcpServers": {
"metabase": {
"command": "docker",
"args": [
"run",
"-e", "METABASE_URL=http://your-metabase-url",
"-e", "METABASE_API_KEY=your_api_key",
"metabase-mcp",
"mcp"
]
}
}
}
```
3. Restart Claude for Desktop and use the MCP tools to interact with Metabase.

## Available Tools

- `list_databases`: Lists all databases configured in Metabase
- `get_database_metadata`: Gets detailed metadata for a specific database
- `list_actions`: Lists all actions configured in Metabase
- `get_action_details`: Gets detailed information about a specific action
- `execute_action`: Executes an action with parameters

## Environment Variables

- `METABASE_URL`: The URL of your Metabase instance
- `METABASE_API_KEY`: Your Metabase API key


