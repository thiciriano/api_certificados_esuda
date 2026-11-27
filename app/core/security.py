"""token jwt e hash de senha"""
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_senha(senha: str) -> str:
    """transforma a senha em hash bcrypt (a senha pura nunca é gravada)"""
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def verificar_senha(senha: str, hash_guardado: str) -> bool:
    """confere se a senha bate com o hash guardado"""
    try:
        return bcrypt.checkpw(senha.encode(), hash_guardado.encode())
    except ValueError:
        # hash antigo/corrompido nao pode derrubar o login
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """gera o token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """abre o token, devolve None se estiver invalido ou expirado"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
