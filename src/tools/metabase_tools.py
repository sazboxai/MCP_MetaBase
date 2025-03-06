from src.api.metabase import MetabaseAPI
from src.config.settings import Config

async def list_databases() -> str:
    """
    List all databases configured in Metabase.
    
    Returns:
        A formatted string with information about all configured databases.
    """
    response = await MetabaseAPI.get_databases()
    
    # Handle different response types
    if isinstance(response, str):
        return f"Error: Received unexpected string response: {response}"
    
    if response is None:
        return "Error: No response received from Metabase API"
    
    if isinstance(response, dict) and "error" in response:
        return f"Error fetching databases: {response.get('message', 'Unknown error')}"
    
    # If we got a dictionary without an error, try to extract databases
    if isinstance(response, dict) and not isinstance(response, list):
        # Try to find databases in common locations
        if 'data' in response:
            response = response['data']
        elif 'databases' in response:
            response = response['databases']
        elif 'results' in response:
            response = response['results']
        else:
            return f"Error: Unexpected response format: {response}"
    
    if not response:
        return "No databases found in Metabase."
    
    if not isinstance(response, list):
        return f"Error: Expected a list of databases, but got {type(response).__name__}: {response}"
    
    # Now we should have a list of databases
    result = "## Databases in Metabase\n\n"
    
    for db in response:
        # Check if each item is a dictionary
        if not isinstance(db, dict):
            result += f"- Warning: Found non-dictionary item: {db}\n\n"
            continue
            
        # Safely extract values with fallbacks
        db_id = db.get('id', 'Unknown')
        db_name = db.get('name', 'Unnamed')
        db_engine = db.get('engine', 'Unknown')
        db_created = db.get('created_at', 'Unknown')
        
        result += f"- **ID**: {db_id}\n"
        result += f"  **Name**: {db_name}\n"
        result += f"  **Engine**: {db_engine}\n"
        result += f"  **Created At**: {db_created}\n\n"
    
    return result

async def get_database_metadata(database_id: int) -> str:
    """
    Get metadata for a specific database in Metabase.
    
    Args:
        database_id: The ID of the database to fetch metadata for
        
    Returns:
        A formatted string with the database's metadata including tables and fields.
    """
    response = await MetabaseAPI.get_database_metadata(database_id)
    
    if response is None or "error" in response:
        return f"Error fetching database metadata: {response.get('message', 'Unknown error')}"
    
    result = f"## Metadata for Database: {response.get('name')}\n\n"
    
    # Add database details
    result += f"**ID**: {response.get('id')}\n"
    result += f"**Engine**: {response.get('engine')}\n"
    result += f"**Is Sample**: {response.get('is_sample', False)}\n\n"
    
    # Add tables information
    tables = response.get('tables', [])
    result += f"### Tables ({len(tables)})\n\n"
    
    for table in tables:
        result += f"#### {table.get('name')}\n"
        result += f"**ID**: {table.get('id')}\n"
        result += f"**Schema**: {table.get('schema', 'N/A')}\n"
        result += f"**Description**: {table.get('description', 'No description')}\n\n"
        
        # Add fields for this table
        fields = table.get('fields', [])
        result += f"##### Fields ({len(fields)})\n\n"
        
        for field in fields:
            result += f"- **{field.get('name')}**\n"
            result += f"  - Type: {field.get('base_type')}\n"
            result += f"  - Description: {field.get('description', 'No description')}\n"
            if field.get('special_type'):
                result += f"  - Special Type: {field.get('special_type')}\n"
        
        result += "\n"
    
    return result 