from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.conexao import Base


class Certificado(Base):
    __tablename__ = "certificados"

    id = Column(Integer, primary_key=True, index=True)
    inscricao_id = Column(Integer, ForeignKey("inscricoes.id"), unique=True, nullable=False)  # 1 inscricao = 1 certificado
    codigo = Column(String(20), unique=True, nullable=False)  # codigo aleatorio que vai aparecer no certificado
    data_emissao = Column(DateTime, default=datetime.now)

    inscricao = relationship("Inscricao", back_populates="certificado")
