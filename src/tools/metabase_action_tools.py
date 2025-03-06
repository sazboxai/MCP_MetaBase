from src.api.metabase import MetabaseAPI
from typing import Dict, Any

async def list_actions() -> str:
    """
    List all actions configured in Metabase.
    
    Returns:
        A formatted string with information about all configured actions.
    """
    # Check Metabase version
    version_info = await MetabaseAPI.get_request("version")
    version = "unknown"
    if version_info and not "error" in version_info:
        version = version_info.get("version", "unknown")
    
    response = await MetabaseAPI.get_actions()
    
    if response is None or "error" in response:
        error_message = response.get('message', 'Unknown error') if response else 'No response'
        return f"Error fetching actions: {error_message}"
    
    if not response:
        return "No actions found in Metabase. You may need to create some actions first."
    
    result = "## Actions in Metabase\n\n"
    for action in response:
        result += f"- **ID**: {action.get('id')}\n"
        result += f"  **Name**: {action.get('name')}\n"
        result += f"  **Type**: {action.get('type')}\n"
        result += f"  **Model ID**: {action.get('model_id')}\n"
        result += f"  **Created At**: {action.get('created_at')}\n\n"
    
    return result

async def get_action_details(action_id: int) -> str:
    """
    Get detailed information about a specific action.
    
    Args:
        action_id: The ID of the action to fetch
        
    Returns:
        A formatted string with the action's details.
    """
    response = await MetabaseAPI.get_request(f"action/{action_id}")
    
    if response is None or "error" in response:
        return f"Error fetching action details: {response.get('message', 'Unknown error')}"
    
    result = f"## Action: {response.get('name')}\n\n"
    result += f"**ID**: {response.get('id')}\n"
    result += f"**Type**: {response.get('type')}\n"
    result += f"**Model ID**: {response.get('model_id')}\n"
    result += f"**Database ID**: {response.get('database_id')}\n"
    result += f"**Created At**: {response.get('created_at')}\n\n"
    
    # Add parameters if available
    parameters = response.get('parameters', [])
    if parameters:
        result += f"### Parameters ({len(parameters)})\n\n"
        for param in parameters:
            result += f"- **{param.get('id')}**: {param.get('name')}\n"
            result += f"  - Type: {param.get('type')}\n"
            if param.get('required'):
                result += f"  - Required: {param.get('required')}\n"
            if param.get('default'):
                result += f"  - Default: {param.get('default')}\n"
        result += "\n"
    
    return result

async def execute_action(action_id: int, parameters: Dict[str, Any] = None) -> str:
    """
    Execute a Metabase action with the provided parameters.
    
    Args:
        action_id: The ID of the action to execute
        parameters: Dictionary of parameter values to use when executing the action
        
    Returns:
        A formatted string with the execution results.
    """
    if parameters is None:
        parameters = {}
    
    # First, verify the action exists
    action_details = await MetabaseAPI.get_request(f"action/{action_id}")
    if "error" in action_details:
        return f"Error: Action with ID {action_id} not found. {action_details.get('message', '')}"
    
    # Execute the action
    response = await MetabaseAPI.make_request(
        f"action/{action_id}/execute", 
        method="POST",
        data={"parameters": parameters}
    )
    
    if response is None or "error" in response:
        error_msg = response.get('message', 'Unknown error') if response else 'No response'
        return f"Error executing action: {error_msg}"
    
    # Format the successful response
    result = f"## Action Execution Results for '{action_details.get('name')}'\n\n"
    
    # Format the response based on what was returned
    if isinstance(response, dict):
        for key, value in response.items():
            result += f"**{key}**: {value}\n"
    elif isinstance(response, list):
        result += f"Returned {len(response)} rows\n\n"
        if response and len(response) > 0:
            # Get keys from first item
            keys = response[0].keys()
            # Create table header
            result += "| " + " | ".join(keys) + " |\n"
            result += "| " + " | ".join(["---" for _ in keys]) + " |\n"
            # Add rows
            for row in response[:10]:  # Limit to first 10 rows
                result += "| " + " | ".join([str(row.get(k, "")) for k in keys]) + " |\n"
            
            if len(response) > 10:
                result += "\n_Showing first 10 rows of results_\n"
    else:
        result += f"Result: {response}\n"
    
    return result

async def check_actions_enabled() -> bool:
    """Check if actions are enabled in this Metabase instance"""
    # Check settings endpoint to see if actions are enabled
    settings = await MetabaseAPI.get_request("setting")
    
    if settings and not "error" in settings:
        for setting in settings:
            if setting.get("key") == "enable-actions" or setting.get("key") == "actions-enabled":
                return setting.get("value") == "true" or setting.get("value") == True
    
    # If we can't determine from settings, try to fetch actions as a test
    actions = await MetabaseAPI.get_actions()
    return not (actions is None or "error" in actions) 