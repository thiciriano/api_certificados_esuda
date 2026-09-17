from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import Configuracoes

configuracoes = Configuracoes()

# o connect_args ali embaixo é só pro sqlite não reclamar quando tem mais de uma thread usando o bancoo
if configuracoes.database_url.startswith("sqlite"):
    engine = create_engine(
        configuracoes.database_url,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(configuracoes.database_url)

SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def pegar_sessao():
    # abre uma sessao com o banco pra rota usar e fecha no final da requisicao
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()
