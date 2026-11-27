"""testes das regras de negocio R1 a R13 (mínimo 6)"""


def _criar_categoria(client, nome="Regra Categoria"):
    r = client.post(
        "/api/v1/categorias",
        json={"nome": nome, "descricao": "teste"},
        headers=client.admin_headers,
    )
    return r.json()["data"]["id"]


def _criar_evento(client, titulo, capacidade=10, data_evento="2027-11-20", cat_id=None):
    r = client.post(
        "/api/v1/eventos",
        json={
            "titulo": titulo,
            "data_evento": data_evento,
            "capacidade": capacidade,
            "categoria_id": cat_id or _criar_categoria(client, f"Cat {titulo}"),
        },
        headers=client.organizador_headers,
    )
    return r.json()


def _criar_participante(client, email):
    client.post(
        "/api/v1/usuarios",
        json={"nome": "Part Teste", "email": email, "senha": "partSeguro123", "papel": "participante"},
    )
    login = client.post("/api/v1/auth/login", data={"username": email, "password": "partSeguro123"})
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def test_r1_email_duplicado_e_bloqueado(client):
    """R1: email unico"""
    r = client.post(
        "/api/v1/usuarios",
        json={"nome": "Dup", "email": "duplicado@esuda.edu.br", "senha": "dupSeguro123", "papel": "participante"},
    )
    assert r.status_code == 201

    r = client.post(
        "/api/v1/usuarios",
        json={"nome": "Dup 2", "email": "duplicado@esuda.edu.br", "senha": "dupSeguro123", "papel": "participante"},
    )
    assert r.status_code == 400
    assert "cadastrado" in r.json()["detail"].lower()


def test_r2_titulo_de_evento_duplicado_e_bloqueado(client):
    """R2: titulo unico de evento"""
    _criar_evento(client, "Workshop Unico")
    r = client.post(
        "/api/v1/eventos",
        json={"titulo": "Workshop Unico", "data_evento": "2027-11-21", "capacidade": 5, "categoria_id": _criar_categoria(client)},
        headers=client.organizador_headers,
    )
    assert r.status_code == 400


def test_r3_r6_inscricao_respeita_capacidade_e_vagas(client):
    """R3/R6: capacidade maxima, sem vaga nao inscreve"""
    evento = _criar_evento(client, "Evento Lotado", capacidade=1)

    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )
    assert r.status_code == 201

    # segundo participante nao cabe mais
    headers2 = _criar_participante(client, "segundo@esuda.edu.br")
    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=headers2,
    )
    assert r.status_code == 400
    assert "vaga" in r.json()["detail"].lower()


def test_r4_inscricao_duplicada_e_bloqueada(client):
    """R4: nao inscreve duas vezes no mesmo evento"""
    evento = _criar_evento(client, "Evento Duplicado")
    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )
    assert r.status_code == 201

    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )
    assert r.status_code == 400


def test_r5_evento_com_data_passada_e_bloqueado(client):
    """R5: data futura"""
    r = client.post(
        "/api/v1/eventos",
        json={"titulo": "Evento Passado", "data_evento": "2020-01-01", "capacidade": 10, "categoria_id": _criar_categoria(client)},
        headers=client.organizador_headers,
    )
    assert r.status_code == 400
    assert "passada" in r.json()["detail"].lower()


def test_r7_cancelar_inscricao_devolve_a_vaga(client):
    """R7: cancela a propria inscricao e a vaga volta"""
    evento = _criar_evento(client, "Evento Cancela", capacidade=1)
    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )
    inscricao_id = r.json()["data"]["id"]

    # lotou
    r = client.get(f"/api/v1/eventos/{evento['data']['id']}")
    assert r.json()["vagas_disponiveis"] == 0

    # cancela a propria
    r = client.put(
        f"/api/v1/inscricoes/{inscricao_id}",
        json={"status": "cancelada"},
        headers=client.participante_headers,
    )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "cancelada"

    # vaga voltou
    r = client.get(f"/api/v1/eventos/{evento['data']['id']}")
    assert r.json()["vagas_disponiveis"] == 1


def test_r8_certificado_somente_para_inscricao_ativa(client):
    """R8: inscricao cancelada nao ganha certificado"""
    evento = _criar_evento(client, "Evento Cert Cancelado")
    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )
    inscricao_id = r.json()["data"]["id"]

    # cancela antes da emissao
    client.put(
        f"/api/v1/inscricoes/{inscricao_id}",
        json={"status": "cancelada"},
        headers=client.participante_headers,
    )

    r = client.post(
        "/api/v1/certificados",
        json={"inscricao_id": inscricao_id},
        headers=client.organizador_headers,
    )
    assert r.status_code == 400
    assert "ativa" in r.json()["detail"].lower()


def test_r10_cada_inscricao_gera_no_maximo_um_certificado(client):
    """R10: certificado unico por inscricao"""
    evento = _criar_evento(client, "Evento Cert Unico")
    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )
    inscricao_id = r.json()["data"]["id"]

    r1 = client.post(
        "/api/v1/certificados",
        json={"inscricao_id": inscricao_id},
        headers=client.organizador_headers,
    )
    assert r1.status_code == 201

    r2 = client.post(
        "/api/v1/certificados",
        json={"inscricao_id": inscricao_id},
        headers=client.organizador_headers,
    )
    assert r2.status_code == 400
    assert "já emitido" in r2.json()["detail"].lower()

    # so um certificado existe pra essa inscricao
    r = client.get("/api/v1/certificados", headers=client.admin_headers)
    assert len([c for c in r.json() if c["inscricao_id"] == inscricao_id]) == 1


def test_r11_categoria_com_eventos_nao_e_excluida(client):
    """R11: nao apaga categoria que tem evento vinculado"""
    cat_id = _criar_categoria(client, "Categoria Com Evento")
    client.post(
        "/api/v1/eventos",
        json={"titulo": "Evento da Cat", "data_evento": "2027-11-20", "capacidade": 10, "categoria_id": cat_id},
        headers=client.organizador_headers,
    )

    r = client.delete(f"/api/v1/categorias/{cat_id}", headers=client.admin_headers)
    assert r.status_code == 400
    assert "vinculad" in r.json()["detail"].lower()


def test_r12_capacidade_nao_fica_menor_que_inscricoes_ativas(client):
    """R12: nao baixa capacidade abaixo de quem ja esta inscrito"""
    evento = _criar_evento(client, "Evento Capacidade", capacidade=2)
    client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )
    # segundo participante lota o evento
    headers2 = _criar_participante(client, "capacidade2@esuda.edu.br")
    client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=headers2,
    )

    # com 2 inscritos, pedir capacidade 1 quebra a regra
    r = client.put(
        f"/api/v1/eventos/{evento['data']['id']}",
        json={"capacidade": 1},
        headers=client.organizador_headers,
    )
    assert r.status_code == 400
    assert "inscrições" in r.json()["detail"].lower()

    # dobrar a capacidade passa e recalcula as vagas (2 inscritos, 2 vagas livres)
    r = client.put(
        f"/api/v1/eventos/{evento['data']['id']}",
        json={"capacidade": 4},
        headers=client.organizador_headers,
    )
    assert r.status_code == 200
    assert r.json()["data"]["vagas_disponiveis"] == 2


def test_r13_certificado_cancelado_nao_muda_de_status(client):
    """R13: cancelado é terminal"""
    evento = _criar_evento(client, "Evento Cert Terminal")
    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )
    inscricao_id = r.json()["data"]["id"]

    r = client.post(
        "/api/v1/certificados",
        json={"inscricao_id": inscricao_id},
        headers=client.organizador_headers,
    )
    cert_id = r.json()["data"]["id"]

    # cancela
    r = client.put(f"/api/v1/certificados/{cert_id}", json={"status": "cancelado"}, headers=client.admin_headers)
    assert r.status_code == 200

    # tenta voltar pra emitido = bloqueado
    r = client.put(f"/api/v1/certificados/{cert_id}", json={"status": "emitido"}, headers=client.admin_headers)
    assert r.status_code == 400


def test_evento_cancelado_nao_aceita_inscricao(client):
    """regra nova: evento cancelado nao recebe inscricao"""
    evento = _criar_evento(client, "Evento Cancelado")
    client.put(
        f"/api/v1/eventos/{evento['data']['id']}",
        json={"status": "cancelado"},
        headers=client.admin_headers,
    )

    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )
    assert r.status_code == 400
    assert "ativo" in r.json()["detail"].lower()
