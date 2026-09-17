from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.conexao import pegar_sessao
from app.models.categoria import Categoria
from app.models.evento import Evento
from app.schemas.categoria import CategoriaAtualizar, CategoriaCriar, CategoriaResposta

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.post("", response_model=CategoriaResposta, status_code=status.HTTP_201_CREATED)
def criar_categoria(dados: CategoriaCriar, db: Session = Depends(pegar_sessao)):
    nome_ja_existe = db.query(Categoria).filter(Categoria.nome == dados.nome).first()
    if nome_ja_existe:
        raise HTTPException(status_code=400, detail="Já existe uma categoria com esse nome")

    nova_categoria = Categoria(nome=dados.nome, descricao=dados.descricao)
    db.add(nova_categoria)
    db.commit()
    db.refresh(nova_categoria)
    return nova_categoria


@router.get("", response_model=list[CategoriaResposta])
def listar_categorias(db: Session = Depends(pegar_sessao)):
    return db.query(Categoria).all()


@router.put("/{categoria_id}", response_model=CategoriaResposta)
def atualizar_categoria(categoria_id: int, dados: CategoriaAtualizar, db: Session = Depends(pegar_sessao)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    if dados.nome:
        categoria.nome = dados.nome
    if dados.descricao is not None:
        categoria.descricao = dados.descricao

    db.commit()
    db.refresh(categoria)
    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_categoria(categoria_id: int, db: Session = Depends(pegar_sessao)):
    categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    # não deixa excluir categoria que tem evento usando
    tem_evento = db.query(Evento).filter(Evento.categoria_id == categoria_id).first()
    if tem_evento:
        raise HTTPException(status_code=400, detail="Essa categoria tem eventos ligados a ela, não pode excluir")

    db.delete(categoria)
    db.commit()
