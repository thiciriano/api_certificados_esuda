#!/usr/bin/env python3
"""cria uns dados de teste pra nao precisar digitar tudo no swagger.

so funciona com a api no ar (python run.py em outro terminal).
o admin vai direto no banco (a API nao deixa ninguem se promover a admin),
o resto é tudo pela API pra mostrar o fluxo real com JWT."""

import getpass
import os

import requests
from sqlalchemy.orm import Session

from app.core.security import hash_senha
from app.database.database import SessionLocal
from app.models.models import Usuario

# a porta pode mudar: BASE_URL="http://localhost:8080/api/v1" python seed.py
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000/api/v1")


def criar_admin(db: Session, senha: str) -> dict:
    """grava o admin direto no banco com senha em hash (a API nao deixa ninguem se promover a admin)"""
    admin = db.query(Usuario).filter(Usuario.email == "admin@esuda.edu.br").first()
    if admin:
        admin.senha = hash_senha(senha)  # atualiza o hash (usuarios da 1AV tinham senha pura)
        print("   ✅ Admin já existia, senha atualizada para hash")
    else:
        admin = Usuario(nome="Admin Esuda", email="admin@esuda.edu.br",
                        senha=hash_senha(senha), papel="admin")
        db.add(admin)
        print("   ✅ Admin criado: admin@esuda.edu.br")
    db.commit()
    db.refresh(admin)
    return {"id": admin.id, "papel": admin.papel}


def logar(email: str, senha: str) -> dict:
    """faz login e devolve o header de Authorization com o token"""
    r = requests.post(f"{BASE_URL}/auth/login", data={"username": email, "password": senha})
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def popular_banco():
    print("🚀 Populando banco com dados de teste...")
    senha_admin = getpass.getpass("🔐 Senha do admin (escondida, min 6): ")
    if len(senha_admin) < 6:
        print("   ❌ A senha precisa de pelo menos 6 caracteres")
        raise SystemExit(1)

    db = SessionLocal()
    try:
        criar_admin(db, senha_admin)
    finally:
        db.close()

    senha_demo = "senhaSegura123"
    admin_headers = logar("admin@esuda.edu.br", senha_admin)

    # organizador e participante: tenta cadastrar pela API (auto-cadastro);
    # se ja existirem (ex: banco da 1AV com senha em texto puro), atualiza o hash direto
    db = SessionLocal()
    try:
        for nome, email, papel in [
            ("Victor Oliveira", "victor@esuda.edu.br", "organizador"),
            ("Thiago Henrique", "thiago@esuda.edu.br", "participante"),
        ]:
            r = requests.post(f"{BASE_URL}/usuarios", json={
                "nome": nome, "email": email, "senha": senha_demo, "papel": papel
            })
            if r.status_code == 201:
                print(f"   ✅ Usuario {email} ({papel}) criado")
            else:
                # ja existia: troca a senha pura pelo hash (login volta a funcionar)
                db.query(Usuario).filter(Usuario.email == email).update(
                    {"senha": hash_senha(senha_demo)}
                )
                db.commit()
                print(f"   ✅ Usuario {email} já existia, senha atualizada para hash")
    finally:
        db.close()

    org_headers = logar("victor@esuda.edu.br", senha_demo)
    part_headers = logar("thiago@esuda.edu.br", senha_demo)

    # categoria pelo admin, evento pelo organizador (cada um no seu perfil)
    cat = requests.post(f"{BASE_URL}/categorias", json={
        "nome": "Workshop", "descricao": "Eventos Práticos"
    }, headers=admin_headers).json()
    if "data" not in cat:  # ja existia de uma rodada anterior
        cat = next(c for c in requests.get(f"{BASE_URL}/categorias").json() if c["nome"] == "Workshop")
        cat = {"data": cat}
        print(f"   ✅ Categoria Workshop já existia (ID: {cat['data']['id']})")
    else:
        print(f"   ✅ Categoria criada: {cat['data']['nome']} (ID: {cat['data']['id']})")

    event = requests.post(f"{BASE_URL}/eventos", json={
        "titulo": "Apresentação MVP Esuda", "descricao": "Defesa de ADS",
        "data_evento": "2026-12-10", "local": "Auditório",
        "capacidade": 30, "categoria_id": cat["data"]["id"]
    }, headers=org_headers).json()
    if "data" not in event:  # titulo unico (R2), ja existia
        event = {"data": requests.get(f"{BASE_URL}/eventos").json()[0]}
        print(f"   ✅ Evento já existia (ID: {event['data']['id']})")
    else:
        print(f"   ✅ Evento criado: {event['data']['titulo']} (ID: {event['data']['id']})")

    # participante se inscreve (o usuario vem do token, nao do body)
    inscricao = requests.post(f"{BASE_URL}/inscricoes", json={
        "evento_id": event["data"]["id"]
    }, headers=part_headers).json()
    if "data" not in inscricao:  # ja inscrito (R4)
        inscricao = {"data": requests.get(f"{BASE_URL}/inscricoes", headers=part_headers).json()[0]}
        print(f"   ✅ Inscrição já existia: ID {inscricao['data']['id']}, Status: {inscricao['data']['status']}")
    else:
        print(f"   ✅ Inscrição criada: ID {inscricao['data']['id']}, Status: {inscricao['data']['status']}")

    # organizador emite o certificado da inscrição
    cert = requests.post(f"{BASE_URL}/certificados", json={
        "inscricao_id": inscricao["data"]["id"]
    }, headers=org_headers).json()
    if "data" not in cert:  # ja emitido (R10)
        cert = {"data": requests.get(f"{BASE_URL}/certificados", headers=org_headers).json()[0]}
        print(f"   ✅ Certificado já existia: ID {cert['data']['id']}, Código: {cert['data']['codigo_certificacao']}")
    else:
        print(f"   ✅ Certificado emitido: ID {cert['data']['id']}, Código: {cert['data']['codigo_certificacao']}")

    print("\n✅ Banco pronto para demonstração!")
    print(f"   👤 Admin:       admin@esuda.edu.br (a senha que você digitou)")
    print(f"   👤 Organizador: victor@esuda.edu.br / {senha_demo}")
    print(f"   👤 Participante: thiago@esuda.edu.br / {senha_demo}")


if __name__ == "__main__":
    popular_banco()
