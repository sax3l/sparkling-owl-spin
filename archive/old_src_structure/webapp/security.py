import os
from fastapi import Security, HTTPException, status, Depends, Request
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session
from src.database.manager import get_db
from src.database.models import UserAPIKey, OAuthClient
from src.utils.auth_utils import decode_access_token, get_password_hash, verify_password, get_user_scopes
import logging

logger = logging.getLogger(__name__)

# API Key authentication
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# OAuth2 authentication (for client credentials flow)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/oauth/token", auto_error=False)

async def get_current_tenant_id(request: Request) -> UUID:
    """
    Dependency to extract the tenant_id from the request state.
    This will be set by either `get_api_key` or `get_current_user_from_jwt`.
    """
    tenant_id = getattr(request.state, "tenant_id", None)
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not determine tenant ID. Authentication required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return tenant_id

async def get_api_key(
    request: Request,
    api_key: str = Security(api_key_header),
    db: Session = Depends(get_db)
) -> UserAPIKey:
    """
    Dependency that checks for a valid API key in the request header.
    Sets request.state.tenant_id and request.state.api_key_id.
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check for API key prefixes (sk_live_, sk_test_)
    if api_key.startswith("sk_live_"):
        is_test_key = False
        key_value = api_key[len("sk_live_"):]
    elif api_key.startswith("sk_test_"):
        is_test_key = True
        key_value = api_key[len("sk_test_"):]
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key prefix. Must be 'sk_live_' or 'sk_test_'.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # In a real system, you'd hash the incoming key_value and compare to stored hash
    # For simplicity, we'll assume direct lookup for now, but a hash comparison is safer.
    # You should hash `key_value` and query `api_key_hash` column.
    db_api_key = db.query(UserAPIKey).filter(UserAPIKey.api_key_hash == get_password_hash(key_value)).first() # This is a simplification, should hash and compare
    
    if not db_api_key or not db_api_key.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last_used_at
    db_api_key.last_used_at = datetime.datetime.utcnow()
    db.commit()

    request.state.tenant_id = db_api_key.tenant_id
    request.state.api_key_id = db_api_key.id
    request.state.scopes = db_api_key.permissions # API keys have explicit permissions

    return db_api_key

async def get_current_user_from_jwt(
    request: Request,
    token: Optional[str] = Security(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Dependency that decodes a JWT token and retrieves user/client information.
    Sets request.state.tenant_id and request.state.scopes.
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    tenant_id = payload.get("tenant_id")
    if not tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing tenant ID",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For OAuth2 Client Credentials, scopes are directly in the client definition
    # For user tokens, scopes are derived from roles
    if payload.get("client_id"): # This is an OAuth client token
        client = db.query(OAuthClient).filter(OAuthClient.client_id == payload["client_id"]).first()
        if not client:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="OAuth client not found")
        scopes = client.scopes
    else: # This is a user token (assuming user_id is present)
        user_id = payload.get("sub") # 'sub' is typically the user ID
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing user ID")
        scopes = get_user_scopes(db, UUID(user_id)) # Get scopes based on user's roles

    request.state.tenant_id = UUID(tenant_id)
    request.state.scopes = scopes
    request.state.user_id = UUID(payload.get("sub")) # Store user_id if available

    return payload

async def get_current_active_user(
    api_key_auth: Optional[UserAPIKey] = Depends(get_api_key),
    jwt_auth: Optional[Dict[str, Any]] = Depends(get_current_user_from_jwt)
) -> Dict[str, Any]:
    """
    Combines API Key and JWT authentication.
    Prioritizes API Key if present.
    """
    if api_key_auth:
        return {"tenant_id": api_key_auth.tenant_id, "scopes": api_key_auth.permissions, "auth_type": "api_key"}
    elif jwt_auth:
        return {"tenant_id": jwt_auth["tenant_id"], "scopes": jwt_auth["scopes"], "auth_type": "jwt"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

def authorize_with_scopes(required_scopes: List[str]):
    """
    Dependency to check if the authenticated user/client has the required scopes.
    """
    async def _authorize(request: Request):
        user_scopes = getattr(request.state, "scopes", [])
        if not user_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No scopes found for authenticated entity. Access denied.",
            )
        
        if not has_scope(required_scopes, user_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scopes: {', '.join(required_scopes)}",
            )
        return True
    return _authorize