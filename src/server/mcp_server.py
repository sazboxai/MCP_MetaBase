from mcp.server.fastmcp import FastMCP
from src.config.settings import Config
from src.tools.metabase_tools import list_databases, get_database_metadata, db_overview, table_detail, visualize_database_relationships, run_database_query
from src.tools.metabase_action_tools import list_actions, get_action_details, execute_action

def create_mcp_server():
    """Create and configure an MCP server instance."""
    mcp = FastMCP(Config.MCP_NAME)
    
    # Register database tools
    mcp.tool(
        description="List all databases configured in Metabase"
    )(list_databases)
    
    mcp.tool(
        description="Get detailed metadata for a specific database"
    )(get_database_metadata)
    
    mcp.tool(
        description="Get a high-level overview of all tables in a database"
    )(db_overview)

    mcp.tool(
        description="Get detailed information about a specific table"
    )(table_detail)

    mcp.tool(
        description="Generate a visual representation of database relationships"
    )(visualize_database_relationships)

    mcp.tool(
        description="Run a read-only SQL query against a database"
    )(run_database_query)

    # Register action tools
    mcp.tool(
        description="List all actions configured in Metabase"
    )(list_actions)

    mcp.tool(
        description="Get detailed information about a specific action"
    )(get_action_details)

    mcp.tool(
        description="Execute a Metabase action with parameters"
    )(execute_action)
    
    return mcp

def run_mcp_server():
    """Run the MCP server"""
    mcp = create_mcp_server()
    mcp.run(transport='stdio')

if __name__ == "__main__":
    run_mcp_server() 