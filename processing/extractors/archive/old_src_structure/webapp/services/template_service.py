"""
Service layer for template management.
"""

import yaml
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..utils.validation import TemplateValidator, ValidationResult


class TemplateService:
    """Service for managing scraping templates."""
    
    def __init__(self, db: Session, templates_dir: Optional[Path] = None):
        self.db = db
        self.templates_dir = templates_dir or Path("data/templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.validator = TemplateValidator()
    
    def create_template(self, template_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Create a new scraping template.
        
        Args:
            template_data: Template configuration data
            user_id: User ID creating the template
            
        Returns:
            Created template metadata
            
        Raises:
            HTTPException: If template creation fails
        """
        # Validate template
        validation_result = self.validator.validate_template(template_data)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Template validation failed",
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings
                }
            )
        
        # Add metadata
        template_data.update({
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "version": template_data.get("version", "1.0"),
            "validation_score": validation_result.score
        })
        
        # Generate template ID
        template_name = template_data.get("name", "template")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        template_id = f"{template_name}_{timestamp}_{user_id[:8]}"
        template_data["id"] = template_id
        
        # Save template to file
        template_file = self.templates_dir / f"{template_id}.yaml"
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                yaml.dump(template_data, f, default_flow_style=False, allow_unicode=True)
            
            return {
                "id": template_id,
                "name": template_data.get("name"),
                "description": template_data.get("description"),
                "category": template_data.get("category"),
                "version": template_data.get("version"),
                "validation_score": validation_result.score,
                "created_by": user_id,
                "created_at": template_data["created_at"],
                "file_path": str(template_file)
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save template: {str(e)}"
            )
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """
        Get a template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            Template data
            
        Raises:
            HTTPException: If template not found
        """
        template_file = self.templates_dir / f"{template_id}.yaml"
        
        if not template_file.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
            
            return template_data
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load template: {str(e)}"
            )
    
    def update_template(
        self, 
        template_id: str, 
        template_data: Dict[str, Any], 
        user_id: str
    ) -> Dict[str, Any]:
        """
        Update an existing template.
        
        Args:
            template_id: Template ID
            template_data: Updated template data
            user_id: User ID updating the template
            
        Returns:
            Updated template metadata
            
        Raises:
            HTTPException: If template not found or update fails
        """
        # Get existing template
        existing_template = self.get_template(template_id)
        
        # Check permissions (only creator or admin can update)
        if existing_template.get("created_by") != user_id:
            # TODO: Add admin role check
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        # Validate updated template
        validation_result = self.validator.validate_template(template_data)
        if not validation_result.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Template validation failed",
                    "errors": validation_result.errors,
                    "warnings": validation_result.warnings
                }
            )
        
        # Update metadata
        template_data.update({
            "id": template_id,
            "created_by": existing_template.get("created_by"),
            "created_at": existing_template.get("created_at"),
            "updated_by": user_id,
            "updated_at": datetime.utcnow().isoformat(),
            "version": self._increment_version(existing_template.get("version", "1.0")),
            "validation_score": validation_result.score
        })
        
        # Save updated template
        template_file = self.templates_dir / f"{template_id}.yaml"
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                yaml.dump(template_data, f, default_flow_style=False, allow_unicode=True)
            
            return {
                "id": template_id,
                "name": template_data.get("name"),
                "description": template_data.get("description"),
                "category": template_data.get("category"),
                "version": template_data.get("version"),
                "validation_score": validation_result.score,
                "updated_by": user_id,
                "updated_at": template_data["updated_at"]
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update template: {str(e)}"
            )
    
    def delete_template(self, template_id: str, user_id: str) -> bool:
        """
        Delete a template.
        
        Args:
            template_id: Template ID
            user_id: User ID requesting deletion
            
        Returns:
            True if template deleted successfully
            
        Raises:
            HTTPException: If template not found or permission denied
        """
        # Get existing template
        existing_template = self.get_template(template_id)
        
        # Check permissions
        if existing_template.get("created_by") != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        
        template_file = self.templates_dir / f"{template_id}.yaml"
        
        try:
            template_file.unlink()
            return True
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete template: {str(e)}"
            )
    
    def list_templates(
        self, 
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        List templates with filtering and pagination.
        
        Args:
            user_id: Filter by user ID (optional)
            category: Filter by category (optional)
            limit: Maximum number of templates to return
            offset: Number of templates to skip
            
        Returns:
            Dictionary with templates list and pagination info
        """
        templates = []
        
        # Load all template files
        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                
                # Apply filters
                if user_id and template_data.get("created_by") != user_id:
                    continue
                
                if category and template_data.get("category") != category:
                    continue
                
                # Extract summary info
                template_summary = {
                    "id": template_data.get("id"),
                    "name": template_data.get("name"),
                    "description": template_data.get("description"),
                    "category": template_data.get("category"),
                    "version": template_data.get("version"),
                    "validation_score": template_data.get("validation_score"),
                    "created_by": template_data.get("created_by"),
                    "created_at": template_data.get("created_at"),
                    "updated_at": template_data.get("updated_at"),
                    "selector_count": len(template_data.get("selectors", {}))
                }
                
                templates.append(template_summary)
                
            except Exception:
                # Skip invalid template files
                continue
        
        # Sort by creation date (newest first)
        templates.sort(
            key=lambda x: x.get("created_at", ""), 
            reverse=True
        )
        
        # Apply pagination
        total = len(templates)
        templates_page = templates[offset:offset + limit]
        
        return {
            "templates": templates_page,
            "pagination": {
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
        }
    
    def validate_template_by_id(self, template_id: str) -> ValidationResult:
        """
        Validate a template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            ValidationResult
            
        Raises:
            HTTPException: If template not found
        """
        template_data = self.get_template(template_id)
        return self.validator.validate_template(template_data)
    
    def get_template_categories(self) -> List[str]:
        """
        Get list of all template categories.
        
        Returns:
            List of category names
        """
        categories = set()
        
        for template_file in self.templates_dir.glob("*.yaml"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                
                category = template_data.get("category")
                if category:
                    categories.add(category)
                    
            except Exception:
                continue
        
        return sorted(list(categories))
    
    def duplicate_template(self, template_id: str, user_id: str, new_name: str) -> Dict[str, Any]:
        """
        Duplicate an existing template.
        
        Args:
            template_id: Source template ID
            user_id: User ID creating the duplicate
            new_name: Name for the new template
            
        Returns:
            New template metadata
            
        Raises:
            HTTPException: If source template not found
        """
        # Get source template
        source_template = self.get_template(template_id)
        
        # Create duplicate with new metadata
        duplicate_data = source_template.copy()
        duplicate_data.update({
            "name": new_name,
            "description": f"Copy of {source_template.get('name', 'template')}",
            "version": "1.0"  # Reset version for duplicate
        })
        
        # Remove original metadata
        for key in ["id", "created_by", "created_at", "updated_by", "updated_at"]:
            duplicate_data.pop(key, None)
        
        return self.create_template(duplicate_data, user_id)
    
    def export_template(self, template_id: str, format: str = "yaml") -> Tuple[str, str]:
        """
        Export a template in specified format.
        
        Args:
            template_id: Template ID
            format: Export format (yaml or json)
            
        Returns:
            Tuple of (filename, content)
            
        Raises:
            HTTPException: If template not found or invalid format
        """
        template_data = self.get_template(template_id)
        
        if format.lower() == "yaml":
            content = yaml.dump(template_data, default_flow_style=False, allow_unicode=True)
            filename = f"{template_id}.yaml"
        elif format.lower() == "json":
            content = json.dumps(template_data, indent=2, ensure_ascii=False)
            filename = f"{template_id}.json"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported export format: {format}"
            )
        
        return filename, content
    
    def import_template(self, content: str, format: str, user_id: str) -> Dict[str, Any]:
        """
        Import a template from content.
        
        Args:
            content: Template content
            format: Content format (yaml or json)
            user_id: User ID importing the template
            
        Returns:
            Imported template metadata
            
        Raises:
            HTTPException: If import fails
        """
        try:
            if format.lower() == "yaml":
                template_data = yaml.safe_load(content)
            elif format.lower() == "json":
                template_data = json.loads(content)
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported import format: {format}"
                )
            
            if not isinstance(template_data, dict):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid template format"
                )
            
            # Remove existing metadata to avoid conflicts
            for key in ["id", "created_by", "created_at", "updated_by", "updated_at"]:
                template_data.pop(key, None)
            
            # Ensure template has a name
            if not template_data.get("name"):
                template_data["name"] = f"Imported Template {datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return self.create_template(template_data, user_id)
            
        except yaml.YAMLError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"YAML parsing error: {str(e)}"
            )
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"JSON parsing error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Import failed: {str(e)}"
            )
    
    def _increment_version(self, version: str) -> str:
        """
        Increment version number.
        
        Args:
            version: Current version string
            
        Returns:
            Incremented version string
        """
        try:
            parts = version.split(".")
            if len(parts) >= 2:
                major, minor = int(parts[0]), int(parts[1])
                patch = int(parts[2]) if len(parts) > 2 else 0
                return f"{major}.{minor}.{patch + 1}"
            else:
                return f"{version}.1"
        except (ValueError, IndexError):
            return "1.0.1"
