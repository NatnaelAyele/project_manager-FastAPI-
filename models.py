from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from database import Base


class Users(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(34), unique=True)
    first_name = Column(String(34))
    last_name = Column(String(34))
    email = Column(String(34), unique=True)
    hashed_password = Column(String(72))
    is_active = Column(Boolean, default=True)

class Projects(Base):
    __tablename__ = "Projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String(40))
    owner_id = Column(Integer, ForeignKey(Users.id))

    __table_args__ = (
        UniqueConstraint(
            "owner_id",
            "project_name",
            name="uq_project_per_user"
        ),
    )

class Tasks(Base):
    __tablename__ = "Tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(40))
    priority = Column(Integer)
    owner_project_id = Column(Integer, ForeignKey(Projects.id))
    owner_id = Column(Integer, ForeignKey(Users.id))
    completed = Column(Boolean, default=False)


    __table_args__ = (
        UniqueConstraint(
            "owner_project_id",
            "task_name",
            name="uq_task_per_project"
        ),
    )