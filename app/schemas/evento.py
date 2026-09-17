from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, field_validator


class EventoBase(BaseModel):
    titulo: str
    descricao: str | None = None
    data_evento: date
    local: str
    capacidade: int
    categoria_id: int | None = None


class EventoCriar(EventoBase):
    @field_validator("capacidade")
    @classmethod
    def validar_capacidade(cls, valor):
        # regra de negocio: capacidade tem que ser maior que zero
        if valor <= 0:
            raise ValueError("a capacidade tem que ser maior que zero")
        return valor

    @field_validator("data_evento")
    @classmethod
    def validar_data_evento(cls, valor):
        # regra de negocio: nao pode cadastrar evento com data no passado
        if valor < date.today():
            raise ValueError("não pode cadastrar evento com data no passado")
        return valor


class EventoAtualizar(BaseModel):
    titulo: str | None = None
    descricao: str | None = None
    data_evento: date | None = None
    local: str | None = None
    capacidade: int | None = None
    categoria_id: int | None = None
    status: str | None = None

    @field_validator("capacidade")
    @classmethod
    def validar_capacidade(cls, valor):
        if valor is not None and valor <= 0:
            raise ValueError("a capacidade tem que ser maior que zero")
        return valor

    @field_validator("data_evento")
    @classmethod
    def validar_data_evento(cls, valor):
        if valor is not None and valor < date.today():
            raise ValueError("não pode cadastrar evento com data no passado")
        return valor


class EventoResposta(EventoBase):
    id: int
    status: str
    data_cadastro: datetime

    model_config = ConfigDict(from_attributes=True)
