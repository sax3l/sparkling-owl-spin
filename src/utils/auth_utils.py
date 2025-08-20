import os
import datetime
from typing import List, Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from uuid import UUID

# Configuration for JWT and password hashing
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-jwt-key-please-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[datetime.timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def has_scope(required_scopes: List[str], user_scopes: List[str]) -> bool:
    """
    Checks if the user has all required scopes.
    'admin:*' grants all permissions.
    """
    if "admin:*" in user_scopes:
        return True
    
    for req_scope in required_scopes:
        if req_scope not in user_scopes:
            return False
    return True

def get_user_roles_from_db(db, user_id: UUID) -> List[str]:
    """Fetches roles for a user from the database."""
    from src.database.models import UserRole # Import here to avoid circular dependency
    roles = db.query(UserRole.role).filter(UserRole.user_id == user_id).all()
    return [r[0] for r in roles]

def get_role_scopes_from_db(db, role_name: str) -> List[str]:
    """Fetches scopes for a given role from the database."""
    from src.database.models import RolePermission # Import here to avoid circular dependency
    scopes = db.query(RolePermission.scope).filter(RolePermission.role_name == role_name).all()
    return [s[0] for s in scopes]

def get_user_scopes(db, user_id: UUID) -> List[str]:
    """Aggregates all scopes for a user based on their roles."""
    user_roles = get_user_roles_from_db(db, user_id)
    all_scopes = set()
    for role in user_roles:
        all_scopes.update(get_role_scopes_from_db(db, role))
    return list(all_scopes)