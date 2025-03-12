from fastapi import FastAPI
from app.routers import projects
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create a FastAPI instance
app = FastAPI()

# Include the projects router
app.include_router(projects.router)
