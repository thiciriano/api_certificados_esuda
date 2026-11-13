"""testes de autenticação e JWT (mínimo 4)"""

from app.core.security import create_access_token, decode_access_token, hash_senha, verificar_senha


def test_login_com_credenciais_validas_retorna_token(client):
    """login certo devolve access_token e token_type bearer"""
    r = client.post(
        "/api/v1/auth/login",
        data={"username": client.participante.email, "password": "partSeguro123"},
    )
    assert r.status_code == 200
    corpo = r.json()
    assert "access_token" in corpo
    assert corpo["token_type"] == "bearer"
    # o token precisa ser funcional: dá pra usar numa rota protegida
    me = client.get("/api/v1/usuarios/me", headers={"Authorization": f"Bearer {corpo['access_token']}"})
    assert me.status_code == 200


def test_login_com_senha_incorreta_retorna_401(client):
    """senha errada nao autentica"""
    r = client.post(
        "/api/v1/auth/login",
        data={"username": client.participante.email, "password": "senhaErrada123"},
    )
    assert r.status_code == 401
    assert "access_token" not in r.json()


def test_login_com_email_inexistente_retorna_401(client):
    """email que nao existe no banco tambem nao autentica"""
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "naoexiste@esuda.edu.br", "password": "qualquer123"},
    )
    assert r.status_code == 401


def test_rota_protegida_sem_token_retorna_401(client):
    """sem Authorization header não passa"""
    r = client.get("/api/v1/usuarios/me")
    assert r.status_code == 401


def test_token_invalido_retorna_401(client):
    """token forjado/lixo nao passa"""
    r = client.get(
        "/api/v1/usuarios/me",
        headers={"Authorization": "Bearer esse.token.e.um.lixo"},
    )
    assert r.status_code == 401


def test_token_expirado_retorna_401(client, token_expirado_headers):
    """token vencido nao passa (mesmo com assinatura certa)"""
    r = client.get("/api/v1/usuarios/me", headers=token_expirado_headers)
    assert r.status_code == 401


def test_resposta_do_login_e_me_nunca_expoem_senha(client):
    """nenhuma resposta da api pode devolver senha ou hash"""
    r = client.post(
        "/api/v1/auth/login",
        data={"username": client.admin.email, "password": "adminSeguro123"},
    )
    assert r.status_code == 200
    assert "senha" not in r.json()

    me = client.get("/api/v1/usuarios/me", headers=client.admin_headers)
    assert me.status_code == 200
    assert "senha" not in me.text
    assert hash_senha("adminSeguro123") not in me.text  # nem o hash


def test_hash_da_senha_nao_é_texto_puro():
    """bcrypt guarda hash, e o verificar_senha confere sem guardar a pura"""
    hash_guardado = hash_senha("minhaSenha123")
    assert hash_guardado != "minhaSenha123"
    assert verificar_senha("minhaSenha123", hash_guardado) is True
    assert verificar_senha("outraSenha", hash_guardado) is False


def test_decode_de_token_assinado_com_outra_chave_retorna_none():
    """token assinado com chave que nao é a do servidor nao decodifica"""
    token = create_access_token(data={"sub": "1"})
    # troca a chave do settings na hora do decode (simula servidor com outra chave)
    from app.core import security
    chave_original = security.settings.JWT_SECRET_KEY
    try:
        security.settings.JWT_SECRET_KEY = "outra-chave-bem-diferente"
        assert decode_access_token(token) is None
    finally:
        security.settings.JWT_SECRET_KEY = chave_original
