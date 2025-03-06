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