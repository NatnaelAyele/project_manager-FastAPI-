from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated, Optional
from .auth import get_current_user
from database import Localsession
from sqlalchemy.orm import session
from starlette import status
from models import  Projects,Tasks
from pydantic import BaseModel, Field

router = APIRouter(prefix="/tasks", tags=["tasks"])

user_dependancy = Annotated[dict,Depends(get_current_user)]


def get_db():
    db = Localsession()
    try:
        yield db
    finally:
        db.close()

db_dependancy = Annotated[session, Depends(get_db)]

class task_request_model(BaseModel):
    task_name:str
    priority: int  = Field(gt=0, lt=6)
    project_name: str
    completed: bool

class update_request_model(BaseModel):
    Project_name: str
    task_name: str
    new_name: Optional [str]
    new_priority: Optional[int] = Field(gt=0, lt=6)
    new_status: Optional[bool]
    


@router.post("/create-task", status_code=status.HTTP_201_CREATED)
def create_new_task(db: db_dependancy, task_request:task_request_model, user: user_dependancy):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated user")
    
    project = db.query(Projects).filter(Projects.project_name == task_request.project_name).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail="project does not exist")
    if db.query(Tasks).filter(Tasks.owner_project_id == project.id, Tasks.task_name == task_request.task_name).first():
        raise HTTPException(status_code=status.HTTP_412_PRECONDITION_FAILED, detail="task name must be unique")
   
    task = Tasks(task_name = task_request.task_name, priority = task_request.priority, owner_project_id = project.id, owner_id = user["id"])
    db.add(task)
    db.commit()

@router.put("/update-task")
def update_task_info(user: user_dependancy, db:db_dependancy, update_request:update_request_model):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated user")
    project = db.query(Projects).filter(Projects.owner_id == user["id"], Projects.project_name == update_request.Project_name).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project not found")
  
    task = db.query(Tasks).filter(Tasks.owner_id == user["id"], Tasks.owner_project_id == project.id, Tasks.task_name == update_request.task_name)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found")
    
    if (update_request.new_name is None and update_request.new_priority is  None and update_request.new_status is None):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="nothing to update from task")
    if update_request.new_name is not None:
        task.task_name = update_request.new_name
    if update_request.new_priority is not None:
        task.priority = update_request.new_priority
    if update_request.new_status is not None:
        task.completed = update_request.new_status

    db.commit()
    
@router.get("/list-project_tasks")
def list_all_tasks_under_project(user: user_dependancy, project_name: str, db:db_dependancy):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated user")
    project = db.query(Projects).filter( Projects.owner_id == user["id"],Projects.project_name == project_name).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    return db.query(Tasks).filter(Tasks.owner_project_id == project.id).all() 

@router.delete("/delelte-task")

def delete_task(user:user_dependancy, db:db_dependancy, project_name:str, task_name:str):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthenticated user")
    
    project = db.query(Projects).filter(Projects.owner_id == user["id"], Projects.project_name == project_name).first()
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="project not found")
    
    task = db.query(Tasks).filter( Tasks.owner_project_id == project.id ,Tasks.task_name == task_name).first()
    if task is None:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="task not found") 
    db.delete(task)
    db.commit()