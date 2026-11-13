"""testes de CRUD e operações principais (mínimo 4)"""


def test_crud_completo_de_usuario(client):
    """cria, lê, atualiza e deleta um usuário"""
    # cria
    r = client.post(
        "/api/v1/usuarios",
        json={"nome": "CRUD User", "email": "crud@esuda.edu.br", "senha": "crudSeguro123", "papel": "participante"},
    )
    assert r.status_code == 201
    user_id = r.json()["data"]["id"]
    assert r.json()["data"]["nome"] == "CRUD User"

    # lê pelo /me logando com ele
    login = client.post(
        "/api/v1/auth/login", data={"username": "crud@esuda.edu.br", "password": "crudSeguro123"}
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    r = client.get("/api/v1/usuarios/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["data"]["email"] == "crud@esuda.edu.br"

    # atualiza o proprio nome
    r = client.put(f"/api/v1/usuarios/{user_id}", json={"nome": "CRUD User Atualizado"}, headers=headers)
    assert r.status_code == 200
    assert r.json()["data"]["nome"] == "CRUD User Atualizado"

    # deleta como admin
    r = client.delete(f"/api/v1/usuarios/{user_id}", headers=client.admin_headers)
    assert r.status_code == 204


def test_crud_completo_de_evento_como_organizador(client):
    """cria, lê, atualiza e deleta um evento"""
    r = client.post(
        "/api/v1/categorias",
        json={"nome": "CRUD Categoria", "descricao": "teste"},
        headers=client.admin_headers,
    )
    cat_id = r.json()["data"]["id"]

    # cria
    r = client.post(
        "/api/v1/eventos",
        json={
            "titulo": "Evento CRUD",
            "descricao": "teste",
            "data_evento": "2027-10-10",
            "local": "Auditório",
            "capacidade": 20,
            "categoria_id": cat_id,
        },
        headers=client.organizador_headers,
    )
    assert r.status_code == 201
    evento_id = r.json()["data"]["id"]
    assert r.json()["data"]["vagas_disponiveis"] == 20  # abre com todas as vagas

    # lê
    r = client.get(f"/api/v1/eventos/{evento_id}")
    assert r.status_code == 200
    assert r.json()["titulo"] == "Evento CRUD"

    # atualiza
    r = client.put(
        f"/api/v1/eventos/{evento_id}",
        json={"local": "Sala 101"},
        headers=client.organizador_headers,
    )
    assert r.status_code == 200
    assert r.json()["data"]["local"] == "Sala 101"

    # deleta como admin
    r = client.delete(f"/api/v1/eventos/{evento_id}", headers=client.admin_headers)
    assert r.status_code == 204

    # sumiu mesmo
    r = client.get(f"/api/v1/eventos/{evento_id}")
    assert r.status_code == 404


def test_fluxo_inscricao_e_certificado(client):
    """inscricao baixa vaga e o certificado nasce da inscricao"""
    r = client.post(
        "/api/v1/categorias",
        json={"nome": "Fluxo Categoria", "descricao": "teste"},
        headers=client.admin_headers,
    )
    cat_id = r.json()["data"]["id"]

    r = client.post(
        "/api/v1/eventos",
        json={
            "titulo": "Evento Fluxo",
            "data_evento": "2027-12-01",
            "capacidade": 2,
            "categoria_id": cat_id,
        },
        headers=client.organizador_headers,
    )
    evento_id = r.json()["data"]["id"]

    # participante se inscreve, vaga cai pra 1
    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento_id},
        headers=client.participante_headers,
    )
    assert r.status_code == 201
    inscricao_id = r.json()["data"]["id"]

    r = client.get(f"/api/v1/eventos/{evento_id}")
    assert r.json()["vagas_disponiveis"] == 1

    # organizador emite o certificado da inscricao
    r = client.post(
        "/api/v1/certificados",
        json={"inscricao_id": inscricao_id},
        headers=client.organizador_headers,
    )
    assert r.status_code == 201
    assert r.json()["data"]["codigo_certificacao"].startswith("ESUDA-")

    # emitido pelo organizador, o participante ve o certificado dele
    r = client.get("/api/v1/certificados", headers=client.participante_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_crud_de_categoria(client):
    """organizador gerencia categorias"""
    r = client.post(
        "/api/v1/categorias",
        json={"nome": "Palestra", "descricao": "eventos grandes"},
        headers=client.organizador_headers,
    )
    assert r.status_code == 201
    cat_id = r.json()["data"]["id"]

    r = client.get("/api/v1/categorias")
    assert r.status_code == 200
    assert any(c["id"] == cat_id for c in r.json())

    r = client.put(
        f"/api/v1/categorias/{cat_id}",
        json={"descricao": "palestras e conferencias"},
        headers=client.organizador_headers,
    )
    assert r.status_code == 200
    assert r.json()["data"]["descricao"] == "palestras e conferencias"

    r = client.delete(f"/api/v1/categorias/{cat_id}", headers=client.admin_headers)
    assert r.status_code == 204


def test_listagem_de_eventos_e_publica(client):
    """consultar eventos nao exige login (consulta aberta)"""
    r = client.get("/api/v1/eventos")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
