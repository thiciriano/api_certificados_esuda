from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.conexao import Base


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(80), unique=True, nullable=False)
    descricao = Column(Text, nullable=True)

    eventos = relationship("Evento", back_populates="categoria")
