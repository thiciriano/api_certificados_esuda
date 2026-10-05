"""rotas de eventos"""

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import Evento, Categoria


router = APIRouter(prefix="/eventos", tags=["Eventos"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Criar evento",
    description="Cria um novo evento no sistema",
)
async def criar_evento(
    evento: dict = Body(
        ...,
        openapi_examples={
            "Workshop": {
                "summary": "Evento Workshop",
                "description": "Evento de teste com capacidade para 50 vagas",
                "value": {
                    "titulo": "Workshop FastAPI",
                    "descricao": "Evento de prática",
                    "data_evento": "2026-11-20",
                    "local": "Laboratorio 3",
                    "capacidade": 50,
                    "categoria_id": 1,
                },
            }
        },
    ),
    db: Session = Depends(get_db),
):
    cat = db.query(Categoria).filter(Categoria.id == evento.get("categoria_id")).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    # titulo tambem é unico
    for e in db.query(Evento).all():
        if e.titulo == evento.get("titulo") and e.id != evento.get("id"):
            raise HTTPException(status_code=400, detail="Já existe evento com este título")

    novo = Evento(
        titulo=evento.get("titulo", ""),
        descricao=evento.get("descricao", ""),
        data_evento=evento.get("data_evento", ""),
        local=evento.get("local", ""),
        capacidade=evento.get("capacidade", 50),
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {"success": True, "message": "Evento criado", "data": {"id": novo.id, "titulo": novo.titulo}}


@router.get(
    "",
    summary="Listar eventos",
    description="Lista todos os eventos do sistema",
)
async def listar_eventos(db: Session = Depends(get_db)):
    eventos = db.query(Evento).all()
    return [
        {
            "id": e.id,
            "titulo": e.titulo,
            "descricao": e.descricao,
            "local": e.local,
            "capacidade": e.capacidade,
            "categoria_id": e.categoria_id,
        }
        for e in eventos
    ]


@router.put(
    "/{evento_id}",
    summary="Atualizar evento",
    description="Atualiza os dados de um evento existente",
)
async def atualizar_evento(
    evento_id: int,
    evento: dict = Body(
        ...,
        openapi_examples={
            "Atualizar": {
                "summary": "Evento atualizado",
                "description": "Atualiza título e/ou capacidade do evento",
                "value": {"titulo": "Workshop Atualizado", "capacidade": 60},
            }
        },
    ),
    db: Session = Depends(get_db),
) -> dict:
    db_evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    if "titulo" in evento:
        db_evento.titulo = evento["titulo"]
    if "descricao" in evento:
        db_evento.descricao = evento["descricao"]
    if "local" in evento:
        db_evento.local = evento["local"]
    if "capacidade" in evento:
        db_evento.capacidade = evento["capacidade"]
    db.commit()
    db.refresh(db_evento)
    return {"success": True, "message": "Evento atualizado", "data": {"id": db_evento.id, "titulo": db_evento.titulo}}


@router.delete(
    "/{evento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar evento",
    description="Remove um evento do sistema",
)
async def deletar_evento(evento_id: int, db: Session = Depends(get_db)) -> None:
    db_evento = db.query(Evento).filter(Evento.id == evento_id).first()
    if db_evento:
        db.delete(db_evento)
        db.commit()
