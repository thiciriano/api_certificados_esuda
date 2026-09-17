from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InscricaoCriar(BaseModel):
    usuario_id: int
    evento_id: int


class InscricaoResposta(BaseModel):
    id: int
    usuario_id: int
    evento_id: int
    data_inscricao: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)
