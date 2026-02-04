from typing import Annotated
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import session

from database import Localsession
from models import Users

from passlib.context import CryptContext
from starlette import status


router = APIRouter(prefix="/user", tags=["users"])


class user_model(BaseModel):
    user_name: str
    first_name: str
    last_name: str
    email: str
    Password: str

    model_config = {
        "json_schema_extra":{
            "example":{
                "user_name": "unique user",
                "first_name": "tester",
                "last_name": "tester last_name",
                "email": "unique eamil",
                "Password": "test123"
            }
        }
    }


def get_db():
    db = Localsession()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[session, Depends(get_db)]
bcrypt_context = CryptContext(schemes="bcrypt", deprecated = "auto")


@router.post("/create-user", status_code=status.HTTP_201_CREATED)
def create_user(db:db_dependancy, new_user: user_model):    
    user = Users(
        user_name = new_user.user_name,
        first_name = new_user.first_name,
        last_name = new_user.last_name,
        email = new_user.email,
        hashed_password = bcrypt_context.hash(new_user.Password)
        )
    


    db.add(user)
    db.commit()