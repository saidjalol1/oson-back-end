from typing import List
from fastapi import APIRouter
from dependencies import injections
from store.pydantics import user_models
from store.models import User, Store, UserRole
from auth import password
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    tags=["Users"]
)


# Get Staffs
@router.get("/staffs", response_model=List[user_models.UserOut])
async def  get_user(user = injections.admin_user, db = injections.database_dep):
    return db.query(User).filter(User.manager_id == user.id).all()


# Delete user
@router.delete("/user/delete")
async def  get_user(object: user_models.UserWithId, user = injections.admin_user, db = injections.database_dep):
    user = db.query(User).filter(User.manager_id == user.id, User.id == object.id).first()
    if user:
        db.delete(user)
        db.commit()
        return {"message":"Deleted Successfully"}
    return {"message":"User not found"}


# reset password
@router.post("/user/password-reset")
async def  get_user(object: user_models.UserPasswordDelete,user = injections.admin_user, db = injections.database_dep):
    user = db.query(User).filter(User.manager_id == user.id, User.id == object.id).first()
    if user:
        user.hashed_password = password.pwd_context.hash(object.password)
        user.username = object.username
        user.name = object.name
        user.surname = object.surname

        await injections.session_manager(user, db)
        return {"message": "Password Updated Successfully"}
    return {"message":"User not found"}


# Admin user password reset
@router.post("/admin/password-reset")
async def  get_user(object: user_models.UserPasswordDelete,user = injections.super_user, db = injections.database_dep):
    user = db.query(User).filter(User.manager_id == user.id, User.id == object.id).first()
    if user:
        user.hashed_password = password.pwd_context.hash(object.password)
        await injections.session_manager(user, db)
        return {"message": "Password Updated Successfully"}
    return {"message":"User not found"}


# create superuser
@router.post("/super-user-create", response_model=user_models.UserOut)
async def super_userCreate(superuser: user_models.UserCreateSchema, db = injections.database_dep):
    try:
        user =  User(**superuser.model_dump())
        user.role = UserRole.SUPERUSER
        user.hashed_password = password.pwd_context.hash(user.hashed_password)
        user =  await injections.session_manager(user, db)
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        injections.error_messages(error_msg)
    return  user
    
    
# create admin user
@router.post("/admin-user-create", response_model=user_models.UserOut)
async def super_userCreate(adminuser: user_models.UserCreateSchema, current_user=injections.super_user,db = injections.database_dep):
    try:
        user = User(**adminuser.model_dump())
        user.super_user_id  = current_user.id
        user.manager_id = current_user.id
        user.role = UserRole.ADMIN
        user.hashed_password = password.pwd_context.hash(user.hashed_password)
        user = await injections.session_manager(user, db)
        await injections.session_manager(Store(**{"boss_id":user.id}), db)
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        injections.error_messages(error_msg)
    return user
    
    
# create staff user
@router.post("/staff-user-create", response_model=user_models.UserOut)
async def super_userCreate(adminuser: user_models.UserCreateSchema, current_user=injections.admin_user, db = injections.database_dep):
    try:
        user = User(**adminuser.model_dump())
        user.user_admin_id  = current_user.id
        user.manager_id = current_user.id
        user.role  = UserRole.STAFF
        user.hashed_password = password.pwd_context.hash(user.hashed_password)
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig)
        injections.error_messages(error_msg)
    return await injections.session_manager(user, db)
    
    
    
    

