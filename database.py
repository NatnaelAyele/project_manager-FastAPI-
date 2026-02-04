from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


sqlalchemy_database_url = "sqlite:///./project_manager.db"
engine = create_engine(sqlalchemy_database_url, connect_args={"check_same_thread": False})
Localsession = sessionmaker(bind=engine, autoflush=False, autocommit = False)
Base = declarative_base()


