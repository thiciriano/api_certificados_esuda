from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.conexao import Base


class Inscricao(Base):
    __tablename__ = "inscricoes"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    data_inscricao = Column(DateTime, default=datetime.now)
    status = Column(String(20), nullable=False, default="ativa")  # ativa ou cancelada

    usuario = relationship("Usuario", back_populates="inscricoes")
    evento = relationship("Evento", back_populates="inscricoes")
    certificado = relationship("Certificado", back_populates="inscricao", uselist=False)
