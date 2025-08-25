"""
Utility functions for pagination in FastAPI endpoints.
"""

from typing import List, Optional, TypeVar, Generic, Any, Dict
from math import ceil

from fastapi import Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Query as SQLQuery

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Standard pagination parameters."""
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(50, ge=1, le=100, description="Items per page")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size
    
    @property
    def limit(self) -> int:
        """Get limit for database queries."""
        return self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response."""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there are more pages")
    has_prev: bool = Field(..., description="Whether there are previous pages")


def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    size: int = Query(50, ge=1, le=100, description="Items per page")
) -> PaginationParams:
    """
    FastAPI dependency for pagination parameters.
    
    Args:
        page: Page number (1-based)
        size: Items per page
        
    Returns:
        PaginationParams: Pagination parameters object
    """
    return PaginationParams(page=page, size=size)


def paginate(
    query: SQLQuery,
    params: PaginationParams,
    total_count: Optional[int] = None
) -> PaginatedResponse:
    """
    Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query object
        params: Pagination parameters
        total_count: Pre-calculated total count (optional)
        
    Returns:
        PaginatedResponse: Paginated results
    """
    # Get total count if not provided
    if total_count is None:
        total_count = query.count()
    
    # Calculate pagination info
    total_pages = ceil(total_count / params.size) if total_count > 0 else 1
    has_next = params.page < total_pages
    has_prev = params.page > 1
    
    # Get items for current page
    items = query.offset(params.offset).limit(params.limit).all()
    
    return PaginatedResponse(
        items=items,
        total=total_count,
        page=params.page,
        size=params.size,
        pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )


def paginate_list(
    items: List[T],
    params: PaginationParams
) -> PaginatedResponse[T]:
    """
    Paginate a list of items.
    
    Args:
        items: List of items to paginate
        params: Pagination parameters
        
    Returns:
        PaginatedResponse: Paginated results
    """
    total_count = len(items)
    total_pages = ceil(total_count / params.size) if total_count > 0 else 1
    has_next = params.page < total_pages
    has_prev = params.page > 1
    
    # Get items for current page
    start_idx = params.offset
    end_idx = start_idx + params.size
    page_items = items[start_idx:end_idx]
    
    return PaginatedResponse(
        items=page_items,
        total=total_count,
        page=params.page,
        size=params.size,
        pages=total_pages,
        has_next=has_next,
        has_prev=has_prev
    )


class CursorPaginationParams(BaseModel):
    """Cursor-based pagination parameters."""
    cursor: Optional[str] = Field(None, description="Cursor for pagination")
    size: int = Field(50, ge=1, le=100, description="Items per page")
    direction: str = Field("forward", description="Pagination direction (forward/backward)")


class CursorPaginatedResponse(BaseModel, Generic[T]):
    """Cursor-based paginated response."""
    items: List[T] = Field(..., description="List of items")
    has_next: bool = Field(..., description="Whether there are more items")
    has_prev: bool = Field(..., description="Whether there are previous items")
    next_cursor: Optional[str] = Field(None, description="Cursor for next page")
    prev_cursor: Optional[str] = Field(None, description="Cursor for previous page")
    size: int = Field(..., description="Items per page")


def get_cursor_pagination_params(
    cursor: Optional[str] = Query(None, description="Cursor for pagination"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    direction: str = Query("forward", description="Pagination direction")
) -> CursorPaginationParams:
    """
    FastAPI dependency for cursor pagination parameters.
    
    Args:
        cursor: Cursor for pagination
        size: Items per page
        direction: Pagination direction
        
    Returns:
        CursorPaginationParams: Cursor pagination parameters
    """
    return CursorPaginationParams(cursor=cursor, size=size, direction=direction)


def encode_cursor(data: Dict[str, Any]) -> str:
    """
    Encode cursor data to string.
    
    Args:
        data: Cursor data dictionary
        
    Returns:
        str: Encoded cursor string
    """
    import base64
    import json
    
    json_str = json.dumps(data, sort_keys=True)
    encoded = base64.b64encode(json_str.encode()).decode()
    return encoded


def decode_cursor(cursor: str) -> Dict[str, Any]:
    """
    Decode cursor string to data.
    
    Args:
        cursor: Encoded cursor string
        
    Returns:
        Dict[str, Any]: Cursor data dictionary
        
    Raises:
        ValueError: If cursor is invalid
    """
    import base64
    import json
    
    try:
        decoded = base64.b64decode(cursor.encode()).decode()
        return json.loads(decoded)
    except Exception as e:
        raise ValueError(f"Invalid cursor: {e}")


class SearchPaginationParams(PaginationParams):
    """Pagination parameters with search support."""
    search: Optional[str] = Field(None, description="Search query")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_order: str = Field("asc", description="Sort order (asc/desc)")
    
    def get_sort_direction(self) -> str:
        """Get SQLAlchemy sort direction."""
        return "desc" if self.sort_order.lower() == "desc" else "asc"


def get_search_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search query"),
    sort_by: Optional[str] = Query(None, description="Sort field"),
    sort_order: str = Query("asc", description="Sort order")
) -> SearchPaginationParams:
    """
    FastAPI dependency for search pagination parameters.
    
    Args:
        page: Page number
        size: Items per page
        search: Search query
        sort_by: Sort field
        sort_order: Sort order
        
    Returns:
        SearchPaginationParams: Search pagination parameters
    """
    return SearchPaginationParams(
        page=page,
        size=size,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )


def apply_search_filter(query: SQLQuery, model, search_fields: List[str], search_term: str) -> SQLQuery:
    """
    Apply search filter to SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query
        model: SQLAlchemy model class
        search_fields: List of field names to search
        search_term: Search term
        
    Returns:
        SQLQuery: Filtered query
    """
    from sqlalchemy import or_
    
    if not search_term or not search_fields:
        return query
    
    search_conditions = []
    search_pattern = f"%{search_term}%"
    
    for field_name in search_fields:
        if hasattr(model, field_name):
            field = getattr(model, field_name)
            search_conditions.append(field.ilike(search_pattern))
    
    if search_conditions:
        query = query.filter(or_(*search_conditions))
    
    return query


def apply_sorting(query: SQLQuery, model, sort_by: str, sort_order: str) -> SQLQuery:
    """
    Apply sorting to SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query
        model: SQLAlchemy model class
        sort_by: Field name to sort by
        sort_order: Sort order (asc/desc)
        
    Returns:
        SQLQuery: Sorted query
    """
    if not sort_by or not hasattr(model, sort_by):
        return query
    
    field = getattr(model, sort_by)
    
    if sort_order.lower() == "desc":
        query = query.order_by(field.desc())
    else:
        query = query.order_by(field.asc())
    
    return query


class FilterParams(BaseModel):
    """Base class for filter parameters."""
    
    def apply_filters(self, query: SQLQuery, model) -> SQLQuery:
        """
        Apply filters to SQLAlchemy query.
        
        Args:
            query: SQLAlchemy query
            model: SQLAlchemy model class
            
        Returns:
            SQLQuery: Filtered query
        """
        return query


def create_pagination_metadata(
    page: int,
    size: int,
    total: int,
    base_url: str = "",
    query_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create pagination metadata with URLs.
    
    Args:
        page: Current page number
        size: Items per page
        total: Total number of items
        base_url: Base URL for pagination links
        query_params: Additional query parameters
        
    Returns:
        Dict[str, Any]: Pagination metadata
    """
    query_params = query_params or {}
    total_pages = ceil(total / size) if total > 0 else 1
    
    def build_url(page_num: int) -> str:
        params = {**query_params, "page": page_num, "size": size}
        param_str = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        return f"{base_url}?{param_str}" if param_str else base_url
    
    metadata = {
        "current_page": page,
        "page_size": size,
        "total_items": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "links": {
            "self": build_url(page),
            "first": build_url(1),
            "last": build_url(total_pages)
        }
    }
    
    if metadata["has_next"]:
        metadata["links"]["next"] = build_url(page + 1)
    
    if metadata["has_prev"]:
        metadata["links"]["prev"] = build_url(page - 1)
    
    return metadata
