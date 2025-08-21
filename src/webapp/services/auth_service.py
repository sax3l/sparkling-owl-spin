"""
Service layer for authentication and user management.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..models import User, APIKey
from ..schemas.auth import UserCreate, UserUpdate, APIKeyCreate
from ..utils.security import PasswordValidator, TokenManager, APIKeyGenerator


class AuthService:
    """Authentication service for user and API key management."""
    
    def __init__(self, db: Session, secret_key: str):
        self.db = db
        self.password_validator = PasswordValidator()
        self.token_manager = TokenManager(secret_key)
    
    def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            Created user
            
        Raises:
            HTTPException: If user creation fails
        """
        # Validate password strength
        is_valid, errors = self.password_validator.validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Password validation failed", "errors": errors}
            )
        
        # Check if email already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = self.password_validator.hash_password(user_data.password)
        
        # Create user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=False
        )
        
        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User creation failed"
            )
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            User if authentication successful, None otherwise
        """
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not self.password_validator.verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: str, user_data: UserUpdate) -> User:
        """
        Update user information.
        
        Args:
            user_id: User ID
            user_data: User update data
            
        Returns:
            Updated user
            
        Raises:
            HTTPException: If user not found or update fails
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_data = user_data.dict(exclude_unset=True)
        
        # Handle password update
        if "password" in update_data:
            is_valid, errors = self.password_validator.validate_password_strength(
                update_data["password"]
            )
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"message": "Password validation failed", "errors": errors}
                )
            
            update_data["hashed_password"] = self.password_validator.hash_password(
                update_data.pop("password")
            )
        
        # Apply updates
        for field, value in update_data.items():
            setattr(user, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User update failed"
            )
    
    def change_password(self, user_id: str, current_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user_id: User ID
            current_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
            
        Raises:
            HTTPException: If validation fails
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not self.password_validator.verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password
        is_valid, errors = self.password_validator.validate_password_strength(new_password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Password validation failed", "errors": errors}
            )
        
        # Update password
        user.hashed_password = self.password_validator.hash_password(new_password)
        
        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Password change failed"
            )
    
    def deactivate_user(self, user_id: str) -> bool:
        """
        Deactivate a user account.
        
        Args:
            user_id: User ID
            
        Returns:
            True if user deactivated successfully
            
        Raises:
            HTTPException: If user not found
        """
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user.is_active = False
        
        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User deactivation failed"
            )
    
    def create_access_token(self, user: User) -> str:
        """
        Create an access token for user.
        
        Args:
            user: User object
            
        Returns:
            JWT access token
        """
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "is_superuser": user.is_superuser
        }
        
        return self.token_manager.create_access_token(token_data)
    
    def create_refresh_token(self, user: User) -> str:
        """
        Create a refresh token for user.
        
        Args:
            user: User object
            
        Returns:
            JWT refresh token
        """
        return self.token_manager.create_refresh_token(str(user.id))
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify and decode a token.
        
        Args:
            token: JWT token
            
        Returns:
            Token payload if valid, None otherwise
        """
        return self.token_manager.verify_token(token)
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Create new access token from refresh token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            HTTPException: If refresh token is invalid
        """
        payload = self.token_manager.verify_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        user = self.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return self.create_access_token(user)


class APIKeyService:
    """Service for API key management."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_api_key(self, user_id: str, api_key_data: APIKeyCreate) -> Dict[str, Any]:
        """
        Create a new API key for user.
        
        Args:
            user_id: User ID
            api_key_data: API key creation data
            
        Returns:
            Dictionary with API key info including the plain key
            
        Raises:
            HTTPException: If creation fails
        """
        # Generate API key
        plain_key = APIKeyGenerator.generate_api_key_with_prefix()
        hashed_key = APIKeyGenerator.hash_api_key(plain_key)
        
        # Create API key record
        api_key = APIKey(
            user_id=user_id,
            name=api_key_data.name,
            key_hash=hashed_key,
            permissions=api_key_data.permissions or [],
            expires_at=api_key_data.expires_at,
            is_active=True
        )
        
        try:
            self.db.add(api_key)
            self.db.commit()
            self.db.refresh(api_key)
            
            return {
                "id": str(api_key.id),
                "name": api_key.name,
                "key": plain_key,  # Only returned once
                "permissions": api_key.permissions,
                "expires_at": api_key.expires_at,
                "created_at": api_key.created_at
            }
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API key creation failed"
            )
    
    def get_user_api_keys(self, user_id: str) -> List[APIKey]:
        """
        Get all API keys for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of API keys
        """
        return self.db.query(APIKey).filter(
            APIKey.user_id == user_id
        ).order_by(APIKey.created_at.desc()).all()
    
    def verify_api_key(self, key: str) -> Optional[APIKey]:
        """
        Verify an API key and return the associated record.
        
        Args:
            key: Plain text API key
            
        Returns:
            APIKey record if valid, None otherwise
        """
        hashed_key = APIKeyGenerator.hash_api_key(key)
        
        api_key = self.db.query(APIKey).filter(
            APIKey.key_hash == hashed_key,
            APIKey.is_active == True
        ).first()
        
        if not api_key:
            return None
        
        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None
        
        # Update last used
        api_key.last_used = datetime.utcnow()
        self.db.commit()
        
        return api_key
    
    def revoke_api_key(self, user_id: str, api_key_id: str) -> bool:
        """
        Revoke an API key.
        
        Args:
            user_id: User ID
            api_key_id: API key ID
            
        Returns:
            True if key revoked successfully
            
        Raises:
            HTTPException: If key not found
        """
        api_key = self.db.query(APIKey).filter(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id
        ).first()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        api_key.is_active = False
        
        try:
            self.db.commit()
            return True
        except Exception:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API key revocation failed"
            )
    
    def update_api_key_permissions(
        self, 
        user_id: str, 
        api_key_id: str, 
        permissions: List[str]
    ) -> APIKey:
        """
        Update API key permissions.
        
        Args:
            user_id: User ID
            api_key_id: API key ID
            permissions: New permissions list
            
        Returns:
            Updated API key
            
        Raises:
            HTTPException: If key not found
        """
        api_key = self.db.query(APIKey).filter(
            APIKey.id == api_key_id,
            APIKey.user_id == user_id
        ).first()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="API key not found"
            )
        
        api_key.permissions = permissions
        
        try:
            self.db.commit()
            self.db.refresh(api_key)
            return api_key
        except Exception:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="API key update failed"
            )
