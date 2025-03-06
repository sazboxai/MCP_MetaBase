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
    Get metadata for a specific database in Metabase, including table relationships.
    
    Args:
        database_id: The ID of the database to fetch metadata for
        
    Returns:
        A formatted string with the database's metadata including tables, fields, and relationships.
    """
    response = await MetabaseAPI.get_database_schema(database_id)
    
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
    
    # Create a map of table IDs to names for reference
    table_map = {table.get('id'): table.get('name') for table in tables}
    
    for table in tables:
        result += f"#### {table.get('name')}\n"
        result += f"**ID**: {table.get('id')}\n"
        result += f"**Schema**: {table.get('schema', 'N/A')}\n"
        result += f"**Description**: {table.get('description', 'No description')}\n\n"
        
        # Add fields for this table
        fields = table.get('fields', [])
        result += f"##### Fields ({len(fields)})\n\n"
        
        # Track foreign keys for relationship section
        foreign_keys = []
        
        for field in fields:
            result += f"- **{field.get('name')}**\n"
            result += f"  - Type: {field.get('base_type')}\n"
            result += f"  - Description: {field.get('description', 'No description')}\n"
            
            # Check if this is a foreign key
            fk_target_field_id = field.get('fk_target_field_id')
            if fk_target_field_id:
                foreign_keys.append({
                    'source_field': field.get('name'),
                    'source_field_id': field.get('id'),
                    'target_field_id': fk_target_field_id
                })
                result += f"  - **Foreign Key** to another table\n"
            
            if field.get('special_type'):
                result += f"  - Special Type: {field.get('special_type')}\n"
        
        # Add relationships section if there are foreign keys
        if foreign_keys:
            result += "\n##### Relationships\n\n"
            
            for fk in foreign_keys:
                # Find target field information
                target_field_info = "Unknown field"
                target_table_name = "Unknown table"
                
                # Search all tables for the target field
                for t in tables:
                    for f in t.get('fields', []):
                        if f.get('id') == fk['target_field_id']:
                            target_field_info = f.get('name')
                            target_table_name = t.get('name')
                            break
                
                result += f"- **{fk['source_field']}** → **{target_table_name}.{target_field_info}**\n"
        
        result += "\n"
    
    # Add a visual representation of relationships
    result += "### Database Relationships\n\n"
    result += "```\n"
    
    # Create a simple text-based diagram of relationships
    for table in tables:
        table_name = table.get('name')
        result += f"{table_name}\n"
        
        for field in table.get('fields', []):
            fk_target_field_id = field.get('fk_target_field_id')
            if fk_target_field_id:
                # Find target field information
                for t in tables:
                    for f in t.get('fields', []):
                        if f.get('id') == fk_target_field_id:
                            target_field = f.get('name')
                            target_table = t.get('name')
                            result += f"  └── {field.get('name')} → {target_table}.{target_field}\n"
        
        result += "\n"
    
    result += "```\n"
    
    return result

async def visualize_database_relationships(database_id: int) -> str:
    """
    Generate a visual representation of database relationships.
    
    Args:
        database_id: The ID of the database to visualize
        
    Returns:
        A formatted string with a visualization of table relationships.
    """
    response = await MetabaseAPI.get_database_schema(database_id)
    
    if response is None or "error" in response:
        return f"Error fetching database schema: {response.get('message', 'Unknown error')}"
    
    tables = response.get('tables', [])
    if not tables:
        return "No tables found in this database."
    
    result = f"## Database Relationship Diagram for: {response.get('name')}\n\n"
    
    # Generate a text-based ER diagram
    result += "```\n"
    
    # First list all tables
    result += "Tables:\n"
    for table in tables:
        result += f"  {table.get('name')}\n"
    
    result += "\nRelationships:\n"
    
    # Then show all relationships
    for table in tables:
        table_name = table.get('name')
        
        for field in table.get('fields', []):
            fk_target_field_id = field.get('fk_target_field_id')
            if fk_target_field_id:
                # Find target field information
                for t in tables:
                    for f in t.get('fields', []):
                        if f.get('id') == fk_target_field_id:
                            target_field = f.get('name')
                            target_table = t.get('name')
                            result += f"  {table_name}.{field.get('name')} → {target_table}.{target_field}\n"
    
    result += "```\n\n"
    
    # Add a more detailed description of each relationship
    result += "### Detailed Relationships\n\n"
    
    for table in tables:
        table_name = table.get('name')
        has_relationships = False
        
        for field in table.get('fields', []):
            fk_target_field_id = field.get('fk_target_field_id')
            if fk_target_field_id:
                if not has_relationships:
                    result += f"**{table_name}** has the following relationships:\n\n"
                    has_relationships = True
                
                # Find target field information
                for t in tables:
                    for f in t.get('fields', []):
                        if f.get('id') == fk_target_field_id:
                            target_field = f.get('name')
                            target_table = t.get('name')
                            result += f"- Field **{field.get('name')}** references **{target_table}.{target_field}**\n"
        
        if has_relationships:
            result += "\n"
    
    return result 