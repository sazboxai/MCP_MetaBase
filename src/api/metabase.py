import httpx
from typing import Dict, Any, Optional
from src.config.settings import Config

class MetabaseAPI:
    """Class for interacting with the Metabase API"""
    
    @staticmethod
    async def make_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Any:
        """Make a request to the Metabase API with proper error handling.
        
        Args:
            endpoint: API endpoint to call (without the base URL)
            method: HTTP method to use (GET, POST, etc.)
            data: Optional JSON data to send with the request
            
        Returns:
            JSON response from the API or error dict
        """
        # Get fresh values from config using the getter methods
        metabase_url = Config.get_metabase_url()
        api_key = Config.get_metabase_api_key()
        
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        
        url = f"{metabase_url}/api/{endpoint.lstrip('/')}"
        print(f"Making request to: {url}")  # Debugging
        
        async with httpx.AsyncClient() as client:
            try:
                if method == "GET":
                    response = await client.get(url, headers=headers, timeout=30.0)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=data, timeout=30.0)
                elif method == "PUT":
                    response = await client.put(url, headers=headers, json=data, timeout=30.0)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers, timeout=30.0)
                else:
                    return {"error": f"Unsupported HTTP method: {method}"}
                
                response.raise_for_status()
                
                # Try to parse as JSON, but handle non-JSON responses
                try:
                    return response.json()
                except ValueError:
                    # If response is not JSON, return as error with the text content
                    return {"error": "Non-JSON response", "message": response.text}
                
            except httpx.HTTPStatusError as e:
                # Try to get JSON error response
                try:
                    error_json = e.response.json()
                    return {"error": f"HTTP error: {e.response.status_code}", "message": str(error_json)}
                except ValueError:
                    # If error is not JSON, return the text
                    return {"error": f"HTTP error: {e.response.status_code}", "message": e.response.text}
            except Exception as e:
                return {"error": "Failed to make request", "message": str(e)}
    
    @classmethod
    async def get_request(cls, endpoint: str) -> Any:
        """Shorthand for GET requests"""
        return await cls.make_request(endpoint, method="GET")
    
    @classmethod
    async def post_request(cls, endpoint: str, data: Dict) -> Any:
        """Shorthand for POST requests"""
        return await cls.make_request(endpoint, method="POST", data=data)
    
    @classmethod
    async def test_connection(cls) -> tuple:
        """Test connection to Metabase API"""
        try:
            response = await cls.get_request("database")
            if response is None or "error" in response:
                return False, f"Connection failed: {response.get('message', 'Unknown error')}"
            return True, "Connection successful!"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"
    
    @classmethod
    async def get_databases(cls):
        """Get list of all databases"""
        response = await cls.get_request("database")
        
        # Handle case where response might be a string
        if isinstance(response, str):
            return {"error": "Unexpected string response", "message": response}
        
        # Check if response is a dictionary with a 'data' key (new Metabase API format)
        if isinstance(response, dict) and 'data' in response:
            print(f"Found 'data' key in response with {len(response['data'])} databases")
            return response['data']  # Return just the list of databases
        
        return response
    
    @classmethod
    async def get_database_metadata(cls, database_id: int):
        """Get metadata for a specific database"""
        return await cls.get_request(f"database/{database_id}/metadata")
    
    @classmethod
    async def get_actions(cls):
        """Get list of all actions with support for different Metabase versions"""
        # Try the standard endpoint first
        response = await cls.get_request("action")
        
        # If that fails, try alternative endpoints
        if response is None or "error" in response:
            # Try the legacy endpoint (some older Metabase versions)
            response_legacy = await cls.get_request("api/action")
            if response_legacy and not "error" in response_legacy:
                return response_legacy
            
            # If all attempts failed, return the original error
            return response
        
        return response
    
    @classmethod
    async def get_action(cls, action_id: int):
        """Get details for a specific action"""
        return await cls.get_request(f"action/{action_id}")
    
    @classmethod
    async def execute_action(cls, action_id: int, parameters: Dict = None):
        """Execute an action with parameters"""
        if parameters is None:
            parameters = {}
        
        # Validate action_id
        if not isinstance(action_id, int) or action_id <= 0:
            return {"error": "Invalid action ID", "message": "Action ID must be a positive integer"}
        
        # Sanitize parameters
        sanitized_params = {}
        for key, value in parameters.items():
            sanitized_params[str(key)] = value
        
        return await cls.post_request(f"action/{action_id}/execute", {"parameters": sanitized_params})
    
    @classmethod
    async def get_table_metadata(cls, table_id: int):
        """Get detailed metadata for a specific table"""
        return await cls.get_request(f"table/{table_id}/query_metadata")
    
    @classmethod
    async def get_field_metadata(cls, field_id: int):
        """Get detailed metadata for a specific field"""
        return await cls.get_request(f"field/{field_id}")
    
    @classmethod
    async def get_database_schema(cls, database_id: int):
        """Get the database schema with relationships between tables"""
        # First get the basic metadata
        metadata = await cls.get_database_metadata(database_id)
        
        if metadata is None or "error" in metadata:
            return metadata
        
        # For each table, get detailed metadata including foreign keys
        tables = metadata.get('tables', [])
        enhanced_tables = []
        
        for table in tables:
            table_id = table.get('id')
            if table_id:
                table_details = await cls.get_table_metadata(table_id)
                if table_details and not "error" in table_details:
                    enhanced_tables.append(table_details)
                else:
                    enhanced_tables.append(table)
            else:
                enhanced_tables.append(table)
        
        # Replace tables with enhanced versions
        metadata['tables'] = enhanced_tables
        return metadata
    
    @classmethod
    async def run_query(cls, database_id: int, query_string: str, row_limit: int = 5):
        """Run a native query against a database with a row limit
        
        Args:
            database_id: The ID of the database to query
            query_string: The SQL query to execute
            row_limit: Maximum number of rows to return (default: 5)
            
        Returns:
            Query results or error message
        """
        # Remove trailing semicolons that can cause issues with Metabase API
        query_string = query_string.strip()
        if query_string.endswith(';'):
            query_string = query_string[:-1]
        
        # Ensure the query has a LIMIT clause for safety
        query_string = cls._ensure_query_limit(query_string, row_limit)
        
        # Prepare the query payload
        payload = {
            "database": database_id,
            "type": "native",
            "native": {
                "query": query_string,
                "template-tags": {}
            }
        }
        
        # Execute the query
        response = await cls.post_request("dataset", payload)
        
        # Improved error handling for Metabase error responses
        if response and isinstance(response, dict) and "error" in response:
            error_data = response.get("error")
            
            # Check for common error patterns in Metabase responses
            if isinstance(error_data, str) and "does not exist" in error_data:
                # This is likely a SQL syntax error from the database
                return {"error": "SQL Error", "message": error_data}
            
            # If the error message contains additional info
            message = response.get("message", "Unknown error")
            if isinstance(message, dict) and "data" in message:
                if "errors" in message["data"]:
                    return {"error": "SQL Error", "message": message["data"]["errors"]}
        
        return response
    
    @staticmethod
    def _ensure_query_limit(query: str, limit: int) -> str:
        """Ensure the query has a LIMIT clause
        
        This is a simple implementation and may not work for all SQL dialects
        or complex queries. It's a basic safety measure.
        """
        # Convert to uppercase for case-insensitive matching
        query_upper = query.upper()
        
        # Check if query already has a LIMIT clause
        if "LIMIT" in query_upper:
            return query
        
        # Add LIMIT clause
        return f"{query} LIMIT {limit}" 