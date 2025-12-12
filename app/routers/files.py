from fastapi import APIRouter, UploadFile, status, File as FileParam, HTTPException, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import FileUpload, FileUpdate
from ..models import File as FileModel, Users
from ..oauth2 import get_current_user
from typing import List
import cloudinary.uploader
from ..utils.file_hash import get_file_hash, delete_from_cloudinary

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)

def upload_to_cloudinary(file: UploadFile):
    try:
        file_content = file.file.read()
        result = cloudinary.uploader.upload(
            file_content,
            resource_type="auto",
            folder="uploads"
        )
        file.file.seek(0)
        file_url = result.get("secure_url")
        file_size = result.get("bytes")
        public_id = result.get("public_id")  # add this
        return file_url, file_size, public_id  # now returns 3 values
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=FileUpload)
def upload_file(
    file: UploadFile = FileParam(...),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    file_content = file.file.read()
    file_hash = get_file_hash(file_content)
    file.file.seek(0)
    
    existing_file = db.query(FileModel).filter(FileModel.file_hash == file_hash).first()
    if existing_file:
        raise HTTPException(
            status_code=400, 
            detail=f"This file already exists (ID: {existing_file.id})."
        )
    if not current_user or not current_user.id:
        raise HTTPException(status_code=401, detail="User not authenticated properly")

    # Upload to Cloudinary and get public_id
    file_url, file_size, public_id = upload_to_cloudinary(file)
    
    # Save all file info including public_id
    db_file = FileModel(
        filename=file.filename,
        file_type=file.content_type,
        file_url=file_url,
        file_size=file_size,
        file_hash=file_hash,
        user_id=current_user.id,
        public_id=public_id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[FileUpload])
def list_all_files(
    db: Session = Depends(get_db),
):
    files = db.query(FileModel).all()
    return files

@router.get("/my-files", status_code=status.HTTP_200_OK, response_model=List[FileUpload])
def list_my_files(
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    users_files = db.query(FileModel).filter(FileModel.user_id == current_user.id).all()
    return users_files

@router.get("/{file_id}", status_code=status.HTTP_200_OK, response_model=FileUpload)
def get_file_by_id(
    file_id: str, 
    db: Session = Depends(get_db),
):
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return file

@router.put("/{file_id}", status_code=status.HTTP_200_OK, response_model=FileUpdate)
def update_file(
    file_id: str,
    file: UploadFile = FileParam(...),
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    db_file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if db_file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this file")
  
    file_content = file.file.read()
    new_file_hash = get_file_hash(file_content)
    file.file.seek(0)

    existing_file = db.query(FileModel).filter(
        FileModel.file_hash == new_file_hash,
        FileModel.id != file_id
    ).first()
    if existing_file:
        raise HTTPException(
            status_code=400, 
            detail=f"A file with this content already exists (ID: {existing_file.id})"
        )
    
    # Delete old file from Cloudinary using stored public_id
    delete_from_cloudinary(db_file.public_id)
    
    # Upload new file and get public_id
    file_url, file_size, public_id = upload_to_cloudinary(file)
    
    # Update database record
    db_file.filename = file.filename
    db_file.file_type = file.content_type
    db_file.file_url = file_url
    db_file.file_size = file_size
    db_file.file_hash = new_file_hash
    db_file.public_id = public_id  # <-- store new public_id
    
    db.commit()
    db.refresh(db_file)
    
    return db_file

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: str, 
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    file = db.query(FileModel).filter(FileModel.id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    if file.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this file")
    
    delete_from_cloudinary(file.file_url)
    
    db.delete(file)
    db.commit()
    return None