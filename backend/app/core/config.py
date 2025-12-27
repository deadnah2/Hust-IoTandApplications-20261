from pydantic_settings import BaseSettings
from typing import List, Optional
from pydantic import model_validator, AnyHttpUrl

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartHome Backend"
    API_V1_STR: str = "/api/v1"
    
    # CORS (Frontend URLs) - Default includes common dev ports
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",  # React default
        "http://localhost:8080",  # Vue default
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]

    # MongoDB Configuration
    MONGO_ROOT_USERNAME: str
    MONGO_ROOT_PASSWORD: str
    MONGO_DATABASE_NAME: str
    MONGO_HOST: str
    MONGO_PORT: int
    MONGODB_URL: Optional[str] = None

    @model_validator(mode='after')
    def assemble_db_connection(self) -> 'Settings':
        if self.MONGODB_URL is None:
            self.MONGODB_URL = f"mongodb://{self.MONGO_ROOT_USERNAME}:{self.MONGO_ROOT_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}"
        return self

    # Security (JWT)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # MQTT Configuration
    MQTT_BROKER: str
    MQTT_PORT: int

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
