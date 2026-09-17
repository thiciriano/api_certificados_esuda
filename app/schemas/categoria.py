from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CategoriaBase(BaseModel):
    nome: str
    descricao: str | None = None


class CategoriaCriar(CategoriaBase):
    pass


class CategoriaAtualizar(BaseModel):
    nome: str | None = None
    descricao: str | None = None


class CategoriaResposta(CategoriaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
