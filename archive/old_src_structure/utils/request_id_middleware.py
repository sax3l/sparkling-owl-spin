import uuid
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp
from observability.instrumentation import set_context, get_context # Assuming set_context and get_context are available

class RequestIDMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Check for X-Client-Request-ID header
        client_request_id: Optional[str] = request.headers.get("X-Client-Request-ID")
        
        # Generate a unique request ID if not provided by client
        request_id: str = client_request_id if client_request_id else str(uuid.uuid4())
        
        # Store request_id in request state for access in endpoints/dependencies
        request.state.request_id = request_id
        
        # Set request_id in structlog context for logging correlation
        set_context(request_id=request_id)

        # Process the request
        response = await call_next(request)

        # Add X-Request-ID to the response headers
        response.headers["X-Request-ID"] = request_id
        
        # If client provided an ID, echo it back in a specific header if desired,
        # or just use X-Request-ID for both. Sticking to X-Request-ID for simplicity.
        if client_request_id and client_request_id != request_id:
             response.headers["X-Client-Request-ID-Echo"] = client_request_id # Optional: echo back original client ID

        return response