from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CertificadoCriar(BaseModel):
    inscricao_id: int


class CertificadoResposta(BaseModel):
    id: int
    inscricao_id: int
    codigo: str
    data_emissao: datetime

    model_config = ConfigDict(from_attributes=True)
