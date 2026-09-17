from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.conexao import pegar_sessao
from app.models.evento import Evento
from app.models.inscricao import Inscricao
from app.models.usuario import Usuario
from app.schemas.inscricao import InscricaoCriar, InscricaoResposta

router = APIRouter(prefix="/inscricoes", tags=["Inscrições"])


@router.post("", response_model=InscricaoResposta, status_code=status.HTTP_201_CREATED)
def criar_inscricao(dados: InscricaoCriar, db: Session = Depends(pegar_sessao)):
    usuario = db.query(Usuario).filter(Usuario.id == dados.usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    evento = db.query(Evento).filter(Evento.id == dados.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # regra de negocio: só pode se inscrever em evento ativo
    if evento.status != "ativo":
        raise HTTPException(status_code=400, detail="Não é possível se inscrever em um evento que não está ativo")

    # regra de negocio: não pode se inscrever em evento que já aconteceu
    if evento.data_evento < date.today():
        raise HTTPException(status_code=400, detail="Esse evento já aconteceu")

    # regra de negocio: não pode se inscrever duas vezes no mesmo evento
    ja_inscrito = db.query(Inscricao).filter(
        Inscricao.usuario_id == dados.usuario_id,
        Inscricao.evento_id == dados.evento_id,
        Inscricao.status == "ativa"
    ).first()
    if ja_inscrito:
        raise HTTPException(status_code=400, detail="Usuário já está inscrito nesse evento")

    # regra de negocio: o evento não pode passar da capacidade máxima
    inscritos_ativos = db.query(Inscricao).filter(
        Inscricao.evento_id == dados.evento_id,
        Inscricao.status == "ativa"
    ).count()
    if inscritos_ativos >= evento.capacidade:
        raise HTTPException(status_code=400, detail="A capacidade máxima desse evento já foi atingida")

    nova_inscricao = Inscricao(
        usuario_id=dados.usuario_id,
        evento_id=dados.evento_id
    )
    db.add(nova_inscricao)
    db.commit()
    db.refresh(nova_inscricao)
    return nova_inscricao


@router.get("", response_model=list[InscricaoResposta])
def listar_inscricoes(skip: int = 0, limit: int = 100, db: Session = Depends(pegar_sessao)):
    return db.query(Inscricao).offset(skip).limit(limit).all()


@router.get("/evento/{evento_id}", response_model=list[InscricaoResposta])
def listar_inscritos_do_evento(evento_id: int, db: Session = Depends(pegar_sessao)):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # só as inscrições ativas contam como inscritos
    return db.query(Inscricao).filter(
        Inscricao.evento_id == evento_id,
        Inscricao.status == "ativa"
    ).all()


@router.get("/usuario/{usuario_id}", response_model=list[InscricaoResposta])
def listar_inscricoes_do_usuario(usuario_id: int, db: Session = Depends(pegar_sessao)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    return db.query(Inscricao).filter(Inscricao.usuario_id == usuario_id).all()


@router.put("/{inscricao_id}/cancelar", response_model=InscricaoResposta)
def cancelar_inscricao(inscricao_id: int, db: Session = Depends(pegar_sessao)):
    inscricao = db.query(Inscricao).filter(Inscricao.id == inscricao_id).first()
    if not inscricao:
        raise HTTPException(status_code=404, detail="Inscrição não encontrada")

    if inscricao.status == "cancelada":
        raise HTTPException(status_code=400, detail="Essa inscrição já está cancelada")

    # aqui não apaga do banco, só troca o status pra cancelada
    inscricao.status = "cancelada"
    db.commit()
    db.refresh(inscricao)
    return inscricao
