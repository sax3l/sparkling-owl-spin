"""
Lovable Backend Services

Business logic and service layer implementations.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import hashlib
import secrets

from src.database.models import User, Project, Template, Job, APIKey, AuditLog
from ..schemas.models import (
    UserCreate, UserUpdate, UserInDB,
    ProjectCreate, ProjectUpdate, ProjectInDB,
    TemplateCreate, TemplateUpdate, TemplateInDB,
    JobCreate, JobUpdate, JobInDB
)
from ..auth import get_password_hash, verify_password


class UserService:
    """User management service."""

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> UserInDB:
        """Create a new user."""
        # Check if user exists
        if db.query(User).filter(User.email == user.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        if db.query(User).filter(User.username == user.username).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return UserInDB.from_orm(db_user)

    @staticmethod
    def get_user(db: Session, user_id: int) -> Optional[UserInDB]:
        """Get user by ID."""
        db_user = db.query(User).filter(User.id == user_id).first()
        return UserInDB.from_orm(db_user) if db_user else None

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        db_user = db.query(User).filter(User.email == email).first()
        return UserInDB.from_orm(db_user) if db_user else None

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[UserInDB]:
        """Get user by username."""
        db_user = db.query(User).filter(User.username == username).first()
        return UserInDB.from_orm(db_user) if db_user else None

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserInDB]:
        """Update user."""
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)
        return UserInDB.from_orm(db_user)

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[UserInDB]:
        """Authenticate user."""
        user = UserService.get_user_by_username(db, username)
        if not user:
            user = UserService.get_user_by_email(db, username)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user


class ProjectService:
    """Project management service."""

    @staticmethod
    def create_project(db: Session, project: ProjectCreate, owner_id: int) -> ProjectInDB:
        """Create a new project."""
        db_project = Project(
            name=project.name,
            description=project.description,
            config=project.config,
            template_id=project.template_id,
            owner_id=owner_id
        )
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return ProjectInDB.from_orm(db_project)

    @staticmethod
    def get_project(db: Session, project_id: int, user_id: int) -> Optional[ProjectInDB]:
        """Get project by ID."""
        db_project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user_id
        ).first()
        return ProjectInDB.from_orm(db_project) if db_project else None

    @staticmethod
    def get_user_projects(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[ProjectInDB]:
        """Get user's projects."""
        projects = db.query(Project).filter(
            Project.owner_id == user_id
        ).offset(skip).limit(limit).all()
        return [ProjectInDB.from_orm(p) for p in projects]

    @staticmethod
    def update_project(db: Session, project_id: int, project_update: ProjectUpdate, user_id: int) -> Optional[ProjectInDB]:
        """Update project."""
        db_project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user_id
        ).first()
        if not db_project:
            return None

        update_data = project_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_project, field, value)

        db.commit()
        db.refresh(db_project)
        return ProjectInDB.from_orm(db_project)

    @staticmethod
    def delete_project(db: Session, project_id: int, user_id: int) -> bool:
        """Delete project."""
        db_project = db.query(Project).filter(
            Project.id == project_id,
            Project.owner_id == user_id
        ).first()
        if not db_project:
            return False

        db.delete(db_project)
        db.commit()
        return True


class TemplateService:
    """Template management service."""

    @staticmethod
    def create_template(db: Session, template: TemplateCreate, creator_id: int) -> TemplateInDB:
        """Create a new template."""
        db_template = Template(
            name=template.name,
            description=template.description,
            category=template.category,
            config=template.config,
            is_public=template.is_public,
            creator_id=creator_id
        )
        db.add(db_template)
        db.commit()
        db.refresh(db_template)
        return TemplateInDB.from_orm(db_template)

    @staticmethod
    def get_template(db: Session, template_id: int) -> Optional[TemplateInDB]:
        """Get template by ID."""
        db_template = db.query(Template).filter(Template.id == template_id).first()
        return TemplateInDB.from_orm(db_template) if db_template else None

    @staticmethod
    def get_public_templates(db: Session, skip: int = 0, limit: int = 100) -> List[TemplateInDB]:
        """Get public templates."""
        templates = db.query(Template).filter(
            Template.is_public == True
        ).offset(skip).limit(limit).all()
        return [TemplateInDB.from_orm(t) for t in templates]

    @staticmethod
    def get_user_templates(db: Session, creator_id: int, skip: int = 0, limit: int = 100) -> List[TemplateInDB]:
        """Get user's templates."""
        templates = db.query(Template).filter(
            Template.creator_id == creator_id
        ).offset(skip).limit(limit).all()
        return [TemplateInDB.from_orm(t) for t in templates]


class JobService:
    """Job management service."""

    @staticmethod
    def create_job(db: Session, job: JobCreate, user_id: int) -> JobInDB:
        """Create a new job."""
        db_job = Job(
            name=job.name,
            type=job.type,
            config=job.config,
            project_id=job.project_id,
            user_id=user_id
        )
        db.add(db_job)
        db.commit()
        db.refresh(db_job)
        return JobInDB.from_orm(db_job)

    @staticmethod
    def get_job(db: Session, job_id: int, user_id: int) -> Optional[JobInDB]:
        """Get job by ID."""
        db_job = db.query(Job).filter(
            Job.id == job_id,
            Job.user_id == user_id
        ).first()
        return JobInDB.from_orm(db_job) if db_job else None

    @staticmethod
    def get_user_jobs(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[JobInDB]:
        """Get user's jobs."""
        jobs = db.query(Job).filter(
            Job.user_id == user_id
        ).offset(skip).limit(limit).all()
        return [JobInDB.from_orm(j) for j in jobs]

    @staticmethod
    def update_job_status(db: Session, job_id: int, status: str, result: dict = None, error: str = None) -> Optional[JobInDB]:
        """Update job status."""
        db_job = db.query(Job).filter(Job.id == job_id).first()
        if not db_job:
            return None

        db_job.status = status
        if result:
            db_job.result = result
        if error:
            db_job.error_message = error
        if status == "running" and not db_job.started_at:
            db_job.started_at = datetime.utcnow()
        elif status in ["completed", "failed"]:
            db_job.completed_at = datetime.utcnow()

        db.commit()
        db.refresh(db_job)
        return JobInDB.from_orm(db_job)


class APIKeyService:
    """API Key management service."""

    @staticmethod
    def generate_api_key() -> str:
        """Generate a new API key."""
        return f"lv_{secrets.token_urlsafe(32)}"

    @staticmethod
    def hash_key(key: str) -> str:
        """Hash an API key."""
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def create_api_key(db: Session, name: str, user_id: int, permissions: List[str] = None) -> tuple[str, APIKey]:
        """Create a new API key."""
        api_key = APIKeyService.generate_api_key()
        key_hash = APIKeyService.hash_key(api_key)

        db_key = APIKey(
            name=name,
            key_hash=key_hash,
            permissions=permissions or [],
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(days=365)
        )
        db.add(db_key)
        db.commit()
        db.refresh(db_key)

        return api_key, db_key

    @staticmethod
    def verify_api_key(db: Session, key: str) -> Optional[APIKey]:
        """Verify an API key."""
        key_hash = APIKeyService.hash_key(key)
        db_key = db.query(APIKey).filter(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True
        ).first()

        if db_key and (not db_key.expires_at or db_key.expires_at > datetime.utcnow()):
            # Update last used
            db_key.last_used = datetime.utcnow()
            db.commit()
            return db_key

        return None


class AuditService:
    """Audit logging service."""

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[dict] = None
    ):
        """Log an audit event."""
        audit_log = AuditLog(
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        db.add(audit_log)
        db.commit()
