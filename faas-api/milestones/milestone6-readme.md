### Milestone 6, focusing on generating documentation, including a LangGraph workflow visualization and essential project documentation using an LLM.

## Generating LangGraph Workflow Visualization
```bash

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import functional_graph
from langgraph.graph import END
from langgraph.prebuilt import draw_mermaid_png
from PIL import Image
from io import BytesIO
import subprocess
from io import BytesIO

# npm install -g mermaid.cli
def draw_mermaid_png_local(mermaid_syntax):
    """Generates a Mermaid diagram locally using the Mermaid CLI."""

    try:
        # Save the Mermaid syntax to a file
        with open("mermaid_diagram.mmd", "w") as f:
            f.write(mermaid_syntax)

        # Use the Mermaid CLI to generate the PNG
        subprocess.run(["mmdc", "-i", "mermaid_diagram.mmd", "-o", "mermaid_diagram.png"], check=True)

        # Read the PNG and return bytes
        with open("mermaid_diagram.png", "rb") as f:
            image_bytes = f.read()
        img = Image.open(BytesIO(image_bytes))
        img.save("langgraph_workflow_local.png")

        return image_bytes
    except subprocess.CalledProcessError as e:
        print(f"Error generating Mermaid diagram: {e}")
        return None

# Assuming you have your LangGraph workflow defined as 'workflow'
# Example:
# workflow = create_graph() # from previous steps
def generate_workflow_visualization(workflow):
    """Generates a graph visualization of the LangGraph workflow."""

    try:
        image_bytes = draw_mermaid_png(workflow)
        img = Image.open(BytesIO(image_bytes))
        img.save("langgraph_workflow.png")
        print("LangGraph workflow visualization generated: langgraph_workflow.png")
    except Exception as e:
        print(f"Error generating LangGraph visualization: {e}")

```

## Generating Documentation (Using Groq LLM)
```bash
from langchain_community.chat_models import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY)

def generate_documentation(analysis_results, ui_components):
    """Generates project documentation using Groq LLM."""

    # Generate README.md
    readme_prompt = ChatPromptTemplate.from_template(
        """Generate a README.md file for an Angular frontend project.
        Include setup instructions, usage guidelines, and project structure details.
        {project_details}

        Provide the README.md content in a markdown format.
        """
    )

    project_details = f"Project Details: {analysis_results}, Components: {ui_components}" # Add project details here.

    readme_message = readme_prompt.format_messages(project_details=project_details)
    readme_content = groq_llm(readme_message).content

    with open("README.md", "w") as f:
        f.write(readme_content)
    print("README.md generated.")

    # Generate component documentation
    for component, code in ui_components.items():
        component_prompt = ChatPromptTemplate.from_template(
            """Generate documentation for the following Angular component: {component}.
            Include props, states, API integration details, and usage examples.
            {component_code}

            Provide the component documentation in a markdown format.
            """
        )

        component_message = component_prompt.format_messages(component=component, component_code=code)
        component_content = groq_llm(component_message).content

        with open(f"{component}.md", "w") as f:
            f.write(component_content)
        print(f"Component documentation generated: {component}.md")

    # Generate code comments (conceptual)
    # This would involve parsing the generated code and adding comments using LLM.
    # Implementation omitted for brevity.
    print("Code comments generation (conceptual).")

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

# Generate workflow visualization
# generate_workflow_visualization(workflow) # uncomment after creating workflow

# Generate documentation
generate_documentation(analysis_results, ui_components)
```
