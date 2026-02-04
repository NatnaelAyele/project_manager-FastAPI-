from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from .auth import get_current_user
from database import Localsession
from sqlalchemy.orm import session
from starlette import status
from models import  Projects, Tasks

router = APIRouter(prefix="/Projects", tags=["projects"])

user_dependancy = Annotated[dict,Depends(get_current_user)]


def get_db():
    db = Localsession()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[session, Depends(get_db)]

@router.post("/create-project")
def create_new_projects(user:user_dependancy, db:db_dependancy, project_name_request:str):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated user")
    
    if db.query(Projects).filter(Projects.owner_id == user.get("id")).filter(Projects.project_name == project_name_request).first():
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail="Project name must be unique")
    project = Projects(project_name = project_name_request, owner_id = user.get("id"))
    
    db.add(project)
    db.commit()

@router.get("/list-all-projects")
def list_all_projects(user:user_dependancy,db:db_dependancy):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated user")
    
    return db.query(Projects).filter(Projects.owner_id == user["id"]).all()


@router.delete("/delelte-projects")
def delete_task(user:user_dependancy, db:db_dependancy, project_name:str):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated user")
    
    project = db.query(Projects).filter(Projects.owner_id == user["id"], Projects.project_name == project_name).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project not found")
    db.delete(project)
    db.commit()
