# Developer Guide for Metabase MCP Server

This guide provides detailed information for developers who want to extend or modify the Metabase MCP Server.

## Architecture Overview

The Metabase MCP Server consists of several key components:

1. **MCP Server**: Implements the Model Control Protocol to expose tools to AI assistants
2. **Web Interface**: Provides a configuration and testing UI
3. **Metabase API Client**: Handles communication with the Metabase API
4. **Tool Implementations**: Functions that implement specific capabilities
5. **Configuration Management**: Handles settings and secure storage of credentials

### Component Interactions

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  AI Model   │     │ Web Browser │     │  Developer  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌──────────────────────────────────────────────────────┐
│                  Metabase MCP Server                  │
│                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  MCP Server │  │Web Interface│  │  Tools API  │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                │                │          │
│         └────────────────┼────────────────┘          │
│                          │                           │
│                  ┌───────┴───────┐                   │
│                  │ Metabase API  │                   │
│                  │    Client     │                   │
│                  └───────┬───────┘                   │
└──────────────────────────┼──────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ Metabase Server │
                  └─────────────────┘
```

## Code Structure

### Key Files and Their Purposes

- `src/api/metabase.py`: Metabase API client implementation
- `src/config/settings.py`: Configuration management and secure storage
- `src/server/mcp_server.py`: MCP server implementation
- `src/server/web_interface.py`: Web interface for configuration and testing
- `src/tools/metabase_tools.py`: Database-related tool implementations
- `src/tools/metabase_action_tools.py`: Action-related tool implementations
- `templates/config.html`: HTML template for the web interface

## Adding New Features

### Adding a New Tool

1. **Implement the Tool Function**:

```python
# In src/tools/metabase_tools.py or a new file
async def my_new_tool(param1: str, param2: int) -> str:
    """
    Description of what the tool does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        A formatted string with the result
    """
    # Implementation
    result = await MetabaseAPI.some_method(param1, param2)
    
    # Format the result
    formatted_result = f"## Result\n\n{result}"
    
    return formatted_result
```

2. **Register the Tool in the MCP Server**:

```python
# In src/server/mcp_server.py
from src.tools.metabase_tools import my_new_tool

# In create_mcp_server function
mcp.tool(
    description="Description of what the tool does",
    examples=["Example usage 1", "Example usage 2"],
    input_schema={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Description of param1"
            },
            "param2": {
                "type": "integer",
                "description": "Description of param2"
            }
        },
        "required": ["param1", "param2"]
    }
)(my_new_tool)
```

3. **Add a Testing Interface (Optional)**:

```html
<!-- In templates/config.html -->
<h3>My New Tool</h3>
<div class="form-group">
    <label for="param1">Parameter 1:</label>
    <input type="text" id="param1" placeholder="Enter param1">
</div>
<div class="form-group">
    <label for="param2">Parameter 2:</label>
    <input type="text" id="param2" placeholder="Enter param2">
</div>
<button type="button" id="test-my-new-tool">Test My New Tool</button>
<div id="my-new-tool-result" class="result-area"></div>

<!-- Add JavaScript for the button -->
<script>
document.getElementById('test-my-new-tool').addEventListener('click', function() {
    const param1 = document.getElementById('param1').value;
    const param2 = document.getElementById('param2').value;
    
    if (!param1 || !param2) {
        alert('Please enter all parameters');
        return;
    }
    
    const resultArea = document.getElementById('my-new-tool-result');
    resultArea.style.display = 'block';
    resultArea.innerHTML = 'Processing...';
    
    fetch('/test_my_new_tool', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `param1=${param1}&param2=${param2}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            resultArea.innerHTML = data.result;
        } else {
            resultArea.innerHTML = `<div class="error">${data.error}</div>`;
        }
    })
    .catch(error => {
        resultArea.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    });
});
</script>
```

4. **Add a Route in the Web Interface**:

```python
# In src/server/web_interface.py
@app.route('/test_my_new_tool', methods=['POST'])
async def test_my_new_tool():
    """Test the my_new_tool tool"""
    from src.tools.metabase_tools import my_new_tool
    
    param1 = request.form.get('param1')
    param2 = request.form.get('param2')
    
    if not param1 or not param2 or not param2.isdigit():
        return jsonify({'success': False, 'error': 'Valid parameters are required'})
    
    try:
        result = await my_new_tool(param1, int(param2))
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```

### Adding a New Metabase API Endpoint

1. **Add a Method to the MetabaseAPI Class**:

```python
# In src/api/metabase.py
@classmethod
async def some_method(cls, param1: str, param2: int):
    """Description of what this method does"""
    endpoint = f"some/endpoint/{param1}/{param2}"
    return await cls.get_request(endpoint)
```

## Security Best Practices

### API Key Handling

- Always use the encryption methods in `Config` for storing sensitive data
- Never log or display API keys in plain text
- Use environment variables for production deployments

### Input Validation

- Validate all user inputs before passing to the Metabase API
- Sanitize parameters to prevent injection attacks
- Use type hints and validate types at runtime

### Error Handling

- Catch and handle exceptions appropriately
- Provide meaningful error messages without exposing sensitive information
- Log errors for debugging but redact sensitive data

## Testing

### Manual Testing

Use the web interface to test new functionality:

1. Configure the server with valid Metabase credentials
2. Navigate to the testing section for your tool
3. Enter test parameters and verify the results

### Automated Testing

Add unit tests for new functionality:

```python
# In tests/test_tools.py
import pytest
from src.tools.metabase_tools import my_new_tool
from unittest.mock import patch

@pytest.mark.asyncio
async def test_my_new_tool():
    # Mock the API response
    with patch('src.api.metabase.MetabaseAPI.some_method') as mock_method:
        mock_method.return_value = {"test": "data"}
        
        # Call the tool
        result = await my_new_tool("test", 123)
        
        # Verify the result
        assert "test" in result
        assert "data" in result
        
        # Verify the API was called correctly
        mock_method.assert_called_once_with("test", 123)
```

## Deployment

### Docker Deployment

Build and push a new Docker image:

```bash
docker build -t yourusername/metabase-mcp:latest .
docker push yourusername/metabase-mcp:latest
```

### Environment Variables

Configure the following environment variables for deployment:

- `METABASE_URL`: URL of the Metabase instance
- `METABASE_API_KEY`: API key for Metabase (encrypted)
- `SECRET_KEY`: Secret key for encryption
- `FLASK_HOST`: Host to bind the web interface (default: 0.0.0.0)
- `FLASK_PORT`: Port for the web interface (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: False)

## Troubleshooting Development Issues

### Common Development Errors

1. **API Changes**: Metabase API may change between versions. Check the Metabase API documentation for your version.

2. **Async/Await**: Ensure all async functions are properly awaited and that you're using the correct event loop.

3. **Docker Networking**: When testing with Docker, use `host.docker.internal` to access services on the host machine.

### Debugging Tips

1. Add print statements for debugging:
```python
print(f"Debug: {variable}")
```

2. Use the Python debugger:
```python
import pdb; pdb.set_trace()
```

3. Check the logs for error messages:
```bash
docker logs metabase-mcp
```

## Performance Optimization

1. **Caching**: Consider caching frequently accessed data:
```python
# Simple in-memory cache
_cache = {}

async def get_with_cache(key, fetch_func, ttl=300):
    """Get from cache or fetch and cache"""
    now = time.time()
    if key in _cache and _cache[key]['expires'] > now:
        return _cache[key]['data']
    
    data = await fetch_func()
    _cache[key] = {
        'data': data,
        'expires': now + ttl
    }
    return data
```

2. **Batch Requests**: Combine multiple requests when possible to reduce API calls.

3. **Async Processing**: Use asyncio.gather for parallel processing:
```python
results = await asyncio.gather(
    MetabaseAPI.get_request("endpoint1"),
    MetabaseAPI.get_request("endpoint2"),
    MetabaseAPI.get_request("endpoint3")
)
``` 