from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import session
from database import Localsession
from models import Users
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets
from starlette import status

router = APIRouter(prefix="/authorization", tags=["auth"])

token_bearer = OAuth2PasswordBearer(tokenUrl="/authorization/token")

def get_db():
    db = Localsession()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[session, Depends(get_db)]
bcrypt_context = CryptContext(schemes="bcrypt", deprecated = "auto")

SECRETE_KEY = "a72ae000a3be14f6f3d67cdb9f4f5503324e6be690b7a0409a7125a6bade5bda"
ALGORITHM = "HS256"
def  authenticate_user(user_name, password, db):
    user = db.query(Users).filter(Users.user_name == user_name).first()
    if not user:
        return False
    
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

def generate_token(user_name, id, expiry_delta:timedelta):
    expiry_time = datetime.now(timezone.utc) + expiry_delta
    payload={
        "sub": user_name,
        "id": id,
        "exp": expiry_time 
    }
    return jwt.encode(payload, SECRETE_KEY, algorithm=ALGORITHM)

def get_current_user(token: Annotated[str, Depends(token_bearer)]):
    try:
        payload = jwt.decode(token, SECRETE_KEY, algorithms=[ALGORITHM])
        user_name = payload.get("sub")
        id =  payload.get("id")
        exp =  payload.get("exp")
        if  user_name is None or id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated user")
        return{
            "user_name": user_name,
            "id": id,
            "exp": exp
        }
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.post("/token")
def get_login_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: db_dependancy):
   user = authenticate_user(form_data.username, form_data.password, db)
   if user:
       token =  generate_token(user.user_name, user.id, timedelta(minutes=20))
       return {
        "access_token": token,
        "token_type": "bearer"
    }
   raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenitcated user")
   


