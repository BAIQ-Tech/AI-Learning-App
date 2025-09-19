from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
import hashlib
from typing import Dict, Tuple
from collections import defaultdict, deque
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        # Store requests per IP: {ip: deque of timestamps}
        self.requests: Dict[str, deque] = defaultdict(deque)
        # Rate limit configurations
        self.limits = {
            "default": {"requests": 100, "window": 3600},  # 100 requests per hour
            "auth": {"requests": 10, "window": 300},       # 10 auth attempts per 5 minutes
            "api": {"requests": 1000, "window": 3600},     # 1000 API calls per hour
            "translation": {"requests": 50, "window": 3600}, # 50 translations per hour
            "chat": {"requests": 200, "window": 3600},     # 200 chat messages per hour
        }
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address"""
        # Check for forwarded headers first
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        return request.client.host if request.client else "unknown"
    
    def _get_rate_limit_key(self, request: Request, limit_type: str = "default") -> str:
        """Generate rate limit key for the request"""
        client_ip = self._get_client_ip(request)
        
        # For authenticated users, use user ID instead of IP
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # Hash the token to create a user-specific key
            token_hash = hashlib.sha256(auth_header.encode()).hexdigest()[:16]
            return f"{limit_type}:user:{token_hash}"
        
        return f"{limit_type}:ip:{client_ip}"
    
    def _cleanup_old_requests(self, key: str, window_seconds: int):
        """Remove old requests outside the time window"""
        current_time = time.time()
        cutoff_time = current_time - window_seconds
        
        # Remove requests older than the window
        while self.requests[key] and self.requests[key][0] < cutoff_time:
            self.requests[key].popleft()
    
    def is_rate_limited(self, request: Request, limit_type: str = "default") -> Tuple[bool, Dict[str, int]]:
        """
        Check if request should be rate limited
        
        Returns:
            (is_limited, rate_info)
        """
        key = self._get_rate_limit_key(request, limit_type)
        limit_config = self.limits.get(limit_type, self.limits["default"])
        
        current_time = time.time()
        window_seconds = limit_config["window"]
        max_requests = limit_config["requests"]
        
        # Cleanup old requests
        self._cleanup_old_requests(key, window_seconds)
        
        # Add current request
        self.requests[key].append(current_time)
        
        # Check if limit exceeded
        request_count = len(self.requests[key])
        is_limited = request_count > max_requests
        
        # Calculate reset time
        if self.requests[key]:
            oldest_request = self.requests[key][0]
            reset_time = int(oldest_request + window_seconds)
        else:
            reset_time = int(current_time + window_seconds)
        
        rate_info = {
            "limit": max_requests,
            "remaining": max(0, max_requests - request_count),
            "reset": reset_time,
            "window": window_seconds
        }
        
        if is_limited:
            logger.warning(
                f"Rate limit exceeded for {key}",
                extra={
                    "rate_limit_type": limit_type,
                    "request_count": request_count,
                    "limit": max_requests,
                    "client_ip": self._get_client_ip(request)
                }
            )
        
        return is_limited, rate_info

# Global rate limiter instance
rate_limiter = RateLimiter()

def check_rate_limit(limit_type: str = "default"):
    """Decorator to check rate limits on endpoints"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs (FastAPI dependency injection)
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # If no request found, skip rate limiting
                return await func(*args, **kwargs)
            
            is_limited, rate_info = rate_limiter.is_rate_limited(request, limit_type)
            
            if is_limited:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "X-RateLimit-Limit": str(rate_info["limit"]),
                        "X-RateLimit-Remaining": str(rate_info["remaining"]),
                        "X-RateLimit-Reset": str(rate_info["reset"]),
                        "Retry-After": str(rate_info["window"])
                    }
                )
            
            # Add rate limit headers to response
            response = await func(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
                response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
                response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
            
            return response
        
        return wrapper
    return decorator

def get_rate_limit_middleware():
    """FastAPI middleware for rate limiting"""
    async def middleware(request: Request, call_next):
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Determine rate limit type based on endpoint
        limit_type = "default"
        if request.url.path.startswith("/api/auth/"):
            limit_type = "auth"
        elif request.url.path.startswith("/api/translate"):
            limit_type = "translation"
        elif request.url.path.startswith("/api/conversation"):
            limit_type = "chat"
        elif request.url.path.startswith("/api/"):
            limit_type = "api"
        
        is_limited, rate_info = rate_limiter.is_rate_limited(request, limit_type)
        
        if is_limited:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "error_code": "RATE_LIMIT_EXCEEDED",
                    "rate_limit": rate_info
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info["limit"]),
                    "X-RateLimit-Remaining": str(rate_info["remaining"]),
                    "X-RateLimit-Reset": str(rate_info["reset"]),
                    "Retry-After": str(rate_info["window"])
                }
            )
        
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_info["reset"])
        
        return response
    
    return middleware
