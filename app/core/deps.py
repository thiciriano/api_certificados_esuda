"""dependencias do jwt (pega o usuario logado, confere se ta ativo, pega as permissoes)"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.permissions import PERFIS
from app.core.security import decode_access_token
from app.database.database import get_db
from app.models.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login".lstrip("/"),
)
# mesmo esquema mas sem exigir token (pra rotas que mudam comportamento se tiver logado)
oauth2_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login".lstrip("/"),
    auto_error=False,
)


def _usuario_do_token(token: str, db: Session) -> Usuario:
    """abre o token e busca o usuario, erro 401 se tiver qualquer coisa errada"""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    try:
        user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    except (TypeError, ValueError):
        user = None
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário do token não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """descobre quem é o usuario pelo token"""
    return _usuario_do_token(token, db)


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    """usuario logado e ativo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    return current_user


def get_user_optional(
    token: str | None = Depends(oauth2_optional),
    db: Session = Depends(get_db),
) -> Usuario | None:
    """deslogado devolve None, logado devolve o usuario (rotas que aceitam os dois)"""
    if token is None:
        return None
    return _usuario_do_token(token, db)


def precisa_de_permissao(permissao: str):
    """dependencia que so deixa passar se o papel do usuario tiver a permissao da matriz"""
    def verificar(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
        perfil = PERFIS.get(current_user.papel, {})
        if not perfil.get(permissao):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para esta operação",
            )
        return current_user
    return verificar
