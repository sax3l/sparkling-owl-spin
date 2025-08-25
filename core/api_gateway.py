#!/usr/bin/env python3
"""
API Gateway för Sparkling-Owl-Spin
Hanterar alla API-förfrågningar enligt pyramid-arkitekturen
"""

import logging
import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import aiohttp
from aiohttp import web, ClientSession
from aiohttp.web import middleware
import aiofiles
from pathlib import Path
import traceback

logger = logging.getLogger(__name__)

class APIVersion(Enum):
    """API versions"""
    V1 = "v1"
    V2 = "v2"
    BETA = "beta"

class ResponseFormat(Enum):
    """Response formats"""
    JSON = "json"
    XML = "xml"
    CSV = "csv"
    HTML = "html"

@dataclass
class APIEndpoint:
    """API endpoint definition"""
    path: str
    method: str
    handler: Callable
    version: APIVersion = APIVersion.V1
    requires_auth: bool = False
    rate_limit: Optional[int] = None
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    response_format: ResponseFormat = ResponseFormat.JSON

@dataclass
class APIRequest:
    """API request information"""
    request_id: str
    endpoint: str
    method: str
    client_ip: str
    user_agent: str
    parameters: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: datetime = field(default_factory=datetime.now)
    response_time: Optional[float] = None
    status_code: Optional[int] = None
    response_size: Optional[int] = None

class APIGateway:
    """Enhanced API Gateway för pyramid architecture"""
    
    def __init__(self):
        self.initialized = False
        
        # Web application
        self.app = None
        self.server = None
        self.site = None
        self.runner = None
        
        # Configuration
        self.host = "0.0.0.0"
        self.port = 8000
        self.cors_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        
        # API endpoints registry
        self.endpoints: Dict[str, APIEndpoint] = {}
        self.middleware_stack: List[Callable] = []
        
        # Request tracking
        self.active_requests: Dict[str, APIRequest] = {}
        self.request_history: List[APIRequest] = []
        self.max_history_size = 10000
        
        # Statistics
        self.api_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "by_endpoint": {},
            "by_status_code": {},
            "by_client_ip": {},
            "response_times": [],
            "uptime_start": datetime.now()
        }
        
        # Rate limiting
        self.rate_limits: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self):
        """Initialize API Gateway"""
        try:
            logger.info("🌐 Initializing Enhanced API Gateway")
            
            # Create web application
            self.app = web.Application(
                client_max_size=self.max_request_size,
                middlewares=self._create_middleware_stack()
            )
            
            # Register API endpoints
            await self._register_api_endpoints()
            
            # Setup static file serving
            await self._setup_static_routes()
            
            # Start web server
            await self._start_server()
            
            self.initialized = True
            logger.info(f"✅ Enhanced API Gateway initialized on http://{self.host}:{self.port}")
            
            # Print API status
            await self._print_api_status()
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize API Gateway: {str(e)}")
            raise
            
    def _create_middleware_stack(self) -> List[Callable]:
        """Create middleware stack"""
        
        middleware_stack = [
            self._cors_middleware,
            self._request_logging_middleware,
            self._rate_limiting_middleware,
            self._request_tracking_middleware,
            self._error_handling_middleware,
            self._response_formatting_middleware
        ]
        
        return middleware_stack
        
    @middleware
    async def _cors_middleware(self, request, handler):
        """CORS middleware"""
        
        # Handle preflight requests
        if request.method == 'OPTIONS':
            response = web.Response()
        else:
            response = await handler(request)
            
        # Add CORS headers
        response.headers['Access-Control-Allow-Origin'] = '*'  # Should be restricted in production
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-API-Key'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        
        return response
        
    @middleware
    async def _request_logging_middleware(self, request, handler):
        """Request logging middleware"""
        
        start_time = time.time()
        client_ip = request.remote or "unknown"
        
        try:
            response = await handler(request)
            
            # Log successful request
            response_time = (time.time() - start_time) * 1000
            logger.info(
                f"📡 {request.method} {request.path} "
                f"från {client_ip} - {response.status} "
                f"({response_time:.2f}ms)"
            )
            
            return response
            
        except Exception as e:
            # Log failed request
            response_time = (time.time() - start_time) * 1000
            logger.error(
                f"📡 {request.method} {request.path} "
                f"från {client_ip} - ERROR "
                f"({response_time:.2f}ms): {str(e)}"
            )
            raise
            
    @middleware
    async def _rate_limiting_middleware(self, request, handler):
        """Rate limiting middleware"""
        
        client_ip = request.remote or "unknown"
        endpoint = f"{request.method} {request.path}"
        
        # Check rate limit
        if not await self._check_rate_limit(client_ip, endpoint):
            return web.json_response(
                {
                    "error": "Rate limit exceeded",
                    "message": "Too many requests from this IP address"
                },
                status=429
            )
            
        return await handler(request)
        
    async def _check_rate_limit(self, client_ip: str, endpoint: str) -> bool:
        """Check if request is within rate limits"""
        
        current_time = time.time()
        minute_key = int(current_time // 60)  # Current minute
        
        if client_ip not in self.rate_limits:
            self.rate_limits[client_ip] = {}
            
        if minute_key not in self.rate_limits[client_ip]:
            self.rate_limits[client_ip][minute_key] = {}
            
        # Clean old entries
        for old_minute in list(self.rate_limits[client_ip].keys()):
            if old_minute < minute_key - 5:  # Keep only last 5 minutes
                del self.rate_limits[client_ip][old_minute]
                
        # Check current request count
        current_count = self.rate_limits[client_ip][minute_key].get(endpoint, 0)
        max_requests = 100  # 100 requests per minute per endpoint
        
        if current_count >= max_requests:
            return False
            
        # Increment counter
        self.rate_limits[client_ip][minute_key][endpoint] = current_count + 1
        return True
        
    @middleware
    async def _request_tracking_middleware(self, request, handler):
        """Request tracking middleware"""
        
        request_id = f"req_{int(time.time())}_{len(self.active_requests)}"
        start_time = time.time()
        
        # Create request record
        api_request = APIRequest(
            request_id=request_id,
            endpoint=request.path,
            method=request.method,
            client_ip=request.remote or "unknown",
            user_agent=request.headers.get('User-Agent', ''),
            parameters=dict(request.query),
            headers=dict(request.headers)
        )
        
        self.active_requests[request_id] = api_request
        
        try:
            response = await handler(request)
            
            # Update request record
            api_request.response_time = (time.time() - start_time) * 1000
            api_request.status_code = response.status
            
            # Update statistics
            self._update_api_statistics(api_request, True)
            
            return response
            
        except Exception as e:
            # Update request record för error
            api_request.response_time = (time.time() - start_time) * 1000
            api_request.status_code = 500
            
            # Update statistics
            self._update_api_statistics(api_request, False)
            
            raise
            
        finally:
            # Move to history and clean up
            self.request_history.append(api_request)
            if len(self.request_history) > self.max_history_size:
                self.request_history = self.request_history[-self.max_history_size//2:]
                
            if request_id in self.active_requests:
                del self.active_requests[request_id]
                
    def _update_api_statistics(self, api_request: APIRequest, success: bool):
        """Update API statistics"""
        
        self.api_stats["total_requests"] += 1
        
        if success:
            self.api_stats["successful_requests"] += 1
        else:
            self.api_stats["failed_requests"] += 1
            
        # By endpoint
        endpoint_key = f"{api_request.method} {api_request.endpoint}"
        if endpoint_key not in self.api_stats["by_endpoint"]:
            self.api_stats["by_endpoint"][endpoint_key] = {"count": 0, "avg_response_time": 0}
            
        endpoint_stats = self.api_stats["by_endpoint"][endpoint_key]
        old_count = endpoint_stats["count"]
        endpoint_stats["count"] += 1
        
        if api_request.response_time:
            endpoint_stats["avg_response_time"] = (
                (endpoint_stats["avg_response_time"] * old_count + api_request.response_time) /
                endpoint_stats["count"]
            )
            
        # By status code
        status_code = api_request.status_code or 500
        self.api_stats["by_status_code"][status_code] = (
            self.api_stats["by_status_code"].get(status_code, 0) + 1
        )
        
        # By client IP
        if api_request.client_ip not in self.api_stats["by_client_ip"]:
            self.api_stats["by_client_ip"][api_request.client_ip] = 0
        self.api_stats["by_client_ip"][api_request.client_ip] += 1
        
        # Response times
        if api_request.response_time:
            self.api_stats["response_times"].append(api_request.response_time)
            if len(self.api_stats["response_times"]) > 1000:
                self.api_stats["response_times"] = self.api_stats["response_times"][-500:]
                
    @middleware
    async def _error_handling_middleware(self, request, handler):
        """Error handling middleware"""
        
        try:
            return await handler(request)
            
        except web.HTTPException:
            # Re-raise HTTP exceptions
            raise
            
        except Exception as e:
            logger.error(f"❌ API error: {str(e)}\n{traceback.format_exc()}")
            
            return web.json_response(
                {
                    "error": "Internal server error",
                    "message": str(e),
                    "request_id": getattr(request, 'request_id', 'unknown'),
                    "timestamp": datetime.now().isoformat()
                },
                status=500
            )
            
    @middleware
    async def _response_formatting_middleware(self, request, handler):
        """Response formatting middleware"""
        
        response = await handler(request)
        
        # Add common headers
        response.headers['X-API-Version'] = 'v1'
        response.headers['X-Server'] = 'Sparkling-Owl-Spin'
        response.headers['X-Request-ID'] = getattr(request, 'request_id', 'unknown')
        
        return response
        
    async def _register_api_endpoints(self):
        """Register all API endpoints"""
        
        # Core API endpoints
        await self._register_core_endpoints()
        
        # Workflow management endpoints
        await self._register_workflow_endpoints()
        
        # Security endpoints
        await self._register_security_endpoints()
        
        # System monitoring endpoints
        await self._register_monitoring_endpoints()
        
        # Data extraction endpoints
        await self._register_data_endpoints()
        
        logger.info(f"✅ Registered {len(self.endpoints)} API endpoints")
        
    async def _register_core_endpoints(self):
        """Register core API endpoints"""
        
        # Health check
        self.app.router.add_get('/', self._handle_root)
        self.app.router.add_get('/health', self._handle_health)
        self.app.router.add_get('/status', self._handle_status)
        
        # API documentation
        self.app.router.add_get('/docs', self._handle_docs)
        self.app.router.add_get('/api-spec', self._handle_api_spec)
        
    async def _register_workflow_endpoints(self):
        """Register workflow management endpoints"""
        
        # Workflow CRUD
        self.app.router.add_post('/api/v1/workflows', self._handle_create_workflow)
        self.app.router.add_get('/api/v1/workflows', self._handle_list_workflows)
        self.app.router.add_get('/api/v1/workflows/{workflow_id}', self._handle_get_workflow)
        self.app.router.add_post('/api/v1/workflows/{workflow_id}/execute', self._handle_execute_workflow)
        self.app.router.add_delete('/api/v1/workflows/{workflow_id}', self._handle_delete_workflow)
        
        # Workflow results
        self.app.router.add_get('/api/v1/workflows/{workflow_id}/results', self._handle_get_workflow_results)
        self.app.router.add_get('/api/v1/workflows/{workflow_id}/status', self._handle_get_workflow_status)
        
    async def _register_security_endpoints(self):
        """Register security endpoints"""
        
        # Domain authorization
        self.app.router.add_post('/api/v1/security/domains', self._handle_authorize_domain)
        self.app.router.add_get('/api/v1/security/domains', self._handle_list_authorized_domains)
        self.app.router.add_delete('/api/v1/security/domains/{domain}', self._handle_revoke_domain)
        
        # Penetration testing sessions
        self.app.router.add_post('/api/v1/security/pentest-sessions', self._handle_create_pentest_session)
        self.app.router.add_get('/api/v1/security/pentest-sessions', self._handle_list_pentest_sessions)
        self.app.router.add_post('/api/v1/security/pentest-sessions/{session_id}/close', self._handle_close_pentest_session)
        
        # Security logs
        self.app.router.add_get('/api/v1/security/events', self._handle_get_security_events)
        self.app.router.add_post('/api/v1/security/logs/export', self._handle_export_security_log)
        
    async def _register_monitoring_endpoints(self):
        """Register system monitoring endpoints"""
        
        # System metrics
        self.app.router.add_get('/api/v1/metrics', self._handle_get_metrics)
        self.app.router.add_get('/api/v1/metrics/api', self._handle_get_api_metrics)
        self.app.router.add_get('/api/v1/metrics/engines', self._handle_get_engine_metrics)
        
        # System status
        self.app.router.add_get('/api/v1/system/status', self._handle_get_system_status)
        self.app.router.add_get('/api/v1/system/health', self._handle_get_system_health)
        
    async def _register_data_endpoints(self):
        """Register data extraction endpoints"""
        
        # Swedish data sources
        self.app.router.add_get('/api/v1/data/swedish/vehicles', self._handle_search_vehicles)
        self.app.router.add_get('/api/v1/data/swedish/companies', self._handle_search_companies)
        
        # General scraping
        self.app.router.add_post('/api/v1/scraping/jobs', self._handle_create_scraping_job)
        self.app.router.add_get('/api/v1/scraping/jobs', self._handle_list_scraping_jobs)
        self.app.router.add_get('/api/v1/scraping/jobs/{job_id}', self._handle_get_scraping_job)
        
    async def _setup_static_routes(self):
        """Setup static file serving"""
        
        # Serve API documentation
        docs_dir = Path(__file__).parent.parent / "docs" / "api"
        if docs_dir.exists():
            self.app.router.add_static('/docs/static', docs_dir)
            
        # Serve frontend if available
        frontend_dir = Path(__file__).parent.parent / "frontend-nextjs" / "out"
        if frontend_dir.exists():
            self.app.router.add_static('/app', frontend_dir)
            
    async def _start_server(self):
        """Start web server"""
        
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        
        self.site = web.TCPSite(self.runner, self.host, self.port)
        await self.site.start()
        
    # Handler methods
    async def _handle_root(self, request):
        """Root endpoint handler"""
        
        return web.json_response({
            "service": "Sparkling-Owl-Spin API Gateway",
            "version": "1.0.0",
            "status": "operational",
            "endpoints": {
                "health": "/health",
                "status": "/status",
                "docs": "/docs",
                "api": "/api/v1"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    async def _handle_health(self, request):
        """Health check endpoint"""
        
        # Import here to avoid circular imports
        from .orchestrator import orchestrator
        
        try:
            system_status = orchestrator.get_system_status()
            
            health_status = {
                "status": "healthy" if system_status["orchestrator"]["initialized"] else "degraded",
                "timestamp": datetime.now().isoformat(),
                "components": {
                    "orchestrator": "healthy" if system_status["orchestrator"]["initialized"] else "down",
                    "engines": f"{system_status['engines']['initialized']}/{system_status['engines']['registered']}",
                    "workflows": f"{system_status['workflows']['active']} active",
                    "api_gateway": "healthy"
                },
                "uptime": system_status["orchestrator"]["uptime"],
                "version": "1.0.0"
            }
            
            status_code = 200 if health_status["status"] == "healthy" else 503
            return web.json_response(health_status, status=status_code)
            
        except Exception as e:
            return web.json_response({
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }, status=503)
            
    async def _handle_status(self, request):
        """System status endpoint"""
        
        from .orchestrator import orchestrator
        
        try:
            system_status = orchestrator.get_system_status()
            api_uptime = (datetime.now() - self.api_stats["uptime_start"]).total_seconds()
            
            return web.json_response({
                "system": system_status,
                "api": {
                    "uptime": api_uptime,
                    "total_requests": self.api_stats["total_requests"],
                    "active_requests": len(self.active_requests),
                    "success_rate": (
                        self.api_stats["successful_requests"] / max(1, self.api_stats["total_requests"]) * 100
                    )
                },
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
            
    async def _handle_docs(self, request):
        """API documentation endpoint"""
        
        # Simple HTML documentation page
        docs_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Sparkling-Owl-Spin API Documentation</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #2c3e50; }
                h2 { color: #3498db; margin-top: 30px; }
                .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }
                .method { font-weight: bold; color: #e74c3c; }
                code { background: #ecf0f1; padding: 2px 4px; }
            </style>
        </head>
        <body>
            <h1>🦉 Sparkling-Owl-Spin API Documentation</h1>
            
            <h2>Core Endpoints</h2>
            <div class="endpoint">
                <div><span class="method">GET</span> <code>/health</code></div>
                <div>System health check</div>
            </div>
            
            <div class="endpoint">
                <div><span class="method">GET</span> <code>/status</code></div>
                <div>Detailed system status</div>
            </div>
            
            <h2>Workflow Management</h2>
            <div class="endpoint">
                <div><span class="method">POST</span> <code>/api/v1/workflows</code></div>
                <div>Create new workflow</div>
            </div>
            
            <div class="endpoint">
                <div><span class="method">GET</span> <code>/api/v1/workflows</code></div>
                <div>List all workflows</div>
            </div>
            
            <h2>Security</h2>
            <div class="endpoint">
                <div><span class="method">POST</span> <code>/api/v1/security/pentest-sessions</code></div>
                <div>Create penetration testing session</div>
            </div>
            
            <h2>Data Extraction</h2>
            <div class="endpoint">
                <div><span class="method">GET</span> <code>/api/v1/data/swedish/vehicles</code></div>
                <div>Search Swedish vehicle data</div>
            </div>
            
            <p><strong>⚠️ ENDAST FÖR AUKTORISERAD PENETRATIONSTESTNING</strong></p>
        </body>
        </html>
        """
        
        return web.Response(text=docs_html, content_type='text/html')
        
    async def _handle_create_workflow(self, request):
        """Create workflow endpoint"""
        
        try:
            data = await request.json()
            
            # Import orchestrator
            from .orchestrator import orchestrator
            
            workflow_id = await orchestrator.create_workflow(data)
            
            return web.json_response({
                "workflow_id": workflow_id,
                "status": "created",
                "message": "Workflow created successfully"
            }, status=201)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
            
    async def _handle_execute_workflow(self, request):
        """Execute workflow endpoint"""
        
        try:
            workflow_id = request.match_info['workflow_id']
            
            from .orchestrator import orchestrator
            
            result = await orchestrator.execute_workflow(workflow_id)
            
            return web.json_response(result)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
            
    async def _handle_list_workflows(self, request):
        """List workflows endpoint"""
        
        try:
            from .orchestrator import orchestrator
            
            workflows = []
            for workflow_id, workflow in orchestrator.active_workflows.items():
                workflows.append({
                    "workflow_id": workflow_id,
                    "name": workflow.name,
                    "type": workflow.workflow_type.value,
                    "status": workflow.status.value,
                    "created_at": workflow.created_at.isoformat(),
                    "target_domains": workflow.target_domains
                })
                
            return web.json_response({
                "workflows": workflows,
                "total": len(workflows)
            })
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
            
    async def _handle_create_pentest_session(self, request):
        """Create penetration testing session endpoint"""
        
        try:
            data = await request.json()
            
            from .orchestrator import orchestrator
            
            session_id = await orchestrator.security_controller.create_pentest_session(
                target_domains=data.get('target_domains', []),
                operator=data.get('operator', 'api_user'),
                purpose=data.get('purpose', 'API initiated pentest'),
                duration_hours=data.get('duration_hours', 24)
            )
            
            return web.json_response({
                "session_id": session_id,
                "status": "created",
                "message": "Penetration testing session created"
            }, status=201)
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
            
    async def _handle_search_vehicles(self, request):
        """Search vehicles endpoint"""
        
        try:
            # Get search parameters
            params = dict(request.query)
            
            # Import vehicle adapter
            from ..data_processing.sources.swedish_data import SwedishVehicleDataAdapter
            
            # This would normally go through orchestrator
            # För now, direct call för demonstration
            return web.json_response({
                "message": "Vehicle search endpoint - requires workflow execution",
                "suggested_workflow": {
                    "type": "swedish_data_extraction",
                    "steps": [
                        {
                            "engine": "swedish_vehicle_data",
                            "parameters": {
                                "vehicle_search": params
                            }
                        }
                    ]
                }
            })
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
            
    async def _handle_get_metrics(self, request):
        """Get system metrics endpoint"""
        
        try:
            from .orchestrator import orchestrator
            
            system_status = orchestrator.get_system_status()
            
            return web.json_response({
                "system_metrics": system_status["metrics"],
                "api_metrics": self.api_stats,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            return web.json_response({"error": str(e)}, status=500)
            
    async def _handle_api_spec(self, request):
        """API specification endpoint"""
        
        # OpenAPI specification
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Sparkling-Owl-Spin API",
                "version": "1.0.0",
                "description": "Enhanced web scraping and penetration testing platform"
            },
            "servers": [
                {
                    "url": f"http://{self.host}:{self.port}",
                    "description": "Local development server"
                }
            ],
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health check",
                        "responses": {
                            "200": {"description": "System is healthy"}
                        }
                    }
                },
                "/api/v1/workflows": {
                    "post": {
                        "summary": "Create workflow",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "type": {"type": "string"},
                                            "target_domains": {
                                                "type": "array",
                                                "items": {"type": "string"}
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        return web.json_response(spec)
        
    # Placeholder handlers för other endpoints
    async def _handle_get_workflow(self, request):
        return web.json_response({"message": "Get workflow details"})
        
    async def _handle_delete_workflow(self, request):
        return web.json_response({"message": "Delete workflow"})
        
    async def _handle_get_workflow_results(self, request):
        return web.json_response({"message": "Get workflow results"})
        
    async def _handle_get_workflow_status(self, request):
        return web.json_response({"message": "Get workflow status"})
        
    async def _handle_authorize_domain(self, request):
        return web.json_response({"message": "Authorize domain"})
        
    async def _handle_list_authorized_domains(self, request):
        return web.json_response({"message": "List authorized domains"})
        
    async def _handle_revoke_domain(self, request):
        return web.json_response({"message": "Revoke domain authorization"})
        
    async def _handle_list_pentest_sessions(self, request):
        return web.json_response({"message": "List pentest sessions"})
        
    async def _handle_close_pentest_session(self, request):
        return web.json_response({"message": "Close pentest session"})
        
    async def _handle_get_security_events(self, request):
        return web.json_response({"message": "Get security events"})
        
    async def _handle_export_security_log(self, request):
        return web.json_response({"message": "Export security log"})
        
    async def _handle_get_api_metrics(self, request):
        return web.json_response(self.api_stats)
        
    async def _handle_get_engine_metrics(self, request):
        return web.json_response({"message": "Get engine metrics"})
        
    async def _handle_get_system_status(self, request):
        return await self._handle_status(request)
        
    async def _handle_get_system_health(self, request):
        return await self._handle_health(request)
        
    async def _handle_search_companies(self, request):
        return web.json_response({"message": "Search companies"})
        
    async def _handle_create_scraping_job(self, request):
        return web.json_response({"message": "Create scraping job"})
        
    async def _handle_list_scraping_jobs(self, request):
        return web.json_response({"message": "List scraping jobs"})
        
    async def _handle_get_scraping_job(self, request):
        return web.json_response({"message": "Get scraping job"})
        
    async def _print_api_status(self):
        """Print API Gateway status"""
        
        print("\n" + "="*80)
        print("🌐 API GATEWAY STATUS")
        print("="*80)
        
        print(f"🚀 Server: http://{self.host}:{self.port}")
        print(f"📡 Registered Endpoints: {len(self.endpoints)}")
        print(f"🔒 CORS Origins: {len(self.cors_origins)}")
        print(f"⚡ Max Request Size: {self.max_request_size // 1024 // 1024}MB")
        
        print(f"\n📊 Request Statistics:")
        print(f"   • Total Requests: {self.api_stats['total_requests']}")
        print(f"   • Success Rate: {(self.api_stats['successful_requests'] / max(1, self.api_stats['total_requests']) * 100):.1f}%")
        print(f"   • Active Requests: {len(self.active_requests)}")
        
        print(f"\n🔗 Key Endpoints:")
        endpoints = [
            ("GET", "/health", "System health check"),
            ("GET", "/docs", "API documentation"),
            ("POST", "/api/v1/workflows", "Create workflow"),
            ("POST", "/api/v1/security/pentest-sessions", "Create pentest session"),
            ("GET", "/api/v1/data/swedish/vehicles", "Search vehicles")
        ]
        
        for method, path, desc in endpoints:
            print(f"   {method:6} {path:35} - {desc}")
            
        print("="*80)
        print("✅ API Gateway Ready för Authorized Operations")
        print("="*80 + "\n")
        
    def get_api_status(self) -> Dict[str, Any]:
        """Get API Gateway status"""
        
        uptime = (datetime.now() - self.api_stats["uptime_start"]).total_seconds()
        
        return {
            "initialized": self.initialized,
            "server": f"http://{self.host}:{self.port}",
            "uptime": uptime,
            "endpoints": len(self.endpoints),
            "active_requests": len(self.active_requests),
            "statistics": self.api_stats,
            "rate_limits": len(self.rate_limits)
        }
        
    async def shutdown(self):
        """Shutdown API Gateway"""
        
        logger.info("🔄 Shutting down API Gateway...")
        
        if self.site:
            await self.site.stop()
            
        if self.runner:
            await self.runner.cleanup()
            
        self.initialized = False
        logger.info("✅ API Gateway shutdown complete")
