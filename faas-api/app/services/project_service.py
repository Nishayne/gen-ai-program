import logging
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app.models.project import Project
from fastapi import UploadFile
import docx
import io
from . import analysis_service, generation_service # Import analysis and generation services.
from langchain_core.tools import tool
from langchain.callbacks import StdOutCallbackHandler
from langchain.callbacks import LangChainTracer
import uuid
from .common_service import GraphState, deploy_frontend;

logging.basicConfig(level=logging.INFO)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

# Initialize LangChainTracer
tracer = LangChainTracer(project_name="AI-Frontend-Generation11223") #LangChainTracer

# Function to create a project
def create_project(db: Session, srs_file: UploadFile, screenshot_url: str):
    # Extract text from the uploaded DOCX file
    # with LangChainTracer("create_project",project_name="AI-Frontend-Generation11223") as run:
    try:
        srs_content = extract_text_from_docx(srs_file.file.read())

        # Create a new Project instance
        project = Project(srs_content=srs_content, screenshot_url=screenshot_url)
        db.add(project)
        db.commit()
        db.refresh(project)

        # Run the LangGraph workflow with LangSmith tracing
        # with tracer.run(f"Project-{project.id}",project_name="AI-Frontend-Generation11223") as run:
        # Analyze SRS and generate frontend project
        graph_state = GraphState() 
        screenshot_details = analysis_service.analyze_screenshot(screenshot_url)
        graph_state.screenshot_details=screenshot_details
        graph_state.srs_content=srs_content
        analysis_results = analysis_service.analyze_srs(srs_content,screenshot_details)
        generated_code = generation_service.generate_angular_setup(analysis_results)
        generation_service.execute_angular_setup(generated_code)
        ui_generation_results = generation_service.generate_ui_components(graph_state, analysis_results)
        graph_state.ui_components = ui_generation_results["ui_components"] 
        graph_state.ui_dependencies = ui_generation_results["ui_dependencies"]
        graph_state.api_endpoints = analysis_results["api_endpoints"] 
        graph_state = generation_service.generate_api_integration(graph_state)
        ui_test_results = generation_service.generate_ui_tests(graph_state)
        graph_state.ui_tests = ui_test_results["ui_tests"]
        generation_service.generate_documentation(graph_state)
        graph_state = generation_service.generate_frontend_dockerfile(graph_state)
        validation_report = generation_service.validate_ui(graph_state.ui_components, graph_state.srs_content, graph_state.screenshot_details)
        logging.info(f"UI Validation Report: {validation_report}")
        generation_service.save_generated_files(graph_state)
        # Deploy the generated project (conceptual)
        preview_link = deploy_frontend(graph_state.dockerfile_content)

        # Update the project with preview link and LangSmith run ID
        project.preview_link = preview_link
        project.langsmith_run_id = str(uuid.uuid4()) # run.run_id
        db.commit()
        return project
    except Exception as inner_e:
        logging.error(f"Error in Project-{project.id} workflow: {inner_e}")
        #run.record_exception(inner_e)
        return None
    except Exception as outer_e:
        logging.error(f"Error creating project: {outer_e}")
        #run.record_exception(outer_e)
        return None
    
# Function to get a project by ID
def get_project(db: Session, project_id: int):
    # with LangChainTracer("get_project",project_name="AI-Frontend-Generation11223") as run:
    return db.query(Project).filter(Project.id == project_id).first()

# Function to extract text from a DOCX file
def extract_text_from_docx(file_content: bytes):
    # with LangChainTracer("extract_text_from_docx",project_name="AI-Frontend-Generation11223") as run:
    doc = docx.Document(io.BytesIO(file_content))
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text
