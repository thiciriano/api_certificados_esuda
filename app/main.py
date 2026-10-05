"""sobe a api"""

from fastapi import FastAPI

from app.core.config import settings
from app.database.database import Base, engine
from app.api.v1.api import api_router

# cria as tabelas direto no start
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="API para gerenciamento de certificados do Esuda Certificados",
)

app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():
    """so mostra uma mensagem"""
    return {"message": "Bem-vindo ao Esuda Certificados API", "docs": "/docs"}


@app.get("/health", tags=["Root"])
async def health_check():
    """checa se a api ta de pe"""
    return {"status": "healthy", "project": settings.PROJECT_NAME}
