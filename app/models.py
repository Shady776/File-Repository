from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from uuid import uuid4
from datetime import datetime

class Users(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)
    
    files = relationship("File", back_populates="owner")

class File(Base):
    __tablename__ = "files"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    filename = Column(String)
    file_url = Column(String)
    file_size = Column(Integer)
    file_type = Column(String)
    file_hash = Column(String, unique=True, index=True)
    upload_date = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    public_id = Column(String, nullable=False)
    

    owner = relationship("Users", back_populates="files")