"""
Authentication router for user management and API access.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
import jwt
import bcrypt
from sqlalchemy.orm import Session

from ..deps import (
    get_database,
    get_current_user,
    get_current_active_user,
    get_admin_user,
    RateLimiter
)
from ..config import get_settings

router = APIRouter()
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Pydantic models
class UserCreate(BaseModel):
    """User creation model."""
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: Optional[str] = None
    is_active: bool = True
    tier: str = Field(default="free", regex="^(free|pro|enterprise)$")

class UserResponse(BaseModel):
    """User response model."""
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    tier: str
    created_at: datetime
    last_login: Optional[datetime]

class Token(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    """Token data model."""
    email: Optional[str] = None
    user_id: Optional[int] = None
    scopes: list = []

class PasswordReset(BaseModel):
    """Password reset model."""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""
    token: str
    new_password: str = Field(min_length=8)

class ChangePassword(BaseModel):
    """Change password model."""
    current_password: str
    new_password: str = Field(min_length=8)

class APIKeyCreate(BaseModel):
    """API key creation model."""
    name: str
    expires_in_days: Optional[int] = Field(default=365, ge=1, le=365)
    scopes: list = Field(default=["read"])

class APIKeyResponse(BaseModel):
    """API key response model."""
    id: int
    name: str
    key: str
    scopes: list
    expires_at: datetime
    created_at: datetime

# Authentication utilities
class AuthService:
    """Authentication service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.secret_key = self.settings.security.secret_key
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

auth_service = AuthService()

# Routes
@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_database),
    rate_limit: dict = Depends(RateLimiter("5/minute"))
):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash password
    hashed_password = auth_service.hash_password(user_data.password)
    
    # Create user
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=user_data.is_active,
        tier=user_data.tier,
        created_at=datetime.utcnow()
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.from_orm(db_user)

@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_database),
    rate_limit: dict = Depends(RateLimiter("10/minute"))
):
    """Login and receive access token."""
    # Authenticate user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = auth_service.create_access_token(
        data={"sub": user.email, "user_id": user.id, "tier": user.tier}
    )
    refresh_token = auth_service.create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=auth_service.access_token_expire_minutes * 60
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Form(...),
    db: Session = Depends(get_database)
):
    """Refresh access token using refresh token."""
    payload = auth_service.verify_token(refresh_token, "refresh")
    
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Create new tokens
    access_token = auth_service.create_access_token(
        data={"sub": user.email, "user_id": user.id, "tier": user.tier}
    )
    new_refresh_token = auth_service.create_refresh_token(
        data={"sub": user.email, "user_id": user.id}
    )
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=auth_service.access_token_expire_minutes * 60
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user information."""
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Update current user information."""
    # Update allowed fields
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)

@router.post("/change-password")
async def change_password(
    password_data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Change user password."""
    # Verify current password
    if not auth_service.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Hash new password
    new_hashed_password = auth_service.hash_password(password_data.new_password)
    current_user.hashed_password = new_hashed_password
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Password updated successfully"}

@router.post("/reset-password")
async def request_password_reset(
    reset_data: PasswordReset,
    db: Session = Depends(get_database),
    rate_limit: dict = Depends(RateLimiter("3/hour"))
):
    """Request password reset."""
    user = db.query(User).filter(User.email == reset_data.email).first()
    if not user:
        # Don't reveal if user exists
        return {"message": "If the email exists, a reset link has been sent"}
    
    # Generate reset token
    reset_token = auth_service.create_access_token(
        data={"sub": user.email, "reset": True},
        expires_delta=timedelta(hours=1)
    )
    
    # In a real application, send email with reset link
    # For now, just store the token (in production, use a proper queue/service)
    
    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/reset-password/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db: Session = Depends(get_database)
):
    """Confirm password reset with token."""
    try:
        payload = auth_service.verify_token(reset_data.token)
        if not payload.get("reset"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        user = db.query(User).filter(User.email == payload["sub"]).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )
        
        # Update password
        new_hashed_password = auth_service.hash_password(reset_data.new_password)
        user.hashed_password = new_hashed_password
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """Logout user (in a real app, you'd invalidate the token)."""
    return {"message": "Successfully logged out"}

# API Key management
@router.get("/api-keys", response_model=list[APIKeyResponse])
async def list_api_keys(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """List user's API keys."""
    api_keys = db.query(APIKey).filter(APIKey.user_id == current_user.id).all()
    return [APIKeyResponse.from_orm(key) for key in api_keys]

@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    key_data: APIKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Create new API key."""
    import secrets
    
    # Generate API key
    api_key = f"ck_{secrets.token_urlsafe(32)}"
    
    # Create expiration date
    expires_at = datetime.utcnow() + timedelta(days=key_data.expires_in_days)
    
    # Create API key record
    db_api_key = APIKey(
        user_id=current_user.id,
        name=key_data.name,
        key=api_key,
        scopes=key_data.scopes,
        expires_at=expires_at,
        created_at=datetime.utcnow()
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return APIKeyResponse.from_orm(db_api_key)

@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_database)
):
    """Delete API key."""
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == current_user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db.delete(api_key)
    db.commit()
    
    return {"message": "API key deleted successfully"}

# Admin routes
@router.get("/admin/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_database)
):
    """List all users (admin only)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return [UserResponse.from_orm(user) for user in users]

@router.patch("/admin/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: dict,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_database)
):
    """Update user (admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update allowed fields
    allowed_fields = ["is_active", "tier", "is_admin"]
    for field, value in user_update.items():
        if field in allowed_fields and hasattr(user, field):
            setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)

# Health check for auth service
@router.get("/health")
async def auth_health_check():
    """Health check for authentication service."""
    return {
        "status": "healthy",
        "service": "auth",
        "timestamp": datetime.utcnow().isoformat()
    }
