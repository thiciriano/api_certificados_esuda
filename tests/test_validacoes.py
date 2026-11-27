"""testes de validação de entrada e tratamento de erros (mínimo 2)"""


def test_criar_usuario_sem_campos_obrigatorios_retorna_422(client):
    """body vazio ou incompleto nao passa pela validacao do schema"""
    r = client.post("/api/v1/usuarios", json={})
    assert r.status_code == 422

    r = client.post("/api/v1/usuarios", json={"nome": "Sem Email", "senha": "123456", "papel": "participante"})
    assert r.status_code == 422


def test_senha_curta_retorna_422(client):
    """R8: senha minimo de 6 caracteres barrada pelo schema"""
    r = client.post(
        "/api/v1/usuarios",
        json={"nome": "Senha Curta", "email": "curta@esuda.edu.br", "senha": "123", "papel": "participante"},
    )
    assert r.status_code == 422


def test_email_invalido_retorna_422(client):
    """email malformado nao passa"""
    r = client.post(
        "/api/v1/usuarios",
        json={"nome": "Email Ruim", "email": "nao-e-email", "senha": "senhaSegura123", "papel": "participante"},
    )
    assert r.status_code == 422


def test_papel_invalido_retorna_422(client):
    """papel fora da lista de perfis nao passa"""
    r = client.post(
        "/api/v1/usuarios",
        json={"nome": "Papel Ruim", "email": "papel@esuda.edu.br", "senha": "senhaSegura123", "papel": "superuser"},
    )
    assert r.status_code == 422


def test_criar_evento_com_capacidade_zero_retorna_422(client):
    """capacidade precisa ser maior que zero"""
    r = client.post(
        "/api/v1/eventos",
        json={
            "titulo": "Evento Zero",
            "data_evento": "2027-11-20",
            "capacidade": 0,
            "categoria_id": 1,
        },
        headers=client.organizador_headers,
    )
    assert r.status_code == 422


def test_categoria_inexistente_retorna_404(client):
    """criar evento apontando pra categoria que nao existe"""
    r = client.post(
        "/api/v1/eventos",
        json={
            "titulo": "Evento Sem Categoria",
            "data_evento": "2027-11-20",
            "capacidade": 10,
            "categoria_id": 9999,
        },
        headers=client.organizador_headers,
    )
    assert r.status_code == 404


def test_inscricao_em_evento_inexistente_retorna_404(client):
    """inscricao em evento que nao existe"""
    r = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": 9999},
        headers=client.participante_headers,
    )
    assert r.status_code == 404


def test_atualizar_recurso_inexistente_retorna_404(client):
    """PUT em id que nao existe em qualquer entidade"""
    r = client.put(
        "/api/v1/usuarios/9999",
        json={"nome": "Fantasma"},
        headers=client.admin_headers,
    )
    assert r.status_code == 404

    r = client.put(
        "/api/v1/eventos/9999",
        json={"titulo": "Fantasma"},
        headers=client.admin_headers,
    )
    assert r.status_code == 404

    r = client.put(
        "/api/v1/certificados/9999",
        json={"status": "emitido"},
        headers=client.admin_headers,
    )
    assert r.status_code == 404


def test_deletar_recurso_inexistente_retorna_404(client):
    """DELETE em id que nao existe"""
    r = client.delete("/api/v1/eventos/9999", headers=client.admin_headers)
    assert r.status_code == 404

    r = client.delete("/api/v1/inscricoes/9999", headers=client.admin_headers)
    assert r.status_code == 404


def test_status_de_inscricao_invalido_retorna_422(client):
    """status fora de {ativa, cancelada} nao passa"""
    evento_r = client.post(
        "/api/v1/categorias",
        json={"nome": "Cat Status", "descricao": "x"},
        headers=client.admin_headers,
    )
    evento = client.post(
        "/api/v1/eventos",
        json={
            "titulo": "Evento Status",
            "data_evento": "2027-11-20",
            "capacidade": 10,
            "categoria_id": evento_r.json()["data"]["id"],
        },
        headers=client.organizador_headers,
    ).json()
    inscricao = client.post(
        "/api/v1/inscricoes",
        json={"evento_id": evento["data"]["id"]},
        headers=client.participante_headers,
    ).json()

    r = client.put(
        f"/api/v1/inscricoes/{inscricao['data']['id']}",
        json={"status": "qualquercoisa"},
        headers=client.participante_headers,
    )
    assert r.status_code == 422
