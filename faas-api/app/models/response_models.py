from pydantic import BaseModel
from typing import Optional

class ProjectResponse(BaseModel):
    id: int
    srs_content: Optional[str] = None
    screenshot_url: Optional[str] = None
    preview_link: Optional[str] = None
    langsmith_run_id: Optional[str] = None

    class Config:
        from_attributes = True