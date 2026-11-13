"""conexao com o banco"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# sqlite local por padrao (nao precisa instalar nada); postgres no producao via DATABASE_URL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # testa a conexao antes de usar (cai bem no render)
    echo=settings.DB_ECHO,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
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
