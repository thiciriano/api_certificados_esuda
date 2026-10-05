"""token jwt"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """gera o token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    """abre o token, devolve None se estiver invalido ou expirado"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)
        return payload
    except JWTError:
        return None
