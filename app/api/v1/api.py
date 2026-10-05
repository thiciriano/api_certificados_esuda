"""junta as rotas de cada entidade"""
from fastapi import APIRouter

from app.api.v1.routers import usuarios
from app.api.v1.routers import categorias
from app.api.v1.routers import certificados
from app.api.v1.routers import eventos
from app.api.v1.routers import inscricoes

api_router = APIRouter()

api_router.include_router(usuarios.router, tags=["Usuários"])
api_router.include_router(eventos.router, tags=["Eventos"])
api_router.include_router(inscricoes.router, tags=["Inscrições"])
api_router.include_router(certificados.router, tags=["Certificados"])
api_router.include_router(categorias.router, tags=["Categorias"])
