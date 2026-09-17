import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.conexao import pegar_sessao
from app.models.inscricao import Inscricao
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioAtualizar, UsuarioCriar, UsuarioResposta

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


def gerar_hash_senha(senha: str) -> str:
    # por enquanto é só um hash simples, na segunda entrega isso vira bcrypt com jwt
    return hashlib.sha256(senha.encode()).hexdigest()


@router.post("", response_model=UsuarioResposta, status_code=status.HTTP_201_CREATED)
def criar_usuario(dados: UsuarioCriar, db: Session = Depends(pegar_sessao)):
    # regra de negocio: o email não pode repetir
    email_ja_existe = db.query(Usuario).filter(Usuario.email == dados.email).first()
    if email_ja_existe:
        raise HTTPException(status_code=400, detail="Já existe um usuário com esse e-mail")

    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha=gerar_hash_senha(dados.senha),
        papel=dados.papel
    )
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


@router.get("", response_model=list[UsuarioResposta])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(pegar_sessao)):
    return db.query(Usuario).offset(skip).limit(limit).all()


@router.get("/{usuario_id}", response_model=UsuarioResposta)
def buscar_usuario(usuario_id: int, db: Session = Depends(pegar_sessao)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.put("/{usuario_id}", response_model=UsuarioResposta)
def atualizar_usuario(usuario_id: int, dados: UsuarioAtualizar, db: Session = Depends(pegar_sessao)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # só altera o que foi mandado no json
    if dados.nome:
        usuario.nome = dados.nome
    if dados.senha:
        usuario.senha = gerar_hash_senha(dados.senha)
    if dados.papel:
        usuario.papel = dados.papel

    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_usuario(usuario_id: int, db: Session = Depends(pegar_sessao)):
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # não deixa excluir usuário que tem inscrição, pra não quebrar o histórico dos eventos
    tem_inscricao = db.query(Inscricao).filter(Inscricao.usuario_id == usuario_id).first()
    if tem_inscricao:
        raise HTTPException(
            status_code=400,
            detail="Esse usuário tem inscrições cadastradas, então não pode ser excluído"
        )

    db.delete(usuario)
    db.commit()
