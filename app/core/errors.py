"""tratamento centralizado de erros da API.

Todas as respostas de erro seguem o mesmo envelope:
    {success: false, error: <codigo>, message: <texto>, detail: <detalhe>}

O campo ``detail`` e mantido para compatibilidade com os clientes existentes.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.schemas.schemas import RespostaErro

logger = logging.getLogger(__name__)

# documentado no OpenAPI para todas as rotas da API v1
RESPOSTAS_ERRO = {
    status: {"model": RespostaErro, "description": descricao}
    for status, descricao in {
        400: "Regra de negócio ou requisição inválida",
        401: "Token ausente, inválido ou expirado",
        403: "Usuário autenticado sem permissão",
        404: "Recurso não encontrado",
        422: "Erro de validação dos dados enviados",
        500: "Erro interno do servidor",
    }.items()
}

MENSAGEM_POR_STATUS = {
    400: "Requisição inválida",
    401: "Não autenticado",
    403: "Sem permissão para esta operação",
    404: "Recurso não encontrado",
    422: "Dados inválidos",
    500: "Erro interno do servidor",
}

CODIGO_POR_STATUS = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    422: "validation_error",
    500: "internal_error",
}


def corpo_erro(status_code: int, detail) -> dict:
    """monta o envelope padrao sem perder o detail usado pelos clientes."""
    return {
        "success": False,
        "error": CODIGO_POR_STATUS.get(status_code, "http_error"),
        "message": MENSAGEM_POR_STATUS.get(status_code, "Erro"),
        "detail": detail,
    }


def registrar_handlers(app: FastAPI) -> None:
    """registra os handlers de erro no app (chamado uma unica vez no main)."""

    @app.exception_handler(StarletteHTTPException)
    async def handler_http(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=corpo_erro(exc.status_code, exc.detail),
            headers=dict(exc.headers or {}),
        )

    @app.exception_handler(RequestValidationError)
    async def handler_validacao(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=corpo_erro(422, jsonable_encoder(exc.errors())),
        )

    @app.exception_handler(Exception)
    async def handler_inesperado(request: Request, exc: Exception):
        logger.exception("Erro não tratado em %s", request.url.path)
        return JSONResponse(status_code=500, content=corpo_erro(500, "Erro interno do servidor"))
