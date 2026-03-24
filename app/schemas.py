from pydantic import BaseModel, EmailStr, conint
from typing import Optional
from datetime import datetime


class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    class Config:
        orm_mode = True

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    # rating: Optional[int] = None

class PostCreate(PostBase):
    pass

class Post(BaseModel):
    id: int
    title: str
    content: str
    published: bool = True
    created_at: datetime
    owner_id: int
    owner: UserOut
    class Config: # to allow fastapi to be able to send the model (it can only send dicts)
        orm_mode = True

class PostOut(BaseModel):
    Post: Post
    votes: int
    class Config: # to allow fastapi to be able to send the model (it can only send dicts)
        orm_mode = True

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1, ge=0)
