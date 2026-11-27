"""escopo de recursos por perfil/dono.

Antes essas consultas viviam repetidas dentro dos routers de inscricoes e
certificados. Aqui fica a regra de "o que cada usuario pode ver/alterar".
"""

from sqlalchemy.orm import Session

from app.core.permissions import eh_dono_ou_admin
from app.models.models import Certificado, Evento, Inscrição, Usuario


def ids_eventos_criados(db: Session, usuario: Usuario) -> list[int]:
    """ids dos eventos em que o usuario e o responsavel (criado_por)."""
    return [e.id for e in db.query(Evento).filter(Evento.criado_por == usuario.id).all()]


def ids_inscricoes_em_eventos(db: Session, eventos_ids: list[int]) -> list[int]:
    """ids das inscricoes vinculadas aos eventos informados."""
    if not eventos_ids:
        return []
    return [
        i.id
        for i in db.query(Inscrição).filter(Inscrição.evento_id.in_(eventos_ids)).all()
    ]


def evento_e_do_usuario(db: Session, usuario: Usuario, evento_id: int) -> bool:
    """organizador so altera inscricoes dos proprios eventos; admin pode tudo."""
    if usuario.papel == "admin":
        return True
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    return evento is not None and evento.criado_por == usuario.id


def inscricoes_visiveis(db: Session, usuario: Usuario) -> list[Inscrição]:
    """admin ve todas, organizador as dos seus eventos, participante as suas."""
    if usuario.papel == "admin":
        return db.query(Inscrição).all()
    if usuario.papel == "organizador":
        return db.query(Inscrição).filter(
            Inscrição.evento_id.in_(ids_eventos_criados(db, usuario))
        ).all()
    return db.query(Inscrição).filter(Inscrição.usuario_id == usuario.id).all()


def certificados_visiveis(db: Session, usuario: Usuario) -> list[Certificado]:
    """admin ve todos, organizador os dos seus eventos, participante os seus."""
    if usuario.papel == "admin":
        return db.query(Certificado).all()
    if usuario.papel == "organizador":
        inscricoes_ids = ids_inscricoes_em_eventos(db, ids_eventos_criados(db, usuario))
        return db.query(Certificado).filter(
            Certificado.inscricao_id.in_(inscricoes_ids)
        ).all()
    return db.query(Certificado).filter(Certificado.usuario_id == usuario.id).all()


def pode_alterar_inscricao(db: Session, usuario: Usuario, inscricao: Inscrição) -> bool:
    """dono da inscricao, dono do evento ou admin (conforme o papel)."""
    if usuario.papel == "organizador":
        return evento_e_do_usuario(db, usuario, inscricao.evento_id)
    return eh_dono_ou_admin(usuario, inscricao.usuario_id)
