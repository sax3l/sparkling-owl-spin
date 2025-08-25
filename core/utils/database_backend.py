"""
Database-Enabled Backend Entry Point

En FastAPI backend-app med fullständig databasintegration.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import asyncpg
import asyncio
import os
import uvicorn
import json
from passlib.context import CryptContext
import jwt
import uuid


# Security setup
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours


# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lovable:lovable123@localhost:5433/lovable_db")


# Pydantic Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    status: str
    created_at: datetime
    updated_at: datetime


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    service: str
    version: str
    database: str


# Database connection pool
db_pool = None


async def init_db():
    """Initialize database connection pool."""
    global db_pool
    try:
        db_pool = await asyncpg.create_pool(DATABASE_URL)
        print("✅ Database connection pool created successfully")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise


async def close_db():
    """Close database connection pool."""
    global db_pool
    if db_pool:
        await db_pool.close()
        print("🔒 Database connection pool closed")


async def get_db():
    """Get database connection from pool."""
    if not db_pool:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    async with db_pool.acquire() as connection:
        yield connection


# Authentication utilities
def verify_password(plain_password, hashed_password):
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Hash password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
):
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # Get user from database
    user = await db.fetchrow(
        "SELECT id, username, email, full_name, is_active, is_verified, created_at "
        "FROM users WHERE id = $1",
        uuid.UUID(user_id)
    )
    
    if user is None:
        raise credentials_exception
    
    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


def create_app() -> FastAPI:
    """Create FastAPI application with database integration."""
    
    app = FastAPI(
        title="Lovable Backend API",
        description="Backend API för Lovable-projektet med PostgreSQL integration",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # I produktion, specificera exakta origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Startup event
    @app.on_event("startup")
    async def startup():
        await init_db()
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown():
        await close_db()
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "Lovable Backend API is running with PostgreSQL",
            "status": "ok",
            "docs": "/docs"
        }
    
    @app.get("/health", response_model=HealthResponse)
    async def health_check(db = Depends(get_db)):
        """Health check endpoint med database status."""
        try:
            # Test database connection
            result = await db.fetchval("SELECT 1")
            db_status = "connected" if result == 1 else "error"
        except Exception as e:
            db_status = f"error: {str(e)}"
        
        return HealthResponse(
            status="healthy" if db_status == "connected" else "degraded",
            timestamp=datetime.now().isoformat(),
            service="lovable-backend",
            version="1.0.0",
            database=db_status
        )
    
    @app.post("/auth/register", response_model=UserResponse)
    async def register_user(user: UserCreate, db = Depends(get_db)):
        """Register a new user."""
        # Check if user already exists
        existing = await db.fetchrow(
            "SELECT id FROM users WHERE username = $1 OR email = $2",
            user.username, user.email
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user.password)
        
        # Create user
        user_id = await db.fetchval(
            """
            INSERT INTO users (username, email, password_hash, full_name)
            VALUES ($1, $2, $3, $4)
            RETURNING id
            """,
            user.username, user.email, hashed_password, user.full_name
        )
        
        # Get created user
        created_user = await db.fetchrow(
            "SELECT id, username, email, full_name, is_active, is_verified, created_at "
            "FROM users WHERE id = $1",
            user_id
        )
        
        return UserResponse(**dict(created_user))
    
    @app.post("/auth/login", response_model=Token)
    async def login(user: UserLogin, db = Depends(get_db)):
        """Login user and return JWT token."""
        # Get user from database
        db_user = await db.fetchrow(
            "SELECT id, username, password_hash, is_active FROM users WHERE username = $1",
            user.username
        )
        
        if not db_user or not verify_password(user.password, db_user['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if not db_user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        
        # Update last login
        await db.execute(
            "UPDATE users SET last_login = $1 WHERE id = $2",
            datetime.utcnow(), db_user['id']
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user['id'])}, 
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        )
    
    @app.get("/auth/me", response_model=UserResponse)
    async def get_current_user_info(current_user = Depends(get_current_user)):
        """Get current user information."""
        return UserResponse(**dict(current_user))
    
    @app.get("/api/v1/projects", response_model=List[ProjectResponse])
    async def get_projects(
        current_user = Depends(get_current_user),
        db = Depends(get_db)
    ):
        """Get user's projects."""
        projects = await db.fetch(
            """
            SELECT id, name, description, owner_id, status, created_at, updated_at
            FROM projects
            WHERE owner_id = $1
            ORDER BY created_at DESC
            """,
            current_user['id']
        )
        
        return [ProjectResponse(**dict(project)) for project in projects]
    
    @app.post("/api/v1/projects", response_model=ProjectResponse)
    async def create_project(
        project: ProjectCreate,
        current_user = Depends(get_current_user),
        db = Depends(get_db)
    ):
        """Create a new project."""
        project_id = await db.fetchval(
            """
            INSERT INTO projects (name, description, owner_id)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            project.name, project.description, current_user['id']
        )
        
        # Get created project
        created_project = await db.fetchrow(
            """
            SELECT id, name, description, owner_id, status, created_at, updated_at
            FROM projects WHERE id = $1
            """,
            project_id
        )
        
        return ProjectResponse(**dict(created_project))
    
    @app.get("/api/v1/stats")
    async def get_stats(
        current_user = Depends(get_current_user),
        db = Depends(get_db)
    ):
        """Get user statistics."""
        stats = await db.fetchrow(
            """
            SELECT 
                (SELECT COUNT(*) FROM projects WHERE owner_id = $1) as projects_count,
                (SELECT COUNT(*) FROM jobs j JOIN projects p ON j.project_id = p.id WHERE p.owner_id = $1) as jobs_count,
                (SELECT COUNT(*) FROM jobs j JOIN projects p ON j.project_id = p.id WHERE p.owner_id = $1 AND j.status = 'completed') as completed_jobs
            """,
            current_user['id']
        )
        
        return {
            "projects": stats['projects_count'] or 0,
            "jobs": stats['jobs_count'] or 0,
            "completed_jobs": stats['completed_jobs'] or 0,
            "user": {
                "username": current_user['username'],
                "email": current_user['email'],
                "member_since": current_user['created_at'].isoformat()
            }
        }
    
    @app.get("/api/v1/info")
    async def api_info():
        """API information endpoint."""
        return {
            "api_version": "v1",
            "service": "lovable-backend",
            "database": "PostgreSQL",
            "authentication": "JWT",
            "endpoints": {
                "auth": {
                    "register": "POST /auth/register",
                    "login": "POST /auth/login",
                    "me": "GET /auth/me"
                },
                "projects": {
                    "list": "GET /api/v1/projects",
                    "create": "POST /api/v1/projects"
                },
                "stats": "GET /api/v1/stats",
                "health": "GET /health",
                "docs": "GET /docs"
            }
        }
    
    return app


def main():
    """Start backend server."""
    app = create_app()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
        access_log=True
    )


if __name__ == "__main__":
    main()
