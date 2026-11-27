"""testes de autorização e controle de acesso por perfil (mínimo 4)"""


def _criar_categoria(client, headers=None):
    """helper: cria uma categoria e devolve o id"""
    r = client.post(
        "/api/v1/categorias",
        json={"nome": "Categoria Teste", "descricao": "para os testes"},
        headers=headers or client.admin_headers,
    )
    return r.json()["data"]["id"]


def _criar_evento(client, headers=None, titulo="Evento Teste"):
    """helper: cria um evento (precisa de categoria) e devolve o corpo"""
    cat_id = _criar_categoria(client, headers)
    r = client.post(
        "/api/v1/eventos",
        json={
            "titulo": titulo,
            "descricao": "teste",
            "data_evento": "2027-11-20",
            "local": "Lab 3",
            "capacidade": 10,
            "categoria_id": cat_id,
        },
        headers=headers or client.organizador_headers,
    )
    return r.json()


def test_participante_nao_consegue_criar_evento(client):
    """papel participante cria evento = 403"""
    _criar_categoria(client)
    r = client.post(
        "/api/v1/eventos",
        json={
            "titulo": "Evento do Part",
            "data_evento": "2027-11-20",
            "capacidade": 10,
            "categoria_id": 1,
        },
        headers=client.participante_headers,
    )
    assert r.status_code == 403


def test_organizador_consegue_criar_evento(client):
    """papel organizador cria evento = 201"""
    cat_id = _criar_categoria(client)
    r = client.post(
        "/api/v1/eventos",
        json={
            "titulo": "Evento do Org",
            "data_evento": "2027-11-20",
            "capacidade": 10,
            "categoria_id": cat_id,
        },
        headers=client.organizador_headers,
    )
    assert r.status_code == 201


def test_organizador_nao_consegue_excluir_evento_mas_admin_consegue(client):
    """excluir evento é so admin (R9)"""
    evento = _criar_evento(client)

    # organizador tenta excluir = 403
    r = client.delete(f"/api/v1/eventos/{evento['data']['id']}", headers=client.organizador_headers)
    assert r.status_code == 403

    # admin exclui = 204
    r = client.delete(f"/api/v1/eventos/{evento['data']['id']}", headers=client.admin_headers)
    assert r.status_code == 204


def test_participante_nao_consegue_listar_usuarios(client):
    """gestão de usuarios é so admin"""
    r = client.get("/api/v1/usuarios", headers=client.participante_headers)
    assert r.status_code == 403

    r = client.get("/api/v1/usuarios", headers=client.admin_headers)
    assert r.status_code == 200


def test_nao_autenticado_e_diferente_de_autenticado_sem_permissao(client):
    """sem token = 401; com token mas sem perfil = 403"""
    r_sem_token = client.get("/api/v1/usuarios")
    r_com_token = client.get("/api/v1/usuarios", headers=client.participante_headers)
    assert r_sem_token.status_code == 401
    assert r_com_token.status_code == 403


def test_organizador_nao_consegue_cancelar_inscricao_de_outro_evento(client):
    """organizador so mexe em inscricao dos eventos que ele criou"""
    # participante se inscreve no evento do organizador A
    evento_a = _criar_evento(client, titulo="Evento Org A")
    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento_a["data"]["id"]},
        headers=client.participante_headers,
    )
    inscricao_id = r.json()["data"]["id"]

    # organizador B (outro usuario) tenta cancelar = 403
    outro_org = client.post(
        "/api/v1/usuarios",
        json={"nome": "Org B", "email": "orgb@esuda.edu.br", "senha": "orgbSeguro123", "papel": "organizador"},
    )
    assert outro_org.status_code == 201
    login_b = client.post(
        "/api/v1/auth/login",
        data={"username": "orgb@esuda.edu.br", "password": "orgbSeguro123"},
    )
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    r = client.put(f"/api/v1/inscricoes/{inscricao_id}", json={"status": "cancelada"}, headers=headers_b)
    assert r.status_code == 403

    # o dono do evento (organizador A) consegue cancelar
    r = client.put(
        f"/api/v1/inscricoes/{inscricao_id}",
        json={"status": "cancelada"},
        headers=client.organizador_headers,
    )
    assert r.status_code == 200


def test_participante_nao_consegue_cancelar_inscricao_de_outro_participante(client):
    """cada um so cancela a propria inscricao (R7)"""
    evento = _criar_evento(client)
    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )
    inscricao_id = r.json()["data"]["id"]

    # outro participante tenta cancelar a inscricao de terceiros = 403
    outro = client.post(
        "/api/v1/usuarios",
        json={"nome": "Outro Part", "email": "outropart@esuda.edu.br", "senha": "outroSeguro123", "papel": "participante"},
    )
    assert outro.status_code == 201
    login_outro = client.post(
        "/api/v1/auth/login",
        data={"username": "outropart@esuda.edu.br", "password": "outroSeguro123"},
    )
    headers_outro = {"Authorization": f"Bearer {login_outro.json()['access_token']}"}

    r = client.put(f"/api/v1/inscricoes/{inscricao_id}", json={"status": "cancelada"}, headers=headers_outro)
    assert r.status_code == 403


def test_ninguem_se_promove_a_admin_pelo_cadastro(client):
    """cadastro publico nao aceita papel admin"""
    r = client.post(
        "/api/v1/usuarios",
        json={"nome": "Espião", "email": "espio@esuda.edu.br", "senha": "espioSeguro123", "papel": "admin"},
    )
    assert r.status_code == 403


def test_participante_nao_altera_proprio_papel_pelo_put(client):
    """mesmo logado, ninguem altera o proprio papel de acesso"""
    r = client.put(
        f"/api/v1/usuarios/{client.participante.id}",
        json={"papel": "admin"},
        headers=client.participante_headers,
    )
    assert r.status_code == 403


def test_participante_nao_emite_certificado(client):
    """emissao de certificado é so organizador/admin"""
    evento = _criar_evento(client)
    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )
    inscricao_id = r.json()["data"]["id"]

    r = client.post(
        "/api/v1/certificados",
        json={"inscricao_id": inscricao_id},
        headers=client.participante_headers,
    )
    assert r.status_code == 403


def test_participante_so_ve_as_proprias_inscricoes(client):
    """listagem de inscricoes filtra por dono"""
    evento = _criar_evento(client)
    client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    )

    r = client.get("/api/v1/inscricoes", headers=client.participante_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["usuario_id"] == client.participante.id

    # admin vê a mesma inscricao
    r_admin = client.get("/api/v1/inscricoes", headers=client.admin_headers)
    assert r_admin.status_code == 200
    assert len(r_admin.json()) == 1
