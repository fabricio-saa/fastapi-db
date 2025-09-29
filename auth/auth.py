import os
from jose import jwt, JWTError
from sqlmodel import Session, select
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from typing import Optional
import datetime as dt

from models import User

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/token')


def verify_password(plain: str, hashed:str):
    return pwd_context.verify(plain, hashed)

def hash_password(plain:str):
    return pwd_context.hash(plain)

def create_access_token(subject:str, expires_delta:Optional[int] = None):
    if expires_delta is None:
        expires_delta = dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = dt.datetime.now() + expires_delta
    to_encode = {
        'sub': subject,
        "exp": expire
    }
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_user_by_username(session: Session, username: str):
    query = select(User).where(User.username == username)
    return session.exec(query).first()

def authenticate_user(session: Session, username: str, password:str):
    user = get_user_by_username(session, username)
    if not user or not verify_password(password, user.password):
        return None
    
    return user

