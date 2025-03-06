import os
import base64
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration class
class Config:
    # Secret key for encryption (generate once and store securely)
    # In production, this should be set as an environment variable
    SECRET_KEY = os.environ.get("SECRET_KEY") or Fernet.generate_key().decode()
    
    # Metabase settings
    METABASE_URL = os.environ.get("METABASE_URL", "http://localhost:3000")
    _METABASE_API_KEY = os.environ.get("METABASE_API_KEY", "")
    
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
    def encrypt_api_key(cls, api_key):
        """Encrypt the API key"""
        if not api_key:
            return ""
        
        cipher_suite = Fernet(cls.SECRET_KEY.encode())
        encrypted_key = cipher_suite.encrypt(api_key.encode())
        return base64.urlsafe_b64encode(encrypted_key).decode()
    
    @classmethod
    def decrypt_api_key(cls, encrypted_key):
        """Decrypt the API key"""
        if not encrypted_key:
            return ""
        
        try:
            cipher_suite = Fernet(cls.SECRET_KEY.encode())
            decoded = base64.urlsafe_b64decode(encrypted_key.encode())
            decrypted_key = cipher_suite.decrypt(decoded)
            return decrypted_key.decode()
        except Exception:
            # If decryption fails, return empty string
            return ""
    
    @classmethod
    def save_metabase_config(cls, metabase_url, api_key):
        """Save Metabase configuration to .env file"""
        # Encrypt the API key before saving
        encrypted_key = cls.encrypt_api_key(api_key)
        
        with open(cls.CONFIG_FILE, 'w') as f:
            f.write(f"METABASE_URL={metabase_url}\n")
            f.write(f"METABASE_API_KEY={encrypted_key}\n")
            f.write(f"SECRET_KEY={cls.SECRET_KEY}\n")
        
        # Update current environment
        os.environ['METABASE_URL'] = metabase_url
        os.environ['METABASE_API_KEY'] = encrypted_key
        
        # Update class attributes
        cls.METABASE_URL = metabase_url
        cls._METABASE_API_KEY = encrypted_key

    @classmethod
    def get_metabase_url(cls):
        """Get the current Metabase URL, refreshing from environment if needed"""
        cls.METABASE_URL = os.environ.get("METABASE_URL", cls.METABASE_URL)
        return cls.METABASE_URL
    
    @classmethod
    def get_metabase_api_key(cls):
        """Get the current Metabase API key, decrypting it first"""
        encrypted_key = os.environ.get("METABASE_API_KEY", cls._METABASE_API_KEY)
        return cls.decrypt_api_key(encrypted_key) 