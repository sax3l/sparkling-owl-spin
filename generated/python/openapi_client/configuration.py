"""OpenAPI Client Configuration"""

class Configuration:
    """Configuration class for OpenAPI client"""
    
    def __init__(self):
        self.host = "http://localhost:8000"
        self.api_key = {}
        self.api_key_prefix = {}
        self.username = None
        self.password = None
        self.access_token = None
        self.server_index = 0
        self.server_variables = {}
        self.server_operation_index = {}
        self.server_operation_variables = {}
        
    def get_api_key_with_prefix(self, identifier):
        """Get API key with prefix"""
        key = self.api_key.get(identifier)
        if key:
            prefix = self.api_key_prefix.get(identifier)
            if prefix:
                return f"{prefix} {key}"
            return key
        return None
