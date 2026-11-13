"""rotas de autenticacao (login)"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verificar_senha
from app.database.database import get_db
from app.models.models import Usuario
from app.schemas.schemas import RespostaToken


router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/login",
    response_model=RespostaToken,
    summary="Login",
    description=(
        "Autentica por e-mail e senha e devolve o token JWT. "
        "No campo **username** vai o e-mail. O token expira em "
        "ACCESS_TOKEN_EXPIRE_MINUTES e deve ser enviado como `Authorization: Bearer <token>`."
    ),
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> RespostaToken:
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()

    # mesma mensagem nos dois casos pra nao dizer se o email existe ou nao
    if not usuario or not verificar_senha(form_data.password, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )

    # o sub é o id do usuario, é ele que o get_current_user usa pra te reconhecer
    token = create_access_token(data={"sub": str(usuario.id), "papel": usuario.papel})
    return RespostaToken(access_token=token, token_type="bearer")
