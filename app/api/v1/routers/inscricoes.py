"""rotas de inscricoes"""

from datetime import date

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, precisa_de_permissao
from app.core.permissions import eh_dono_ou_admin
from app.core.swagger_presets import EXEMPLO_INSCRICAO, EXEMPLO_INSCRICAO_STATUS
from app.database.database import get_db
from app.models.models import Certificado, Evento, Inscrição, Usuario
from app.schemas.schemas import (
    InscriçãoCreate,
    InscriçãoOut,
    InscriçãoStatusUpdate,
    RespostaInscrição,
)


router = APIRouter(prefix="/inscricoes", tags=["Inscrições"])


def _evento_do_organizador(db: Session, usuario: Usuario, evento_id: int) -> bool:
    """confere se o evento pertence a algum evento criado pelo organizador"""
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    return evento is not None and evento.criado_por == usuario.id


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=RespostaInscrição,
    summary="Inscrever-se em evento",
    description=(
        "Realiza a inscrição do próprio usuário autenticado no evento. "
        "Somente participantes podem se inscrever."
    ),
)
async def inscrever(
    inscricao: InscriçãoCreate = Body(..., openapi_examples=EXEMPLO_INSCRICAO),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> RespostaInscrição:
    if current_user.papel != "participante":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Somente participantes podem se inscrever em eventos",
        )

    evento = db.query(Evento).filter(Evento.id == inscricao.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    if evento.status != "ativo":
        raise HTTPException(status_code=400, detail="Evento não está ativo")

    # mesma pessoa nao pode se inscrever 2x no mesmo evento (R4)
    ja_inscrito = (
        db.query(Inscrição)
        .filter(
            Inscrição.usuario_id == current_user.id,
            Inscrição.evento_id == inscricao.evento_id,
        )
        .first()
    )
    if ja_inscrito:
        raise HTTPException(status_code=400, detail="Usuário já inscrito neste evento")

    # so inscreve se tiver vaga (R6)
    if evento.vagas_disponiveis <= 0:
        raise HTTPException(status_code=400, detail="Não há vagas disponíveis")

    nova = Inscrição(
        usuario_id=current_user.id,  # sempre ele mesmo, vem do token
        evento_id=inscricao.evento_id,
        status="ativa",
        data_inscricao=date.today(),
    )
    db.add(nova)
    evento.vagas_disponiveis -= 1  # tira uma vaga
    db.commit()
    db.refresh(nova)
    return RespostaInscrição(message="Inscrição realizada", data=nova)


@router.get(
    "",
    response_model=list[InscriçãoOut],
    summary="Listar inscrições",
    description=(
        "Participante vê as próprias inscrições, organizador vê as inscrições dos "
        "eventos que criou e administrador vê todas."
    ),
)
async def listar_inscricoes(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> list[InscriçãoOut]:
    if current_user.papel == "admin":
        return db.query(Inscrição).all()

    if current_user.papel == "organizador":
        eventos_ids = [
            e.id for e in db.query(Evento).filter(Evento.criado_por == current_user.id).all()
        ]
        return db.query(Inscrição).filter(Inscrição.evento_id.in_(eventos_ids)).all()

    return db.query(Inscrição).filter(Inscrição.usuario_id == current_user.id).all()


@router.put(
    "/{inscricao_id}",
    response_model=RespostaInscrição,
    summary="Atualizar inscrição",
    description=(
        "Cancela ou reativa uma inscrição. Participante só mexe na própria; "
        "organizador nas dos eventos que criou; administrador em qualquer uma. "
        "Cancelar devolve a vaga pro evento."
    ),
)
async def atualizar_inscricao(
    inscricao_id: int,
    dados: InscriçãoStatusUpdate = Body(..., openapi_examples=EXEMPLO_INSCRICAO_STATUS),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> RespostaInscrição:
    db_insc = db.query(Inscrição).filter(Inscrição.id == inscricao_id).first()
    if not db_insc:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    # nao da pra mexer na inscricao de outra pessoa (alterar a URL nao adianta)
    if current_user.papel == "organizador":
        if not _evento_do_organizador(db, current_user, db_insc.evento_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você só pode alterar inscrições de eventos que você criou",
            )
    elif not eh_dono_ou_admin(current_user, db_insc.usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode alterar a própria inscrição",
        )

    ev = db.query(Evento).filter(Evento.id == db_insc.evento_id).first()

    if dados.status == "cancelada" and db_insc.status == "ativa":
        db_insc.status = "cancelada"
        if ev:
            ev.vagas_disponiveis += 1  # cancelar devolve a vaga pro evento
    elif dados.status == "ativa" and db_insc.status == "cancelada":
        if ev and ev.vagas_disponiveis <= 0:
            raise HTTPException(status_code=400, detail="Não há vagas disponíveis")
        db_insc.status = "ativa"
        if ev:
            ev.vagas_disponiveis -= 1  # reativar tira a vaga de volta
    # se o status pedido for o mesmo, nao faz nada (evita vaga duplicada)

    db.commit()
    db.refresh(db_insc)
    return RespostaInscrição(message="Inscrição atualizada", data=db_insc)


@router.delete(
    "/{inscricao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar inscrição",
    description="Remove inscrição do evento. Somente administradores. Devolve a vaga.",
)
async def deletar_inscricao(
    inscricao_id: int,
    _: Usuario = Depends(precisa_de_permissao("pode_excluir_inscricao")),
    db: Session = Depends(get_db),
) -> None:
    db_insc = db.query(Inscrição).filter(Inscrição.id == inscricao_id).first()
    if not db_insc:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    # tem que apagar o certificado antes, o inscricao_id dele nao pode ficar vazio
    db.query(Certificado).filter(Certificado.inscricao_id == inscricao_id).delete()
    ev = db.query(Evento).filter(Evento.id == db_insc.evento_id).first()
    if ev and db_insc.status == "ativa":
        ev.vagas_disponiveis += 1  # devolve a vaga
    db.delete(db_insc)
    db.commit()
