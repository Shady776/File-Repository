from fastapi import FastAPI
from .routers import files, users, auth
from .cloudinary_config import setup_cloudinary
from .database import engine, Base

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(files.router)


@app.on_event("startup")
async def startup_event():
    setup_cloudinary()
    Base.metadata.create_all(bind=engine)
