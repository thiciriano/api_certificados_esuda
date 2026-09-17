from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.conexao import pegar_sessao
from app.models.evento import Evento
from app.models.inscricao import Inscricao
from app.models.categoria import Categoria
from app.schemas.evento import EventoAtualizar, EventoCriar, EventoResposta

router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post("", response_model=EventoResposta, status_code=status.HTTP_201_CREATED)
def criar_evento(dados: EventoCriar, db: Session = Depends(pegar_sessao)):
    # se mandar categoria, verifica se ela existe
    if dados.categoria_id is not None:
        categoria = db.query(Categoria).filter(Categoria.id == dados.categoria_id).first()
        if not categoria:
            raise HTTPException(status_code=400, detail="Categoria não existe")

    novo_evento = Evento(
        titulo=dados.titulo,
        descricao=dados.descricao,
        data_evento=dados.data_evento,
        local=dados.local,
        capacidade=dados.capacidade,
        categoria_id=dados.categoria_id,
        status="ativo"
    )
    db.add(novo_evento)
    db.commit()
    db.refresh(novo_evento)
    return novo_evento


@router.get("", response_model=list[EventoResposta])
def listar_eventos(status_filtro: str | None = None, db: Session = Depends(pegar_sessao)):
    consulta = db.query(Evento)
    # dá pra filtrar por status na url, ex: /eventos?status_filtro=ativo
    if status_filtro:
        consulta = consulta.filter(Evento.status == status_filtro)
    return consulta.all()


@router.get("/{evento_id}", response_model=EventoResposta)
def buscar_evento(evento_id: int, db: Session = Depends(pegar_sessao)):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return evento


@router.put("/{evento_id}", response_model=EventoResposta)
def atualizar_evento(evento_id: int, dados: EventoAtualizar, db: Session = Depends(pegar_sessao)):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    if dados.categoria_id is not None:
        categoria = db.query(Categoria).filter(Categoria.id == dados.categoria_id).first()
        if not categoria:
            raise HTTPException(status_code=400, detail="Categoria não existe")

    if dados.titulo is not None:
        evento.titulo = dados.titulo
    if dados.descricao is not None:
        evento.descricao = dados.descricao
    if dados.data_evento is not None:
        evento.data_evento = dados.data_evento
    if dados.local is not None:
        evento.local = dados.local
    if dados.capacidade is not None:
        evento.capacidade = dados.capacidade
    if dados.categoria_id is not None:
        evento.categoria_id = dados.categoria_id
    if dados.status is not None:
        # o status só pode ser ativo ou cancelado
        if dados.status not in ("ativo", "cancelado"):
            raise HTTPException(status_code=400, detail="O status só pode ser ativo ou cancelado")
        evento.status = dados.status

    db.commit()
    db.refresh(evento)
    return evento


@router.delete("/{evento_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_evento(evento_id: int, db: Session = Depends(pegar_sessao)):
    evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # não deixa excluir evento que tem inscrição, senão o histórico some
    tem_inscricao = db.query(Inscricao).filter(Inscricao.evento_id == evento_id).first()
    if tem_inscricao:
        raise HTTPException(
            status_code=400,
            detail="Esse evento já tem inscrições, então não pode ser excluído"
        )

    # obs: a partir da segunda entrega só o admin vai poder chegar nessa rota (jwt)
    db.delete(evento)
    db.commit()
