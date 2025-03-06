from mcp.server.fastmcp import FastMCP
from src.config.settings import Config
from src.tools.metabase_tools import list_databases, get_database_metadata, visualize_database_relationships
from src.tools.metabase_action_tools import list_actions, get_action_details, execute_action

def create_mcp_server():
    """Create and configure the MCP server"""
    mcp = FastMCP(Config.MCP_NAME)
    
    # Register database tools with improved descriptions and schemas
    mcp.tool(
        description="List all databases configured in Metabase with their IDs, names, and engines",
        examples=["List all the databases in Metabase", "Show me the available databases"]
    )(list_databases)
    
    mcp.tool(
        description="Get detailed metadata for a specific database including tables and fields",
        examples=["Get metadata for database 1", "Show me the schema for database 2"],
        input_schema={
            "type": "object",
            "properties": {
                "database_id": {
                    "type": "integer",
                    "description": "The ID of the database to fetch metadata for"
                }
            },
            "required": ["database_id"]
        }
    )(get_database_metadata)
    
    # Register action tools with improved descriptions and schemas
    mcp.tool(
        description="List all actions configured in Metabase with their IDs, names, and types",
        examples=["List all Metabase actions", "Show me the available actions"]
    )(list_actions)
    
    mcp.tool(
        description="Get detailed information about a specific Metabase action",
        examples=["Get details for action 1", "Show me information about action 2"],
        input_schema={
            "type": "object",
            "properties": {
                "action_id": {
                    "type": "integer",
                    "description": "The ID of the action to fetch details for"
                }
            },
            "required": ["action_id"]
        }
    )(get_action_details)
    
    mcp.tool(
        description="Execute a Metabase action with the provided parameters",
        examples=["Execute action 1 with parameter x=10", "Run action 2 with customer_id=123"],
        input_schema={
            "type": "object",
            "properties": {
                "action_id": {
                    "type": "integer",
                    "description": "The ID of the action to execute"
                },
                "parameters": {
                    "type": "object",
                    "description": "Parameter values to use when executing the action"
                }
            },
            "required": ["action_id"]
        }
    )(execute_action)
    
    mcp.tool(
        description="Visualize relationships between tables in a database",
        examples=["Show relationships in database 1", "Visualize database schema for database 2"],
        input_schema={
            "type": "object",
            "properties": {
                "database_id": {
                    "type": "integer",
                    "description": "The ID of the database to visualize relationships for"
                }
            },
            "required": ["database_id"]
        }
    )(visualize_database_relationships)
    
    return mcp

def run_mcp_server():
    """Run the MCP server"""
    mcp = create_mcp_server()
    mcp.run(transport='stdio')

if __name__ == "__main__":
    run_mcp_server() 