import sys
import os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.lifespan import lifespan
from app.api.api import api_router

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# Middleware để log mỗi request
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log thông tin request
        logger.info(f"📨 {request.method} {request.url.path}")
        
        response = await call_next(request)
        
        # Log thông tin response
        logger.info(f"✅ {request.method} {request.url.path} - Status: {response.status_code}")
        
        return response

# Khởi tạo FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Thêm logging middleware
app.add_middleware(LoggingMiddleware)

# Cấu hình CORS
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Đăng ký router
app.include_router(api_router, prefix=settings.API_V1_STR) 

@app.get("/")
def root():
    return {"message": "Welcome to IoT Application Backend"}


if __name__ == "__main__":
    import uvicorn
    import socket

    host = "0.0.0.0"
    port = 8000

    def get_local_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP

    local_ip = get_local_ip()

    print(f"Server running on:")
    print(f"  - Local:   http://localhost:{port}")
    print(f"  - Network: http://{local_ip}:{port}")

    uvicorn.run("app.main:app", host=host, port=port, reload=True)

