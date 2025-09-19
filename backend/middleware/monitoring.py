import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import psutil
import os

logger = logging.getLogger(__name__)

class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for monitoring API performance and system metrics"""
    
    def __init__(self, app, sample_rate: float = 1.0):
        super().__init__(app)
        self.sample_rate = sample_rate
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip monitoring for health checks and static files
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        start_time = time.time()
        self.request_count += 1
        
        # Process request
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            self.total_response_time += process_time
            
            # Log performance metrics
            if self.request_count % 100 == 0:  # Log every 100 requests
                avg_response_time = self.total_response_time / self.request_count
                error_rate = (self.error_count / self.request_count) * 100
                
                logger.info(
                    "Performance metrics",
                    extra={
                        "request_count": self.request_count,
                        "error_count": self.error_count,
                        "error_rate": f"{error_rate:.2f}%",
                        "avg_response_time": f"{avg_response_time:.3f}s",
                        "system_cpu": psutil.cpu_percent(),
                        "system_memory": psutil.virtual_memory().percent,
                        "process_memory": psutil.Process(os.getpid()).memory_percent()
                    }
                )
            
            # Add performance headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-Count"] = str(self.request_count)
            
            return response
            
        except Exception as e:
            self.error_count += 1
            process_time = time.time() - start_time
            
            logger.error(
                f"Request failed: {str(e)}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "process_time": process_time,
                    "error_count": self.error_count
                },
                exc_info=True
            )
            
            raise

class SystemMetrics:
    """System metrics collector"""
    
    @staticmethod
    def get_cpu_usage() -> float:
        """Get CPU usage percentage"""
        return psutil.cpu_percent(interval=1)
    
    @staticmethod
    def get_memory_usage() -> dict:
        """Get memory usage information"""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percentage": memory.percent
        }
    
    @staticmethod
    def get_disk_usage() -> dict:
        """Get disk usage information"""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percentage": (disk.used / disk.total) * 100
        }
    
    @staticmethod
    def get_process_info() -> dict:
        """Get current process information"""
        process = psutil.Process(os.getpid())
        return {
            "pid": process.pid,
            "memory_percent": process.memory_percent(),
            "cpu_percent": process.cpu_percent(),
            "num_threads": process.num_threads(),
            "create_time": process.create_time()
        }

def get_system_metrics() -> dict:
    """Get comprehensive system metrics"""
    return {
        "cpu": SystemMetrics.get_cpu_usage(),
        "memory": SystemMetrics.get_memory_usage(),
        "disk": SystemMetrics.get_disk_usage(),
        "process": SystemMetrics.get_process_info(),
        "timestamp": time.time()
    }
