"""fixtures da suíte: banco de teste isolado + clientes logados por perfil"""

import os
import tempfile
from datetime import timedelta
from pathlib import Path

# aponta pra um banco de teste isolado ANTES de importar a app (nao mexe no .db local nem no de producao)
# gettempdir() resolve /tmp no linux e o diretorio temporario no windows
_TEST_DB = Path(tempfile.gettempdir()) / "opencode" / "esuda_pytest.db"
_TEST_DB.parent.mkdir(parents=True, exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB}"

from fastapi.testclient import TestClient

from app.main import app
from app.core.security import create_access_token, hash_senha
from app.database.database import Base, engine, SessionLocal
from app.models.models import Usuario

# limpa e recria as tabelas antes de cada teste (teste nao depende do outro)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def _nova_sessao():
    """abre uma sessao do banco de teste"""
    return SessionLocal()


def _criar_usuario_direto(nome: str, email: str, senha: str, papel: str) -> Usuario:
    """grava o usuario com hash direto no banco (pra nao depender do endpoint de cadastro)"""
    db = _nova_sessao()
    try:
        usuario = Usuario(nome=nome, email=email, senha=hash_senha(senha), papel=papel)
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
    finally:
        db.close()


def _headers_do_token(usuario: Usuario) -> dict:
    """gera o token na hora e devolve o header Authorization"""
    token = create_access_token(data={"sub": str(usuario.id), "papel": usuario.papel})
    return {"Authorization": f"Bearer {token}"}


def _headers_token_expirado(usuario: Usuario) -> dict:
    """token assinado certinho mas ja vencido (pro teste de expiracao)"""
    token = create_access_token(
        data={"sub": str(usuario.id), "papel": usuario.papel},
        expires_delta=timedelta(minutes=-10),
    )
    return {"Authorization": f"Bearer {token}"}


# usuarios de cada perfil, criados uma vez por sessao de teste
ADMIN = _criar_usuario_direto("Admin Esuda", "admin@esuda.edu.br", "adminSeguro123", "admin")
ORGANIZADOR = _criar_usuario_direto("Victor Org", "organizador@esuda.edu.br", "orgSeguro123", "organizador")
PARTICIPANTE = _criar_usuario_direto("Thiago Part", "participante@esuda.edu.br", "partSeguro123", "participante")


import pytest


@pytest.fixture()
def client():
    """cliente de teste com banco limpo a cada chamada de teste"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # recria os 3 perfis no banco limpo
    admin = _criar_usuario_direto(ADMIN.nome, ADMIN.email, "adminSeguro123", "admin")
    org = _criar_usuario_direto(ORGANIZADOR.nome, ORGANIZADOR.email, "orgSeguro123", "organizador")
    part = _criar_usuario_direto(PARTICIPANTE.nome, PARTICIPANTE.email, "partSeguro123", "participante")

    with TestClient(app) as c:
        c.admin = admin
        c.organizador = org
        c.participante = part
        c.admin_headers = _headers_do_token(admin)
        c.organizador_headers = _headers_do_token(org)
        c.participante_headers = _headers_do_token(part)
        yield c


@pytest.fixture()
def token_expirado_headers():
    """header com token ja expirado do participante"""
    return _headers_token_expirado(PARTICIPANTE)
