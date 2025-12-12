from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr

    class Config:
        orm_mode = True
        
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    id: str


class FileBase(BaseModel):
    filename: str
    file_type: str


class FileUpload(FileBase):
    id: str
    file_url: str
    file_size: int
    file_hash: str
    upload_date: datetime
    user_id: str
    public_id: str
    
    class Config:
        from_attributes = True
        
class FileUpdate(BaseModel):
    id: Optional[str] = None
    file_url: Optional[str] = None
    filename: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None 
    file_hash: Optional[str] = None
    upload_date: Optional[datetime] = None
    public_id: Optional[str] = None
    
    class Config:
        from_attributes = True