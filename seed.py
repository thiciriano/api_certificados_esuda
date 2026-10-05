#!/usr/bin/env python3
"""cria uns dados de teste pra nao precisar digitar tudo no swagger.

so funciona com a api no ar (python run.py em outro terminal) e com o banco vazio."""

import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"


def popular_banco():
    print("🚀 Populando banco com dados de teste...")

    # categoria primeiro, o evento precisa de uma
    cat = requests.post(f"{BASE_URL}/categorias", json={
        "nome": "Workshop", "descricao": "Eventos Práticos"
    }).json()
    print(f"   ✅ Categoria criada: {cat.get('nome', 'Sem nome')} (ID: {cat.get('id')})")

    user = requests.post(f"{BASE_URL}/usuarios", json={
        "nome": "Thiago Henrique", "email": "thiago@esuda.edu.br",
        "senha": "123", "papel": "participante"
    }).json()
    print(f"   ✅ Usuário criado: {user.get('nome', 'Sem nome')} (ID: {user.get('id')}, Papel: {user.get('papel')})")

    event = requests.post(f"{BASE_URL}/eventos", json={
        "titulo": "Apresentação MVP Esuda", "descricao": "Defesa de ADS",
        "data_evento": "2026-11-10", "local": "Auditório",
        "capacidade": 30, "categoria_id": cat.get("id", 1)
    }).json()
    print(f"   ✅ Evento criado: {event.get('titulo', 'Sem título')} (ID: {event.get('id')})")

    inscricao = requests.post(f"{BASE_URL}/inscricoes", json={
        "usuario_id": user.get("id"),
        "evento_id": event.get("id")
    }).json()
    print(f"   ✅ Inscrição criada: ID {inscricao.get('id')}, Status: {inscricao.get('status')}")

    cert = requests.post(f"{BASE_URL}/certificados", json={
        "inscricao_id": inscricao.get("id")
    }).json()
    print(f"   ✅ Certificado emitido: ID {cert.get('id')}, Código: {cert.get('codigo_certificacao')}")

    print("\n✅ Banco pronto para demonstração!")


if __name__ == "__main__":
    popular_banco()
