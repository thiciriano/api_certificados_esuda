"""schemas do pydantic (validacao dos dados)"""
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr


# USUARIOS
class UsuarioBase(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="E-mail único do usuário")
    papel: str = Field(..., description="Papel do usuário: 'participante' ou 'organizador'")


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, description="Senha do usuário")


class UsuarioIn(UsuarioBase):
    senha: str

    class Config:
        from_attributes = True


class UsuarioOut(UsuarioIn):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# CATEGORIAS
class CategoriaBase(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, description="Descrição da categoria")


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaOut(CategoriaCreate):
    id: int

    class Config:
        from_attributes = True


# EVENTOS
class EventoBase(BaseModel):
    titulo: str = Field(..., max_length=200, description="Título do evento")
    descricao: Optional[str] = Field(None, description="Descrição do evento")
    data_evento: datetime = Field(..., description="Data e hora do evento")
    local: Optional[str] = Field(None, max_length=255, description="Local do evento")
    capacidade: int = Field(..., gt=0, description="Capacidade máxima de vagas")
    categoria_id: int = Field(..., description="ID da categoria")


class EventoCreate(EventoBase):
    pass


class EventoOut(EventoCreate):
    id: int
    vagas_disponiveis: int
    status: str
    categoria: Optional[CategoriaOut] = None

    class Config:
        from_attributes = True


class EventoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=200)
    descricao: Optional[str] = Field(None)
    data_evento: Optional[datetime] = Field(None)
    local: Optional[str] = Field(None, max_length=255)
    capacidade: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None)


# INSCRICOES
class InscriçãoBase(BaseModel):
    usuario_id: int = Field(..., description="ID do usuário")
    evento_id: int = Field(..., description="ID do evento")


class InscriçãoCreate(InscriçãoBase):
    pass


class InscriçãoOut(InscriçãoCreate):
    id: int
    status: str
    data_inscricao: Optional[datetime] = None
    usuario: Optional[UsuarioOut] = None
    evento: Optional[EventoOut] = None

    class Config:
        from_attributes = True


# CERTIFICADOS
class CertificadoBase(BaseModel):
    inscricao_id: int = Field(..., description="ID da inscrição")
    usuario_id: int = Field(..., description="ID do usuário")


class CertificadoCreate(CertificadoBase):
    pass


class CertificadoOut(CertificadoCreate):
    id: int
    codigo_certificacao: Optional[str] = None
    data_emissao: Optional[datetime] = None
    status: str
    usuario: Optional[UsuarioOut] = None
    inscricao: Optional[InscriçãoOut] = None

    class Config:
        from_attributes = True


# RESPOSTAS PADRAO
class RespostaSucesso(BaseModel):
    success: bool = True
    message: str
    data: Optional[object] = None


class RespostaErro(BaseModel):
    success: bool = False
    error: str
    message: str
