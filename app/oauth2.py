from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
import os
from fastapi import HTTPException, status, Depends
from dotenv import load_dotenv
from .schemas import TokenData
from fastapi.security.oauth2 import OAuth2PasswordBearer

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def create_access_token(data: dict) -> str:
    payload = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    payload['exp'] = exp
    access_token = jwt.encode(
        payload,
        SECRET_KEY,
        ALGORITHM
    )
    return access_token

def verify_access_token(token: str, credential_exception: HTTPException) -> TokenData:
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY,
            ALGORITHM
        )
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credential_exception
        token_data = TokenData(
           id=user_id,
        )
        return token_data
    except JWTError:
        raise credential_exception
    
def get_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )
    return verify_access_token(token, credential_exception)

