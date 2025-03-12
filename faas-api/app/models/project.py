from sqlalchemy import Column, Integer, String, LargeBinary, Text
from app.database import Base

# Define the Project model
class Project(Base):
    __tablename__ = "projects"

    # Define columns
    id = Column(Integer, primary_key=True, index=True)
    srs_content = Column(Text)
    screenshot_url = Column(String)
    preview_link = Column(String)
    langsmith_run_id = Column(String)
