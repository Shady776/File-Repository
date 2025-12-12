from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db
from ..utils.password import bcrypt

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/create", response_model=schemas.UserResponse)
def create_user(
    user_data: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    try:
        user_data.password = bcrypt(user_data.password)
        new_user = models.Users(**user_data.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.get("/{id}", response_model=schemas.UserResponse)
def get_user_by_id(id: str, db: Session = Depends(get_db)):
    user = db.query(models.Users).where(models.Users.id==id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )
    return user
    


@router.put("/", status_code=status.HTTP_202_ACCEPTED, response_model=schemas.UserResponse)
def update_user(update: schemas.UserUpdate, db: Session=Depends(get_db), current_user: schemas.TokenData = Depends(oauth2.get_current_user)):
    user_query = db.query(models.Users).where(models.Users.id==current_user.id)
    user = user_query.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )
    if update.password!="":
        update.password = bcrypt(update.password)
    
    user_query.update(update.model_dump(exclude_unset=True))
    db.commit()
    updated_user = user_query.first()
    db.refresh(updated_user)
    return updated_user


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    db: Session = Depends(get_db), 
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):  
    user = db.query(models.Users).where(models.Users.id==current_user.id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )

    
    db.delete(user)
    db.commit()
    return

