"""rotas de categorias"""

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import precisa_de_permissao
from app.core.swagger_presets import EXEMPLO_CATEGORIA, EXEMPLO_CATEGORIA_UPDATE
from app.database.database import get_db
from app.models.models import Categoria, Evento, Usuario
from app.schemas.schemas import CategoriaCreate, CategoriaOut, CategoriaUpdate, RespostaCategoria


router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=RespostaCategoria,
    summary="Criar categoria",
    description="Cria uma nova categoria de evento. Exige perfil de administrador ou organizador.",
)
async def criar_categoria(
    categoria: CategoriaCreate = Body(..., openapi_examples=EXEMPLO_CATEGORIA),
    _: Usuario = Depends(precisa_de_permissao("pode_gerenciar_categoria")),
    db: Session = Depends(get_db),
) -> RespostaCategoria:
    # nome é unico
    if db.query(Categoria).filter(Categoria.nome == categoria.nome).first():
        raise HTTPException(status_code=400, detail="Ja existe categoria com este nome")

    novo = Categoria(nome=categoria.nome, descricao=categoria.descricao)
    db.add(novo)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # nome repetido em corrida
        raise HTTPException(status_code=400, detail="Ja existe categoria com este nome")
    db.refresh(novo)
    return RespostaCategoria(message="Categoria criada", data=novo)


@router.get(
    "",
    response_model=list[CategoriaOut],
    summary="Listar categorias",
    description="Lista todas as categorias do sistema. Consulta aberta (não exige login).",
)
async def listar_categorias(db: Session = Depends(get_db)) -> list[CategoriaOut]:
    return db.query(Categoria).all()


@router.put(
    "/{categoria_id}",
    response_model=RespostaCategoria,
    summary="Atualizar categoria",
    description="Atualiza os dados de uma categoria existente. Exige perfil de administrador ou organizador.",
)
async def atualizar_categoria(
    categoria_id: int,
    categoria: CategoriaUpdate = Body(..., openapi_examples=EXEMPLO_CATEGORIA_UPDATE),
    _: Usuario = Depends(precisa_de_permissao("pode_gerenciar_categoria")),
    db: Session = Depends(get_db),
) -> RespostaCategoria:
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    dados = categoria.model_dump(exclude_unset=True)

    if "nome" in dados:
        nome_ja_usado = (
            db.query(Categoria)
            .filter(Categoria.nome == dados["nome"], Categoria.id != categoria_id)
            .first()
        )
        if nome_ja_usado:
            raise HTTPException(status_code=400, detail="Ja existe categoria com este nome")

    # só muda o que veio no body
    for campo, valor in dados.items():
        setattr(db_categoria, campo, valor)

    db.commit()
    db.refresh(db_categoria)
    return RespostaCategoria(message="Categoria atualizada", data=db_categoria)


@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar categoria",
    description="Remove uma categoria do sistema. Exige perfil de administrador ou organizador.",
)
async def deletar_categoria(
    categoria_id: int,
    _: Usuario = Depends(precisa_de_permissao("pode_gerenciar_categoria")),
    db: Session = Depends(get_db),
) -> None:
    db_categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoria nao encontrada")

    # nao deixa apagar categoria que tem evento usando
    em_uso = db.query(Evento).filter(Evento.categoria_id == categoria_id).first()
    if em_uso:
        raise HTTPException(status_code=400, detail="Categoria possui eventos vinculados")

    db.delete(db_categoria)
    db.commit()
