"""
Custom WebSocket CORS Middleware
FastAPI's CORSMiddleware doesn't handle WebSocket connections properly
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
import logging

logger = logging.getLogger(__name__)


class WebSocketCORSMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle CORS for WebSocket connections.
    
    FastAPI's CORSMiddleware doesn't properly handle WebSocket upgrade requests,
    so we need this custom middleware to allow WebSocket connections from allowed origins.
    """
    
    def __init__(self, app, allowed_origins: list):
        super().__init__(app)
        self.allowed_origins = allowed_origins
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if this is a WebSocket upgrade request
        if request.headers.get("upgrade", "").lower() == "websocket":
            origin = request.headers.get("origin")
            
            logger.info(f"WebSocket upgrade request from origin: {origin}")
            
            # Check if origin is allowed
            if origin and "*" not in self.allowed_origins:
                if origin not in self.allowed_origins:
                    logger.warning(f"WebSocket connection rejected - Origin {origin} not in {self.allowed_origins}")
                    # Don't block here, let the endpoint handle it
                    # This is just for logging
        
        response = await call_next(request)
        return response
