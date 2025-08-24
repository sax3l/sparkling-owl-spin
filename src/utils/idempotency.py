import json
import hashlib
from typing import Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp
from sqlalchemy.orm import Session
from database.models import IdempotencyKey
from database.manager import get_db # Assuming get_db is available
import logging
import datetime

logger = logging.getLogger(__name__)

class IdempotencyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        idempotency_key = request.headers.get("Idempotency-Key")
        
        # Only apply to POST/PUT requests that have an Idempotency-Key
        if request.method not in ["POST", "PUT"] or not idempotency_key:
            return await call_next(request)

        # Get tenant_id from request state (set by auth middleware/dependency)
        tenant_id = getattr(request.state, "tenant_id", None)
        if not tenant_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Tenant ID not found in request state.")

        db: Session = next(get_db()) # Get a DB session

        try:
            # Check if this key has been seen before for this tenant and path/method
            existing_record = db.query(IdempotencyKey).filter(
                IdempotencyKey.key == idempotency_key,
                IdempotencyKey.tenant_id == tenant_id,
                IdempotencyKey.path == request.url.path,
                IdempotencyKey.method == request.method
            ).first()

            if existing_record:
                logger.info(f"Idempotency key {idempotency_key} found. Returning cached response.", extra={"idempotency_key": idempotency_key})
                # Return cached response
                return Response(
                    content=json.dumps(existing_record.response_body),
                    status_code=existing_record.response_status,
                    media_type="application/json"
                )
            
            # If not found, proceed with the request
            response = await call_next(request)

            # Cache the response if it's a successful creation (200, 201, 202)
            if response.status_code in [200, 201, 202]:
                response_body = b""
                async for chunk in response.body_iterator:
                    response_body += chunk
                
                new_record = IdempotencyKey(
                    key=idempotency_key,
                    tenant_id=tenant_id,
                    path=request.url.path,
                    method=request.method,
                    response_status=response.status_code,
                    response_body=json.loads(response_body.decode('utf-8')),
                    created_at=datetime.datetime.utcnow()
                )
                db.add(new_record)
                db.commit()
                db.refresh(new_record)
                logger.info(f"Idempotency key {idempotency_key} cached.", extra={"idempotency_key": idempotency_key})

                # Re-create response with the original body
                return Response(content=response_body, status_code=response.status_code, media_type="application/json")
            
            return response # For non-successful responses, don't cache
        
        except Exception as e:
            db.rollback()
            logger.error(f"Error in idempotency middleware: {e}", exc_info=True, extra={"idempotency_key": idempotency_key})
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during idempotency check.")
        finally:
            db.close()