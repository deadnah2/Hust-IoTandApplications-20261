import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.lifespan import lifespan
from app.api.api import api_router

# Khởi tạo FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)


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

