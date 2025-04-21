from typing import Optional, Union
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session
from store import models
from store.db_conf import get_db
from auth.auth_main import is_admin, is_super_user, is_user, is_admin_or_user

super_user : models.User = Depends(is_super_user)
admin_user : models.User = Depends(is_admin)
user_or_admin : models.User = Depends(is_admin_or_user)
user : models.User = Depends(is_user)
database_dep : Session = Depends(get_db)


async def session_manager(object, db):
    """ creating object in databse"""
    object_ = object
    db.add(object)
    db.commit()
    db.refresh(object_)
    return object_


def error_messages(error_msg):
    if "unique constraint" in error_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists."
        )
    elif "not-null constraint" in error_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields."
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error: " + error_msg
        )