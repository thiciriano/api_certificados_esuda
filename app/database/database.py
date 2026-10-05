"""conexao com o banco"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# sqlite pq nao precisa instalar postgres
engine = create_engine(
    "sqlite:///./esuda_certificados.db",
    pool_pre_ping=True,
    echo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """abre a sessao e fecha no final"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

