### Milestone 8, focusing on creating a Frontend Application as a Service (FAAS) API. 
### This will allow users to submit SRS documents, validate UI requirements, generate frontend projects, 
### and receive hosted previews and LangSmith logs.

import logging
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import project_service
from app.models.project import Project
from app.models.response_models import ProjectResponse # Import the Pydantic model
from langsmith import Client  # Import LangSmith client

logging.basicConfig(level=logging.INFO)

load_dotenv()

LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

if not LANGCHAIN_API_KEY:
    raise ValueError("LANGCHAIN_API_KEY environment variable not set.")

client = Client(api_key=LANGCHAIN_API_KEY)

# Create an APIRouter instance
router = APIRouter()

# API endpoint to create a project
# /projects/ (POST): Submit SRS Documents
# Purpose: Allows users to upload SRS documents (DOCX) and a screenshot URL.
# Request:
# srs_file: UploadFile (DOCX)
# screenshot_url: str
# Functionality:
# Extracts text from the DOCX.
# Creates a Project record in the database.
# Starts the LangGraph workflow.
# Returns the project_id.
@router.post("/projects/", response_model=ProjectResponse)
async def create_project(srs_file: UploadFile = File(...), screenshot_url: str = Form(...), db: Session = Depends(get_db)):
    db_project = project_service.create_project(db, srs_file, screenshot_url)
    if db_project:
        return ProjectResponse(
        id=db_project.id,
        srs_content=db_project.srs_content,
        screenshot_url=db_project.screenshot_url,
        preview_link=db_project.preview_link,
        langsmith_run_id=db_project.langsmith_run_id
    )
    else:
        raise HTTPException(status_code=500, detail="Project creation failed")

# API endpoint to read a project by ID
@router.get("/projects/{project_id}", response_model=ProjectResponse)
def read_project(project_id: int, db: Session = Depends(get_db)):
    db_project = project_service.get_project(db, project_id)
    if db_project:
        return db_project
    else:
        raise HTTPException(status_code=404, detail="Project not found")

# API endpoint to read Langsmith Logs by Project ID
@router.get("/projects/{project_id}/logs")
async def get_project_logs(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not project.langsmith_run_id:
        raise HTTPException(status_code=404, detail="Langsmith run ID not found")

    # Fetch logs from LangSmith using project.langsmith_run_id
    try:
        run = client.read_run(run_id=project.langsmith_run_id)
        # Extract desired log information from the run object.
        # Example:
        logs = {
            "name": run.name,
            "start_time": run.start_time,
            "end_time": run.end_time,
            "inputs": run.inputs,
            "outputs": run.outputs,
            "events": [event.dict() for event in run.events] # Convert events to dict.
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching LangSmith logs: {e}")

    return logs