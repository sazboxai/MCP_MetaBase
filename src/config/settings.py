import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration class
class Config:
    # Metabase settings
    METABASE_URL = os.environ.get("METABASE_URL", "http://localhost:3000")
    METABASE_API_KEY = os.environ.get("METABASE_API_KEY", "")
    
    # Flask settings
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
    FLASK_PORT = int(os.environ.get("FLASK_PORT", "5000"))
    
    # MCP settings
    MCP_NAME = os.environ.get("MCP_NAME", "metabase")
    
    # File paths
    CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
    TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates')
    
    @classmethod
    def save_metabase_config(cls, metabase_url, api_key):
        """Save Metabase configuration to .env file"""
        with open(cls.CONFIG_FILE, 'w') as f:
            f.write(f"METABASE_URL={metabase_url}\n")
            f.write(f"METABASE_API_KEY={api_key}\n")
        
        # Update current environment
        os.environ['METABASE_URL'] = metabase_url
        os.environ['METABASE_API_KEY'] = api_key
        
        # Update class attributes
        cls.METABASE_URL = metabase_url
        cls.METABASE_API_KEY = api_key

    @classmethod
    def get_metabase_url(cls):
        """Get the current Metabase URL, refreshing from environment if needed"""
        cls.METABASE_URL = os.environ.get("METABASE_URL", cls.METABASE_URL)
        return cls.METABASE_URL
    
    @classmethod
    def get_metabase_api_key(cls):
        """Get the current Metabase API key, refreshing from environment if needed"""
        cls.METABASE_API_KEY = os.environ.get("METABASE_API_KEY", cls.METABASE_API_KEY)
        return cls.METABASE_API_KEY 