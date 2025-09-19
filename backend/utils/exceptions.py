from fastapi import HTTPException, status
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AILearningException(Exception):
    """Base exception for AI Learning platform"""
    def __init__(self, message: str, error_code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class AuthenticationError(AILearningException):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed", details: Dict[str, Any] = None):
        super().__init__(message, "AUTH_ERROR", details)

class AuthorizationError(AILearningException):
    """Authorization related errors"""
    def __init__(self, message: str = "Access denied", details: Dict[str, Any] = None):
        super().__init__(message, "AUTHZ_ERROR", details)

class ValidationError(AILearningException):
    """Data validation errors"""
    def __init__(self, message: str = "Validation failed", details: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", details)

class DatabaseError(AILearningException):
    """Database related errors"""
    def __init__(self, message: str = "Database operation failed", details: Dict[str, Any] = None):
        super().__init__(message, "DB_ERROR", details)

class ExternalServiceError(AILearningException):
    """External service errors (OpenAI, etc.)"""
    def __init__(self, message: str = "External service error", details: Dict[str, Any] = None):
        super().__init__(message, "EXTERNAL_SERVICE_ERROR", details)

class RateLimitError(AILearningException):
    """Rate limiting errors"""
    def __init__(self, message: str = "Rate limit exceeded", details: Dict[str, Any] = None):
        super().__init__(message, "RATE_LIMIT_ERROR", details)

def handle_exception(exc: Exception) -> HTTPException:
    """Convert custom exceptions to HTTP exceptions"""
    
    if isinstance(exc, AuthenticationError):
        logger.warning(f"Authentication error: {exc.message}", extra={"error_code": exc.error_code})
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=exc.message,
            headers={"X-Error-Code": exc.error_code}
        )
    
    elif isinstance(exc, AuthorizationError):
        logger.warning(f"Authorization error: {exc.message}", extra={"error_code": exc.error_code})
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=exc.message,
            headers={"X-Error-Code": exc.error_code}
        )
    
    elif isinstance(exc, ValidationError):
        logger.warning(f"Validation error: {exc.message}", extra={"error_code": exc.error_code})
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.message,
            headers={"X-Error-Code": exc.error_code}
        )
    
    elif isinstance(exc, DatabaseError):
        logger.error(f"Database error: {exc.message}", extra={"error_code": exc.error_code})
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
            headers={"X-Error-Code": exc.error_code}
        )
    
    elif isinstance(exc, ExternalServiceError):
        logger.error(f"External service error: {exc.message}", extra={"error_code": exc.error_code})
        return HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable",
            headers={"X-Error-Code": exc.error_code}
        )
    
    elif isinstance(exc, RateLimitError):
        logger.warning(f"Rate limit error: {exc.message}", extra={"error_code": exc.error_code})
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=exc.message,
            headers={"X-Error-Code": exc.error_code}
        )
    
    else:
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
