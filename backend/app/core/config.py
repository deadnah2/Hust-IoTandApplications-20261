from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "IoT Application Backend"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    MONGODB_URL: str = "mongodb://localhost:27017"
    DB_NAME: str = "iot_app"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
