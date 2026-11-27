"""variaveis de ambiente"""
from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Esuda Certificados"
    API_V1_STR: str = "/api/v1"
    VERSION: str = "2.0.0"
    # em producao essa chave vem do .env, nunca fica no codigo
    JWT_SECRET_KEY: str = "troque-essa-chave-no-producao"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    # sqlite local por padrao; no render vem o postgres pelo .env
    DATABASE_URL: str = "sqlite:///./esuda_certificados.db"
    DB_ECHO: bool = False  # vira True pra ver o sql no console
    BACKEND_CORS_ORIGINS: list = []

    @field_validator("DATABASE_URL", mode="before")
    def corrige_scheme_postgres(cls, v):
        # o render passa postgres://..., o sqlalchemy 2 so aceita postgresql://
        return v.replace("postgres://", "postgresql://", 1) if v.startswith("postgres://") else v

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
