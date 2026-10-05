"""tabelas do banco"""
from sqlalchemy import Column, Integer, String, Date, Boolean, Text, ForeignKey, Time
from sqlalchemy.orm import relationship
from app.database.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    senha = Column(String(255), nullable=False)
    papel = Column(String(50), nullable=False)  # 'participante' ou 'organizador'
    is_active = Column(Boolean, default=True)
    created_at = Column(Date, nullable=True)

    inscricoes = relationship("Inscrição", back_populates="usuario")
    certificados = relationship("Certificado", back_populates="usuario")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True)
    descricao = Column(Text, nullable=True)

    eventos = relationship("Evento", back_populates="categoria")


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(Text, nullable=True)
    data_evento = Column(String(20), nullable=False)
    local = Column(String(255), nullable=True)
    capacidade = Column(Integer, nullable=False, default=50)
    vagas_disponiveis = Column(Integer, nullable=False, default=50)
    status = Column(String(50), default="ativo")  # 'ativo', 'cancelado', 'finalizado'
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    criado_por = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    categoria = relationship("Categoria", back_populates="eventos")
    inscricoes = relationship("Inscrição", back_populates="evento")


class Inscrição(Base):
    __tablename__ = "inscricoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    status = Column(String(50), default="ativa")  # 'ativa', 'cancelada'
    data_inscricao = Column(Date, nullable=True)

    usuario = relationship("Usuario", back_populates="inscricoes")
    evento = relationship("Evento", back_populates="inscricoes")
    certificado = relationship("Certificado", back_populates="inscricao")


class Certificado(Base):
    __tablename__ = "certificados"

    id = Column(Integer, primary_key=True, index=True)
    inscricao_id = Column(Integer, ForeignKey("inscricoes.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    codigo_certificacao = Column(String(100), unique=True, nullable=True)
    data_emissao = Column(Date, nullable=True)
    status = Column(String(50), default="pendente")  # 'pendente', 'emitido', 'cancelado'
    url_arquivo = Column(String(500), nullable=True)  # caminho do pdf

    usuario = relationship("Usuario", back_populates="certificados")
    inscricao = relationship("Inscrição", back_populates="certificado")

# regras de negocio que a api precisa seguir
# R1: Um usuário não pode se inscrever duas vezes no mesmo evento
# R2: Um evento não pode ultrapassar a capacidade máxima
# R3: Apenas administradores podem excluir eventos
# R4: Um participante só pode cancelar a própria inscrição
# R5: Não é permitido cadastrar evento com data passada
# R6: Um certificado só pode ser emitido para participante inscrito
# R7: E-mail deve ser único e válido
# R8: Senha deve ter no mínimo 6 caracteres
# R9: Título do evento é obrigatório e deve ser único
# R10: Certificado só pode ser emitido após inscrição ativa
