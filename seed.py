#!/usr/bin/env python3
"""Popula o banco com dados de demonstração para a apresentação.

Funciona em dois cenários:

1. Local (padrão): API em http://localhost:8000 e banco local.
2. Ambiente publicado: defina BASE_URL apontando para a API do Render.

Uso:
    python seed.py                              # local
    BASE_URL=https://api-certificados-esuda.onrender.com/api/v1 python seed.py

O admin é opcional: a API não permite auto-promoção a admin (R14). Para criar/
atualizar o admin, defina SENHA_ADMIN (ou execute o script no Shell do Render,
onde DATABASE_URL já aponta para o Postgres de produção). Mesmo sem admin, o
script funciona: o organizador cria a categoria, conforme a matriz de permissões.
"""

import os
from datetime import date, timedelta

import requests
from sqlalchemy.orm import Session

from app.core.security import hash_senha
from app.database.database import SessionLocal
from app.models.models import Usuario

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000/api/v1").rstrip("/")
SENHA_DEMO = os.environ.get("SENHA_DEMO", "senhaSegura123")
SENHA_ADMIN = os.environ.get("SENHA_ADMIN")  # opcional
EMAIL_ADMIN = "admin@esuda.edu.br"

USUARIOS_DEMO = [
    ("Victor Oliveira", "victor@esuda.edu.br", "organizador"),
    ("Thiago Henrique", "thiago@esuda.edu.br", "participante"),
]


def logar(email: str, senha: str) -> dict | None:
    """devolve o header Bearer ou None se as credenciais nao funcionarem."""
    r = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": email, "password": senha},
        timeout=60,
    )
    if r.status_code == 200:
        return {"Authorization": f"Bearer {r.json()['access_token']}"}
    return None


def criar_admin_local(senha: str) -> None:
    """grava o admin direto no banco (a API nao deixa ninguem se promover)."""
    db: Session = SessionLocal()
    try:
        admin = db.query(Usuario).filter(Usuario.email == EMAIL_ADMIN).first()
        if admin:
            admin.senha = hash_senha(senha)
            print("   ✅ Admin já existia; senha atualizada para hash")
        else:
            db.add(
                Usuario(
                    nome="Admin Esuda",
                    email=EMAIL_ADMIN,
                    senha=hash_senha(senha),
                    papel="admin",
                    is_active=True,
                )
            )
            print("   ✅ Admin criado direto no banco")
        db.commit()
    finally:
        db.close()


def garantir_usuario(nome: str, email: str, papel: str, db: Session) -> None:
    """cria pela API; se ja existir, confere o login e corrige o hash se preciso."""
    r = requests.post(
        f"{BASE_URL}/usuarios",
        json={"nome": nome, "email": email, "senha": SENHA_DEMO, "papel": papel},
        timeout=60,
    )
    if r.status_code == 201:
        print(f"   ✅ {email} ({papel}) criado")
        return

    if logar(email, SENHA_DEMO):
        print(f"   ✅ {email} já existia e faz login com a senha da demo")
        return

    # banco da 1AV pode ter senha em texto puro; so corrigimos se o banco for local
    try:
        db.query(Usuario).filter(Usuario.email == email).update(
            {"senha": hash_senha(SENHA_DEMO)}
        )
        db.commit()
        print(f"   ✅ {email} já existia; senha convertida para hash")
    except Exception:
        print(f"   ⚠️ {email} já existia com outra senha — use SENHA_DEMO para alterá-la")


def buscar_ou_criar(caminho: str, chave: str, valor: str, corpo: dict, headers: dict) -> dict:
    """evita duplicidade nas rodadas seguintes do seed."""
    r = requests.post(f"{BASE_URL}/{caminho}", json=corpo, headers=headers, timeout=60)
    if "data" in r.json():
        print(f"   ✅ {caminho}: {valor} (ID {r.json()['data']['id']})")
        return r.json()["data"]

    lista = requests.get(f"{BASE_URL}/{caminho}", headers=headers, timeout=60).json()
    for item in lista:
        if item.get(chave) == valor:
            print(f"   ✅ {caminho}: {valor} já existia (ID {item['id']})")
            return item
    raise RuntimeError(f"Não foi possível criar/encontrar {caminho}: {r.status_code} {r.text}")


def popular_banco() -> None:
    print(f"🚀 Populando banco de demonstração via {BASE_URL}")

    senha_admin = SENHA_ADMIN
    local = "localhost" in BASE_URL or "127.0.0.1" in BASE_URL
    if not senha_admin and local:
        import getpass

        while not senha_admin:
            senha_admin = getpass.getpass("🔐 Senha do admin (escondida, mínimo 6): ")
            if len(senha_admin) < 6:
                print("   ❌ A senha precisa de pelo menos 6 caracteres")
                senha_admin = ""
    elif not senha_admin:
        print("   ℹ️ SENHA_ADMIN não definida: seguindo sem admin (organizador cria a categoria)")

    admin_headers = None
    if senha_admin:
        try:
            criar_admin_local(senha_admin)
        except Exception as e:
            print(f"   ⚠️ Não foi possível gravar admin no banco ({e}); tentando login existente")
        admin_headers = logar(EMAIL_ADMIN, senha_admin)
        if admin_headers:
            print("   ✅ Login de admin OK")

    db: Session = SessionLocal()
    try:
        for nome, email, papel in USUARIOS_DEMO:
            garantir_usuario(nome, email, papel, db)
    finally:
        db.close()

    org_headers = logar("victor@esuda.edu.br", SENHA_DEMO)
    part_headers = logar("thiago@esuda.edu.br", SENHA_DEMO)
    if not org_headers or not part_headers:
        raise RuntimeError("Não foi possível logar com os usuários de demonstração")

    # admin quando disponível; senão o organizador gerencia categorias ( matriz 2AV )
    headers_categoria = admin_headers or org_headers

    cat = buscar_ou_criar(
        "categorias",
        "nome",
        "Workshop",
        {"nome": "Workshop", "descricao": "Eventos Práticos"},
        headers_categoria,
    )

    data_evento = (date.today() + timedelta(days=30)).isoformat()
    evento = buscar_ou_criar(
        "eventos",
        "titulo",
        "Apresentação MVP Esuda",
        {
            "titulo": "Apresentação MVP Esuda",
            "descricao": "Defesa de ADS",
            "data_evento": data_evento,
            "local": "Auditório",
            "capacidade": 30,
            "categoria_id": cat["id"],
        },
        org_headers,
    )

    r = requests.post(
        f"{BASE_URL}/inscricoes",
        json={"evento_id": evento["id"]},
        headers=part_headers,
        timeout=60,
    )
    if "data" in r.json():
        inscricao = r.json()["data"]
        print(f"   ✅ Inscrição criada (ID {inscricao['id']})")
    else:
        inscricoes = requests.get(
            f"{BASE_URL}/inscricoes", headers=part_headers, timeout=60
        ).json()
        inscricao = next(i for i in inscricoes if i["evento_id"] == evento["id"])
        print(f"   ✅ Inscrição já existia (ID {inscricao['id']})")

    r = requests.post(
        f"{BASE_URL}/certificados",
        json={"inscricao_id": inscricao["id"]},
        headers=org_headers,
        timeout=60,
    )
    if "data" in r.json():
        certificado = r.json()["data"]
        print(f"   ✅ Certificado emitido: {certificado['codigo_certificacao']}")
    else:
        certificados = requests.get(
            f"{BASE_URL}/certificados", headers=org_headers, timeout=60
        ).json()
        certificado = next(c for c in certificados if c["inscricao_id"] == inscricao["id"])
        print(f"   ✅ Certificado já existia: {certificado['codigo_certificacao']}")

    print("\n✅ Banco pronto para demonstração!")
    print("   Credenciais para o botão Authorize do Swagger (username = e-mail):")
    if admin_headers:
        print(f"   👤 Admin:       {EMAIL_ADMIN} (senha definida em SENHA_ADMIN)")
    print(f"   👤 Organizador: victor@esuda.edu.br / {SENHA_DEMO}")
    print(f"   👤 Participante: thiago@esuda.edu.br / {SENHA_DEMO}")
    print(f"   📄 Swagger: {BASE_URL.replace('/api/v1', '')}/docs")


if __name__ == "__main__":
    popular_banco()
