from typing import Annotated
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from store.db_conf import get_db
from store.models import User, UserRole
from .password import pwd_context
from jose import JWTError, jwt
from decouple import config

JWT_SECRET = config("secret")
ALGORITH = config("algorithm")


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user


def get_user(username, model,db: Session ):
    user = db.query(model).filter(model.username == username).first()
    return user


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    try:
        payload  = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITH])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
             raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")
        user = get_user(username, db)
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Qayta Login qilib ko'ring token xatolik")
    
    
def is_super_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    try:
        payload  = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITH])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")
        user = get_user(username, User, db)
        if user.role == UserRole.SUPERUSER:
            return user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi SuperUser emas")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Qayta Login qilib ko'ring token xatolik")
    
    
def is_admin(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    try:
        payload  = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITH])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")
        user = get_user(username, User, db)
        if user.role == UserRole.ADMIN:
            return user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi Admin emas")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Qayta Login qilib ko'ring token xatolik")
    

def is_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    try:
        payload  = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITH])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")
        user = get_user(username, User, db)
        if user.role == UserRole.STAFF:
            return user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi Royxatdan otmagan")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Qayta Login qilib ko'ring token xatolik")
    

def is_admin_or_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    try:
        payload  = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITH])
        username = payload.get("sub")
        user_id = payload.get("id")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi topilmadi")
        user = get_user(username, User, db)
        if user.role == UserRole.ADMIN or user.role == UserRole.STAFF:
            return user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Foydalanuvchi Royxatdan otmagan")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Qayta Login qilib ko'ring token xatolik")