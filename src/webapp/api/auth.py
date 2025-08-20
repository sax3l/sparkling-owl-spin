import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from src.database.manager import get_db
from src.database.models import OAuthClient, UserAPIKey, APIKeyCreate, APIKeyRead, APIKeySecret
from src.utils.auth_utils import (
    verify_password, get_password_hash, create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES, get_current_tenant_id, authorize_with_scopes
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/oauth/token", response_model=APIKeySecret, tags=["Authentication"])
async def generate_oauth_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 Client Credentials flow to generate an access token.
    Requires client_id and client_secret.
    """
    if form_data.grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported grant type. Use 'client_credentials'.",
        )

    client = db.query(OAuthClient).filter(OAuthClient.client_id == form_data.username).first()
    if not client or not verify_password(form_data.password, client.client_secret_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # You might want to filter scopes based on what the client is allowed to request
    # For simplicity, we'll use all client's defined scopes
    token_scopes = client.scopes
    if form_data.scope:
        requested_scopes = form_data.scope.split(" ")
        if not all(s in token_scopes for s in requested_scopes):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested scopes are not allowed for this client.",
            )
        token_scopes = requested_scopes

    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(client.id), "client_id": client.client_id, "tenant_id": str(client.tenant_id), "scopes": token_scopes},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "scope": " ".join(token_scopes)
    }

@router.post("/api-keys", response_model=APIKeySecret, status_code=201, tags=["API Keys"])
async def create_api_key(
    api_key_create: APIKeyCreate,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    authorize: bool = Depends(authorize_with_scopes(["admin:*"])) # Only admins can create API keys
):
    """
    Creates a new API key for the authenticated tenant.
    Returns the key secret (only once).
    """
    # Generate a random key value
    key_value = f"sk_live_{uuid.uuid4().hex}" # Or sk_test_ for test keys
    key_hash = get_password_hash(key_value)

    expires_at = None
    if api_key_create.expires_in_days:
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=api_key_create.expires_in_days)

    db_api_key = UserAPIKey(
        tenant_id=tenant_id,
        key_name=api_key_create.key_name,
        api_key_hash=key_hash,
        permissions=api_key_create.scopes,
        expires_at=expires_at,
        is_active=True
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)

    return APIKeySecret(secret=key_value, **APIKeyRead.from_orm(db_api_key).dict())

@router.get("/api-keys", response_model=List[APIKeyRead], tags=["API Keys"])
async def list_api_keys(
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    authorize: bool = Depends(authorize_with_scopes(["admin:*", "telemetry:read"])) # Admins or those with telemetry read
):
    """Lists all API keys for the authenticated tenant."""
    return db.query(UserAPIKey).filter(UserAPIKey.tenant_id == tenant_id).all()

@router.patch("/api-keys/{api_key_id}", response_model=APIKeyRead, tags=["API Keys"])
async def update_api_key(
    api_key_id: UUID,
    update_data: Dict[str, Any] = Body(...),
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    authorize: bool = Depends(authorize_with_scopes(["admin:*"]))
):
    """Updates an existing API key (e.g., activate/deactivate, rotate secret)."""
    db_api_key = db.query(UserAPIKey).filter(
        UserAPIKey.id == api_key_id,
        UserAPIKey.tenant_id == tenant_id
    ).first()

    if not db_api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found")

    if "secret_rotate" in update_data and update_data["secret_rotate"]:
        new_key_value = f"sk_live_{uuid.uuid4().hex}"
        db_api_key.api_key_hash = get_password_hash(new_key_value)
        # You might want to return the new secret here, but it's generally not good practice
        # to return secrets on a PATCH. A separate endpoint for rotation might be better.
        logger.info(f"API Key {api_key_id} secret rotated.", extra={"api_key_id": str(api_key_id)})
        del update_data["secret_rotate"] # Remove this field so it's not applied directly

    for key, value in update_data.items():
        if hasattr(db_api_key, key):
            setattr(db_api_key, key, value)
    
    db.commit()
    db.refresh(db_api_key)
    return APIKeyRead.from_orm(db_api_key)

@router.delete("/api-keys/{api_key_id}", status_code=204, tags=["API Keys"])
async def delete_api_key(
    api_key_id: UUID,
    tenant_id: UUID = Depends(get_current_tenant_id),
    db: Session = Depends(get_db),
    authorize: bool = Depends(authorize_with_scopes(["admin:*"]))
):
    """Deletes an API key."""
    db_api_key = db.query(UserAPIKey).filter(
        UserAPIKey.id == api_key_id,
        UserAPIKey.tenant_id == tenant_id
    ).first()

    if not db_api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found")

    db.delete(db_api_key)
    db.commit()
    return None