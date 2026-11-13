"""rotas de usuarios"""

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_active_user, get_user_optional, precisa_de_permissao
from app.core.permissions import eh_dono_ou_admin
from app.core.security import hash_senha
from app.core.swagger_presets import EXEMPLO_USUARIO, EXEMPLO_USUARIO_UPDATE
from app.database.database import get_db
from app.models.models import Usuario
from app.schemas.schemas import RespostaUsuario, UsuarioCreate, UsuarioOut, UsuarioUpdate


router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=RespostaUsuario,
    summary="Criar usuário",
    description=(
        "Cadastra um novo usuário. Qualquer visitante pode se auto-cadastrar como "
        "'participante' ou 'organizador'. Somente administradores podem criar usuários "
        "com papel 'admin'."
    ),
)
async def criar_usuario(
    usuario: UsuarioCreate = Body(..., openapi_examples=EXEMPLO_USUARIO),
    current_user: Usuario | None = Depends(get_user_optional),
    db: Session = Depends(get_db),
) -> RespostaUsuario:
    # ninguem se promove a admin sem ser admin (nem deslogado)
    if usuario.papel == "admin" and (current_user is None or current_user.papel != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem criar usuários administradores",
        )

    # email é unico (R1)
    if db.query(Usuario).filter(Usuario.email == usuario.email).first():
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    novo = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha=hash_senha(usuario.senha),  # guarda o hash, nunca a senha pura
        papel=usuario.papel,
    )
    db.add(novo)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()  # email repetido em corrida (foi outro request que gravou)
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    db.refresh(novo)
    return RespostaUsuario(message="Usuário criado", data=novo)


@router.get(
    "/me",
    response_model=RespostaUsuario,
    summary="Usuário autenticado",
    description="Devolve os dados do usuário dono do token (sem senha).",
)
async def usuario_logado(current_user: Usuario = Depends(get_current_active_user)) -> RespostaUsuario:
    return RespostaUsuario(message="Usuário autenticado", data=current_user)


@router.get(
    "",
    response_model=list[UsuarioOut],
    summary="Listar usuários",
    description="Lista todos os usuários do sistema. Somente administradores.",
)
async def listar_usuarios(
    _: Usuario = Depends(precisa_de_permissao("pode_gerenciar_usuarios")),
    db: Session = Depends(get_db),
) -> list[UsuarioOut]:
    return db.query(Usuario).all()


@router.put(
    "/{usuario_id}",
    response_model=RespostaUsuario,
    summary="Atualizar usuário",
    description=(
        "Atualiza os dados de um usuário. Cada um altera o próprio cadastro; "
        "somente administradores alteram outros usuários e o papel de qualquer um."
    ),
)
async def atualizar_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate = Body(..., openapi_examples=EXEMPLO_USUARIO_UPDATE),
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> RespostaUsuario:
    if not eh_dono_ou_admin(current_user, usuario_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você só pode alterar o próprio cadastro",
        )

    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    dados = usuario.model_dump(exclude_unset=True)

    # impede que o usuario comum edite o proprio perfil de acesso
    if "papel" in dados and current_user.papel != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem alterar o papel",
        )

    if "email" in dados:
        email_ja_usado = (
            db.query(Usuario)
            .filter(Usuario.email == dados["email"], Usuario.id != usuario_id)
            .first()
        )
        if email_ja_usado:
            raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    if "senha" in dados:
        db_usuario.senha = hash_senha(dados.pop("senha"))

    # só muda o que veio no body
    for campo, valor in dados.items():
        setattr(db_usuario, campo, valor)

    db.commit()
    db.refresh(db_usuario)
    return RespostaUsuario(message="Usuário atualizado", data=db_usuario)


@router.delete(
    "/{usuario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletar usuário",
    description="Remove um usuário do sistema. Somente administradores.",
)
async def deletar_usuario(
    usuario_id: int,
    _: Usuario = Depends(precisa_de_permissao("pode_gerenciar_usuarios")),
    db: Session = Depends(get_db),
) -> None:
    db_usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(db_usuario)
    db.commit()
