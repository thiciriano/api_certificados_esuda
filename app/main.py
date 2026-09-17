from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core.config import Configuracoes
from app.database.conexao import Base, engine

configuracoes = Configuracoes()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # cria as tabelas caso ainda não existam (o alembic também faz isso, isso aqui é só garantia)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=configuracoes.nome_projeto,
    description="API para gerenciar eventos acadêmicos, inscrições e emissão de certificados.",
    version="1.0",
    lifespan=lifespan
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Geral"])
def raiz():
    # só pra saber que a api está de pé
    return {"mensagem": "Esuda Certificados rodando! A documentação está em /docs"}
