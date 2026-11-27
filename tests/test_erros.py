"""testes do tratamento centralizado de erros e do contrato no OpenAPI."""

from fastapi.testclient import TestClient


def _envelope(r, status_code: int, codigo: str) -> dict:
    """valida o formato comum antes de devolver o corpo para assercoes especificas."""
    assert r.status_code == status_code
    corpo = r.json()
    assert corpo["success"] is False
    assert corpo["error"] == codigo
    assert isinstance(corpo["message"], str) and corpo["message"]
    assert "detail" in corpo
    return corpo


def test_erro_401_sem_token_segue_envelope_padrao(client: TestClient):
    corpo = _envelope(client.get("/api/v1/usuarios/me"), 401, "unauthorized")
    assert corpo["detail"] == "Not authenticated"


def test_erro_403_mantem_detalhe_e_envelope(client: TestClient):
    corpo = _envelope(
        client.get("/api/v1/usuarios", headers=client.participante_headers),
        403,
        "forbidden",
    )
    assert "permissão" in corpo["detail"]


def test_erro_422_de_validacao_tem_lista_de_detalhes(client: TestClient):
    corpo = _envelope(client.post("/api/v1/usuarios", json={"nome": "Sem dados"}), 422, "validation_error")
    assert isinstance(corpo["detail"], list)
    assert any(item["loc"][-1] == "email" for item in corpo["detail"])


def test_erro_404_de_rota_inexistente_e_padronizado(client: TestClient):
    corpo = _envelope(client.get("/api/v1/rota-que-nao-existe"), 404, "not_found")
    assert corpo["detail"] == "Not Found"


def test_openapi_documenta_erros_e_autenticacao(client: TestClient):
    spec = client.get("/openapi.json").json()

    propriedades = spec["components"]["schemas"]["RespostaErro"]["properties"]
    assert set(propriedades) >= {"success", "error", "message", "detail"}

    respostas = spec["paths"]["/api/v1/usuarios/me"]["get"]["responses"]
    for status_code in ("401", "403", "422", "500"):
        assert status_code in respostas
        schema = respostas[status_code]["content"]["application/json"]["schema"]
        assert schema["$ref"].endswith("RespostaErro")

    security = spec["components"]["securitySchemes"]
    assert "OAuth2PasswordBearer" in security
    descricao = security["OAuth2PasswordBearer"]["description"]
    assert "Authorize" in descricao and "senhaSegura123" in descricao

    # exemplos de login precisam estar no media type de formulario, senao nao aparecem no Swagger
    login = spec["paths"]["/api/v1/auth/login"]["post"]["requestBody"]["content"]
    exemplos = login["application/x-www-form-urlencoded"]["examples"]
    assert set(exemplos) >= {"organizador_demo", "participante_demo"}
    assert exemplos["organizador_demo"]["value"]["username"] == "victor@esuda.edu.br"
