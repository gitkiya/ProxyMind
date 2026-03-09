from datetime import datetime
from typing import Literal
from pydantic import BaseModel , EmailStr


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    
class PostCreate(PostBase):
    pass

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    
    
    class Config:
        from_attributes = True

class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    
    class Config:
        from_attributes = True
        
class PostOut(BaseModel):
    Post: Post
    votes_count: int
    
    class Config:
        from_attributes = True        
        
class UserBase(BaseModel):
    email: EmailStr
    password: str  
           
class UserLogin(BaseModel):
    email: EmailStr
    password: str  
    
class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    user_id: int | None = None   
    
class vote(BaseModel):
    post_id: int
    dir: Literal[0,1]