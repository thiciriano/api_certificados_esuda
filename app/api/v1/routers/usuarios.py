"""rotas de usuarios"""

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.models import Usuario


router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Criar usuário",
    description="Cria um novo usuário no sistema",
)
async def criar_usuario(
    usuario: dict = Body(
        ...,
        openapi_examples={
            "Aluno": {
                "summary": "Aluno (Participante)",
                "description": "Preenche dados de um participante padrão",
                "value": {"nome": "Thiago", "email": "thiago@esuda.edu.br", "senha": "123", "papel": "participante"},
            },
            "Professor": {
                "summary": "Professor (Organizador)",
                "description": "Preenche dados para perfil organizador",
                "value": {"nome": "Victor", "email": "victor@esuda.edu.br", "senha": "123", "papel": "organizador"},
            },
        },
    ),
    db: Session = Depends(get_db),
):
    # email é unico
    for u in db.query(Usuario).all():
        if u.email == usuario.get("email"):
            raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    novo = Usuario(
        nome=usuario.get("nome", ""),
        email=usuario.get("email", ""),
        senha=usuario.get("senha", ""),
        papel=usuario.get("papel", "participante"),
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return {"success": True, "message": "Usuário criado", "data": {"id": novo.id, "nome": novo.nome}}


@router.get(
    "",
    summary="Listar usuários",
    description="Lista todos os usuários do sistema",
)
async def listar_usuarios(db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).all()
    return [
        {"id": u.id, "nome": u.nome, "email": u.email, "papel": u.papel}
        for u in usuarios
    ]


@router.put(
    "/{usuario_id}",
    summary="Atualizar usuário",
    description="Atualiza os dados de um usuário existente",
)
async def atualizar_usuario(
    usuario_id: int,
    usuario: dict = Body(
        ...,
        openapi_examples={
            "Atualizar": {
                "summary": "Dados atualizados",
                "description": "Atualiza nome e/ou papel do usuário",
                "value": {"nome": "Novo Nome", "papel": "participante"},
            }
        },
    ),
    db: Session = Depends(get_db),
) -> dict:
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # só muda o que veio no body
    if "nome" in usuario:
        db_usuario.nome = usuario["nome"]
    if "email" in usuario:
        db_usuario.email = usuario["email"]
    if "papel" in usuario:
        db_usuario.papel = usuario["papel"]
    db.commit()
    db.refresh(db_usuario)
    return {"success": True, "message": "Usuário atualizado", "data": {"id": db_usuario.id, "nome": db_usuario.nome}}


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar usuário",
    description="Remove um usuário do sistema",
)
async def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)) -> None:
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if db_usuario:
        db.delete(db_usuario)
        db.commit()
