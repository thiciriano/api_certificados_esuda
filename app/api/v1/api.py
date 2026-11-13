"""junta as rotas de cada entidade"""
from fastapi import APIRouter

from app.api.v1.routers import auth, usuarios, eventos, inscricoes, certificados, categorias
from app.core.config import settings

# tudo sob /api/v1 (o prefixo estava faltando, o seed.py ja chamava nesse caminho)
api_router = APIRouter(prefix=settings.API_V1_STR)

api_router.include_router(auth.router)
api_router.include_router(usuarios.router)
api_router.include_router(eventos.router)
api_router.include_router(inscricoes.router)
api_router.include_router(certificados.router)
api_router.include_router(categorias.router)
