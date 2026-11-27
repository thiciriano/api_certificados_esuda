"""verificacoes de unicidade compartilhadas pelas rotas.

Centraliza as queries que antes eram copiadas em usuarios, eventos e categorias.
As mensagens/status continuam iguais para nao quebrar os clientes.
"""

from sqlalchemy.orm import Session

from app.models.models import Categoria, Evento, Usuario


def email_ja_cadastrado(db: Session, email: str, usuario_id: int | None = None) -> bool:
    """e-mail em uso por outro usuario (ignora o proprio id no update)."""
    query = db.query(Usuario).filter(Usuario.email == email)
    if usuario_id is not None:
        query = query.filter(Usuario.id != usuario_id)
    return query.first() is not None


def titulo_evento_ja_usado(db: Session, titulo: str, evento_id: int | None = None) -> bool:
    """titulo de evento repetido (ignora o proprio id no update)."""
    query = db.query(Evento).filter(Evento.titulo == titulo)
    if evento_id is not None:
        query = query.filter(Evento.id != evento_id)
    return query.first() is not None


def categoria_ja_existe(db: Session, nome: str, categoria_id: int | None = None) -> bool:
    """nome de categoria repetido (ignora o proprio id no update)."""
    query = db.query(Categoria).filter(Categoria.nome == nome)
    if categoria_id is not None:
        query = query.filter(Categoria.id != categoria_id)
    return query.first() is not None
