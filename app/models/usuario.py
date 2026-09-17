from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database.conexao import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)  # email nao pode repetir
    senha = Column(String(255), nullable=False)
    papel = Column(String(20), nullable=False, default="participante")  # admin, organizador ou participante
    data_cadastro = Column(DateTime, default=datetime.now)

    inscricoes = relationship("Inscricao", back_populates="usuario")
