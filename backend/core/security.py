from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import jwt
from backend.core.config import settings

BCRYPT_MAX_PASSWORD_BYTES = 72


def is_password_too_long(password: str) -> bool:
    return len(password.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if is_password_too_long(plain_password):
        return False
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    if is_password_too_long(password):
        raise ValueError("Password cannot be longer than 72 bytes")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
