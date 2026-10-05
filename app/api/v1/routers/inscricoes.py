"""rotas de inscricoes"""

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import Inscrição, Evento, Usuario, Certificado


router = APIRouter(prefix="/inscricoes", tags=["Inscrições"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Inscrever-se em evento",
    description="Realiza inscrição de um usuário em um evento",
)
async def inscrever(
    inscricao: dict = Body(
        ...,
        openapi_examples={
            "Padrao": {
                "summary": "Inscrição de teste",
                "description": "Inscreve usuário em evento",
                "value": {"usuario_id": 1, "evento_id": 1},
            }
        },
    ),
    db: Session = Depends(get_db),
):
    user = db.query(Usuario).filter(Usuario.id == inscricao.get("usuario_id")).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    evento = db.query(Evento).filter(Evento.id == inscricao.get("evento_id")).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # mesma pessoa nao pode se inscrever 2x no mesmo evento
    ja_inscrito = db.query(Inscrição).filter(
        Inscrição.usuario_id == inscricao["usuario_id"],
        Inscrição.evento_id == inscricao["evento_id"],
    ).first()
    if ja_inscrito:
        raise HTTPException(status_code=400, detail="Usuário já inscrito neste evento")

    if evento.capacidade <= 0:
        raise HTTPException(status_code=400, detail="Não há vagas disponíveis")

    nova = Inscrição(usuario_id=inscricao["usuario_id"], evento_id=inscricao["evento_id"], status="ativa")
    db.add(nova)
    evento.capacidade -= 1  # tira uma vaga
    db.commit()
    db.refresh(nova)
    return {"success": True, "message": "Inscrição realizada", "data": {"id": nova.id}}


@router.get(
    "",
    summary="Listar inscrições",
    description="Lista todas as inscrições do sistema",
)
async def listar_inscricoes(db: Session = Depends(get_db)):
    inscricoes = db.query(Inscrição).all()
    return [
        {"id": i.id, "usuario_id": i.usuario_id, "evento_id": i.evento_id, "status": i.status}
        for i in inscricoes
    ]


@router.put(
    "/{inscricao_id}",
    summary="Atualizar inscrição",
    description="Atualiza status da inscrição (cancelar/ativar)",
)
async def atualizar_inscricao(
    inscricao_id: int,
    dados: dict = Body(
        ...,
        openapi_examples={
            "Cancelar": {
                "summary": "Cancelar inscrição",
                "description": "Cancela a inscrição e libera vaga",
                "value": {"status": "cancelada"},
            }
        },
    ),
    db: Session = Depends(get_db),
) -> dict:
    db_insc = db.query(Inscrição).filter(Inscrição.id == inscricao_id).first()
    if not db_insc:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    if "status" in dados:
        db_insc.status = dados["status"]
        # cancelar devolve a vaga pro evento
        if dados["status"] == "cancelada":
            ev = db.query(Evento).filter(Evento.id == db_insc.evento_id).first()
            if ev:
                ev.capacidade += 1
                db.commit()
        else:
            db.commit()

    return {"success": True, "message": "Inscrição atualizada", "data": {"id": db_insc.id, "status": db_insc.status}}


@router.delete(
    "/{inscricao_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar inscrição",
    description="Remove inscrição do evento",
)
async def deletar_inscricao(inscricao_id: int, db: Session = Depends(get_db)) -> None:
    db_insc = db.query(Inscrição).filter(Inscrição.id == inscricao_id).first()
    if db_insc:
        # tem que apagar o certificado antes, o inscricao_id dele nao pode ficar vazio
        db.query(Certificado).filter(Certificado.inscricao_id == inscricao_id).delete()
        ev = db.query(Evento).filter(Evento.id == db_insc.evento_id).first()
        if ev:
            ev.capacidade += 1  # devolve a vaga
        db.delete(db_insc)
        db.commit()
