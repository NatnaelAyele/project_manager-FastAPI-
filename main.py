from fastapi import FastAPI
from database import Base, engine
from routers import user,projects, auth, tasks



app = FastAPI()
Base.metadata.create_all(bind = engine)

@app.get("/healthy")
def health_cheker():
    return {"status": "healthy"}

app.include_router(user.router)
app.include_router(projects.router)
app.include_router(auth.router)
app.include_router(tasks.router)