from datetime import date, datetime
from typing import Union, Optional
from pydantic import BaseModel


class User(BaseModel):
    username : str
    hashed_password : str
    
    class Config:
        from_attributes = True


class UserCreateSchema(User):
    name : str
    surname : str
    phone_number : str
    

class UserOut(UserCreateSchema):
    id: int
    role: str
    manager : Optional[UserCreateSchema] = None


class UserWithId(BaseModel):
    id : int
    
    class Config:
        from_attributes  = True
        
class UserPasswordDelete(UserWithId):
    name : str
    surname : str
    username : str
    password : str
    class Config:
        from_attributes = True