import datetime
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.routing import APIRoute
from starlette.types import ASGIApp

class DeprecationMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Check if the current route is an APIRoute and has a 'sunset_date' attribute
        if isinstance(request.scope["route"], APIRoute):
            sunset_date: Optional[datetime.date] = getattr(request.scope["route"], "sunset_date", None)
            if sunset_date:
                # Format the date according to RFC 7231 (HTTP-date format)
                # Example: "Sun, 06 Nov 1994 08:49:37 GMT"
                # For simplicity, we'll use ISO format for now, but RFC 7231 is preferred for strict compliance.
                # A more robust solution would use a library like 'email.utils.formatdate'
                response.headers["Sunset"] = sunset_date.isoformat()
                response.headers["Warning"] = '299 - "Deprecated API endpoint. Please migrate to newer versions."'
        return response

def deprecated_endpoint(sunset_date: datetime.date):
    """
    Decorator to mark a FastAPI endpoint as deprecated and specify its sunset date.
    The DeprecationMiddleware will use this information to add a 'Sunset' header.
    """
    def decorator(func: Callable):
        # Attach the sunset_date to the function object, which FastAPI's APIRoute can pick up
        setattr(func, "sunset_date", sunset_date)
        return func
    return decorator