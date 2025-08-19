import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Get the API key from environment variables
# In a real production system, you might fetch this from a secure vault or database
API_KEY = os.getenv("SERVER_API_KEY")
if not API_KEY:
    raise RuntimeError("SERVER_API_KEY environment variable not set. API cannot start.")

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency that checks for a valid API key in the request header.
    """
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )