from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.conexao import Base


class Evento(Base):
    __tablename__ = "eventos"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(150), nullable=False)
    descricao = Column(Text, nullable=True)
    data_evento = Column(Date, nullable=False)  # nao pode ser data passada (a validacao fica no schema)
    local = Column(String(150), nullable=False)
    capacidade = Column(Integer, nullable=False)  # tem que ser maior que zero
    status = Column(String(20), nullable=False, default="ativo")  # ativo ou cancelado
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)  # evento pode ficar sem categoria
    data_cadastro = Column(DateTime, default=datetime.now)

    categoria = relationship("Categoria", back_populates="eventos")
    inscricoes = relationship("Inscricao", back_populates="evento")
