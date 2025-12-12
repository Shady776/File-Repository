from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..utils.password import verify_hash
from ..database import get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

router=APIRouter(
    prefix='/auth',
    tags=['Auth']
)

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    users = db.query(models.Users).filter(models.Users.email == user_credentials.username).first()
    
    if not users:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"invalid Credentials")
    
    if not verify_hash(user_credentials.password, users.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=F"Invalid credentials")
    
    access_token = oauth2.create_access_token(data = {"user_id": str(users.id)})
    return{"access_token": access_token, "token_type": "bearer"}
