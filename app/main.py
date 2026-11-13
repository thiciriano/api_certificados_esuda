"""sobe a api"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database.database import Base, engine
from app.api.v1.api import api_router

# cria as tabelas direto no start (sem drop_all, senao apagaria os dados de producao)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"❌ Erro ao conectar no banco de dados: {e}")
    raise

tags_metadata = [
    {"name": "Root", "description": "Status da API"},
    {"name": "Autenticação", "description": "Login e geração do token JWT"},
    {"name": "Usuários", "description": "Cadastro, consulta e gestão de usuários"},
    {"name": "Eventos", "description": "CRUD de eventos acadêmicos"},
    {"name": "Inscrições", "description": "Inscrições de participantes nos eventos"},
    {"name": "Certificados", "description": "Emissão e gestão de certificados"},
    {"name": "Categorias", "description": "Categorias de eventos"},
]

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "API para gerenciamento de eventos acadêmicos, inscrições e emissão de "
        "certificados do Esuda Certificados.\n\n"
        "Autenticação JWT: use o botão **Authorize** (ou o endpoint "
        f"`{settings.API_V1_STR}/auth/login`) para obter o token e acessar as rotas protegidas."
    ),
    openapi_tags=tags_metadata,
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router)


@app.get("/", tags=["Root"])
async def root():
    """so mostra uma mensagem"""
    return {"message": "Bem-vindo ao Esuda Certificados API", "docs": "/docs"}


@app.get("/health", tags=["Root"])
async def health_check():
    """checa se a api ta de pe"""
    return {"status": "healthy", "project": settings.PROJECT_NAME, "version": settings.VERSION}
