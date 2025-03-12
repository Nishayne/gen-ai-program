### Milestone 5, focusing on using an LLM to generate a Dockerfile for the frontend project.

## Generating the Dockerfile (Using Groq LLM)
```bash
from langchain_community.chat_models import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY)

def generate_frontend_dockerfile(analysis_results, ui_components):
    """Generates a Dockerfile for the Angular frontend project."""

    prompt = ChatPromptTemplate.from_template(
        """Generate a Dockerfile for an Angular frontend project.
        Use Node.js for building and Nginx for serving the application.
        Ensure best practices for Dockerfile creation.
        {project_details}

        Provide the Dockerfile content in a markdown format.
        """
    )

    project_details = f"Project Details: {analysis_results}, Components: {ui_components}" # Add project details here.

    message = prompt.format_messages(project_details=project_details)
    response = groq_llm(message)
    return response.content

# Example usage (assuming analysis_results and ui_components from the previous steps)
analysis_results = {
    "ui_components": ["login-form", "signup-form"],
    "state_management": "NgRx",
    "api_endpoints": ["/users", "/auth"],
    "accessibility": "WCAG guidelines",
    "styling": "Material UI with custom theme",
}

ui_components = {
    "login-form": {"login-form.component.ts": "...", "login-form.component.html": "..."},
    "signup-form": {"signup-form.component.ts": "...", "signup-form.component.html": "..."},
}

dockerfile_content = generate_frontend_dockerfile(analysis_results, ui_components)
print("Generated Dockerfile:\n", dockerfile_content)
```
