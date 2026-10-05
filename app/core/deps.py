"""dependencias do jwt (pega o usuario logado, confere se ta ativo, pega as permissoes)"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.security import decode_access_token
from app.core.config import settings
from app.models.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


def get_current_user(
    security_scopes: SecurityScopes = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    """descobre quem é o usuario pelo token"""
    if security_scopes.type == "http":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = security_scopes.credentials
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(Usuario).filter(Usuario.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


def get_current_active_user(
    current_user: Usuario = Depends(get_current_user),
) -> Usuario:
    """usuario logado e ativo"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


def get_current_user_permissions(
    current_user: Usuario = Depends(get_current_user),
) -> dict:
    """permissoes do papel do usuario"""
    from app.core.permissions import PERFIS
    return PERFIS.get(current_user.papel, PERFIS["participante"])
