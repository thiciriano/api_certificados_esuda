"""variaveis de ambiente"""
from pydantic import PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Esuda Certificados"
    API_V1_STR: str = "/api/v1"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "esuda_certificados"
    BACKEND_CORS_ORIGINS: list = []

    @validator("POSTGRES_PORT", pre=True)
    def assemble_db_connection(cls, v):
        return int(v) if v else 5432

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
