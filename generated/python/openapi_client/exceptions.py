"""OpenAPI Client Exceptions"""

class OpenApiException(Exception):
    """Base exception for OpenAPI client"""
    
    def __init__(self, status=None, reason=None, http_resp=None):
        self.status = status
        self.reason = reason
        self.http_resp = http_resp
        
        if self.status is not None:
            self.body = f"({self.status})\nReason: {self.reason}\n"
        else:
            self.body = None
            
    def __str__(self):
        return self.body or "OpenAPI client error"

class ApiException(OpenApiException):
    """API-specific exception"""
    pass

class ApiTypeError(OpenApiException, TypeError):
    """Type error in API calls"""
    pass

class ApiValueError(OpenApiException, ValueError):
    """Value error in API calls"""
    pass
