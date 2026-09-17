from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UsuarioBase(BaseModel):
    nome: str
    email: EmailStr
    papel: str = "participante"  # admin, organizador ou participante


class UsuarioCriar(UsuarioBase):
    senha: str


class UsuarioAtualizar(BaseModel):
    nome: str | None = None
    senha: str | None = None
    papel: str | None = None


class UsuarioResposta(UsuarioBase):
    id: int
    data_cadastro: datetime

    # from_attributes pra montar a resposta direto do objeto que vem do banco
    model_config = ConfigDict(from_attributes=True)

    # reparo que a senha não tem aqui em cima de propósito, ela nunca pode voltar na resposta
