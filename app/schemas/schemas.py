"""schemas do pydantic (validacao dos dados)"""
from typing import Literal, Optional
from datetime import date
from pydantic import BaseModel, ConfigDict, Field, EmailStr

# USUARIOS
class UsuarioBase(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome completo do usuário")
    email: EmailStr = Field(..., description="E-mail único do usuário")
    papel: Literal["participante", "organizador", "admin"] = Field(
        ..., description="Papel do usuário: 'participante', 'organizador' ou 'admin'"
    )

class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, max_length=128, description="Senha do usuário (mínimo 6 caracteres)")

class UsuarioUpdate(BaseModel):
    """o que dá pra mudar no cadastro (papel so muda admin)"""
    nome: Optional[str] = Field(None, max_length=100, description="Nome completo do usuário")
    email: Optional[EmailStr] = Field(None, description="E-mail único do usuário")
    senha: Optional[str] = Field(None, min_length=6, max_length=128, description="Nova senha")
    papel: Optional[Literal["participante", "organizador", "admin"]] = Field(
        None, description="Papel do usuário (só administradores podem alterar)"
    )

class UsuarioOut(BaseModel):
    """nenhuma resposta da api pode devolver a senha nem o hash"""
    id: int
    nome: str
    email: EmailStr
    papel: str
    is_active: bool
    created_at: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)

# AUTENTICACAO
class RespostaToken(BaseModel):
    """resposta do login"""
    access_token: str = Field(..., description="Token JWT gerado")
    token_type: str = Field("bearer", description="Tipo do token (sempre bearer)")

# CATEGORIAS
class CategoriaBase(BaseModel):
    nome: str = Field(..., max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, description="Descrição da categoria")

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=100, description="Nome da categoria")
    descricao: Optional[str] = Field(None, description="Descrição da categoria")

class CategoriaOut(CategoriaCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)

# EVENTOS
class EventoBase(BaseModel):
    titulo: str = Field(..., max_length=200, description="Título do evento")
    descricao: Optional[str] = Field(None, description="Descrição do evento")
    data_evento: date = Field(..., description="Data do evento (precisa ser futura)")
    local: Optional[str] = Field(None, max_length=255, description="Local do evento")
    capacidade: int = Field(..., gt=0, description="Capacidade máxima de vagas")
    categoria_id: int = Field(..., description="ID da categoria")

class EventoCreate(EventoBase):
    pass

class EventoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, max_length=200, description="Título do evento")
    descricao: Optional[str] = Field(None, description="Descrição do evento")
    data_evento: Optional[date] = Field(None, description="Data do evento")
    local: Optional[str] = Field(None, max_length=255, description="Local do evento")
    capacidade: Optional[int] = Field(None, gt=0, description="Capacidade máxima de vagas")
    status: Optional[Literal["ativo", "cancelado", "finalizado"]] = Field(
        None, description="Status do evento"
    )

class EventoOut(EventoBase):
    id: int
    vagas_disponiveis: int
    status: str
    categoria: Optional[CategoriaOut] = None

    model_config = ConfigDict(from_attributes=True)

# INSCRICOES
class InscriçãoCreate(BaseModel):
    """so o evento_id, o usuario vem do token (ninguem inscreve outra pessoa)"""
    evento_id: int = Field(..., description="ID do evento")

class InscriçãoStatusUpdate(BaseModel):
    status: Literal["ativa", "cancelada"] = Field(..., description="Novo status da inscrição")

class InscriçãoOut(BaseModel):
    id: int
    usuario_id: int
    evento_id: int
    status: str
    data_inscricao: Optional[date] = None
    usuario: Optional[UsuarioOut] = None
    evento: Optional[EventoOut] = None

    model_config = ConfigDict(from_attributes=True)

# CERTIFICADOS
class CertificadoCreate(BaseModel):
    inscricao_id: int = Field(..., description="ID da inscrição ativa do certificado")

class CertificadoOut(BaseModel):
    id: int
    inscricao_id: int
    usuario_id: int
    codigo_certificacao: Optional[str] = None
    data_emissao: Optional[date] = None
    status: str

    model_config = ConfigDict(from_attributes=True)

class CertificadoStatusUpdate(BaseModel):
    status: Literal["pendente", "emitido", "cancelado"] = Field(
        ..., description="Novo status do certificado"
    )

# RESPOSTAS PADRAO
class RespostaSucesso(BaseModel):
    success: bool = True
    message: str
    data: Optional[object] = None

class RespostaErro(BaseModel):
    success: bool = False
    error: str
    message: str

# envelopes tipados (o data mostra o schema certo no swagger)
class RespostaUsuario(RespostaSucesso):
    data: Optional[UsuarioOut] = None

class RespostaCategoria(RespostaSucesso):
    data: Optional[CategoriaOut] = None

class RespostaEvento(RespostaSucesso):
    data: Optional[EventoOut] = None

class RespostaInscrição(RespostaSucesso):
    data: Optional[InscriçãoOut] = None

class RespostaCertificado(RespostaSucesso):
    data: Optional[CertificadoOut] = None
