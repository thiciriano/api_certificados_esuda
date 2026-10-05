"""rotas de categorias"""

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import Categoria


router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Criar categoria",
    description="Cria uma nova categoria de evento",
)
async def criar_categoria(
    categoria: dict = Body(
        ...,
        openapi_examples={
            "Workshop": {
                "summary": "Categoria Workshop",
                "description": "Eventos de curta duração com mão na massa",
                "value": {"nome": "Workshop Pratico", "descricao": "Eventos praticos"},
            }
        },
    ),
    db: Session = Depends(get_db),
):
    # nome é unico
    for c in db.query(Categoria).all():
        if c.nome == categoria.get("nome"):
            raise HTTPException(status_code=400, detail="Ja existe categoria com este nome")

    novo = Categoria(nome=categoria.get("nome", ""), descricao=categoria.get("descricao", ""))
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {"success": True, "message": "Categoria criada", "data": {"id": novo.id, "nome": novo.nome}}


@router.get(
    "",
    summary="Listar categorias",
    description="Lista todas as categorias do sistema",
)
async def listar_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return [{"id": c.id, "nome": c.nome, "descricao": c.descricao} for c in categorias]


@router.put(
    "/{categoria_id}",
    summary="Atualizar categoria",
    description="Atualiza os dados de uma categoria existente",
)
async def atualizar_categoria(
    categoria_id: int,
    categoria: dict = Body(
        ...,
        openapi_examples={
            "Atualizar": {
                "summary": "Categoria atualizada",
                "description": "Atualiza nome e/ou descricao da categoria",
                "value": {"nome": "Workshop Advanced", "descricao": "Workshop avançado"},
            }
        },
    ),
    db: Session = Depends(get_db),
) -> dict:
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    if "nome" in categoria:
        db_categoria.nome = categoria["nome"]
    if "descricao" in categoria:
        db_categoria.descricao = categoria["descricao"]
    db.commit()
    db.refresh(db_categoria)
    return {"success": True, "message": "Categoria atualizada", "data": {"id": db_categoria.id, "nome": db_categoria.nome}}


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar categoria",
    description="Remove uma categoria do sistema",
)
async def deletar_categoria(categoria_id: int, db: Session = Depends(get_db)) -> None:
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if db_categoria:
        db.delete(db_categoria)
        db.commit()
