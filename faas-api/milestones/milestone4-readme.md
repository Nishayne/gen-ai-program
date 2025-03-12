### Milestone 4, focusing on persistence and iterations in the LangGraph workflow. This involves ensuring that the system retains previously generated UI components, maintains context, and aligns new generations with previous iterations.

## Modify GraphState

```bash
from typing import Dict, List, Optional, Any
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import functional_graph

class GraphState:
    srs_content: Optional[str] = None
    screenshot_details: Optional[Dict[str, Any]] = None
    # ui_components: Changed to Dict[str, Dict[str, str]] to store component code as a dictionary of file names and their contents.
    ui_components: Optional[Dict[str, Dict[str, str]]] = None  # Component name: {file_name: code}
    state_management: Optional[str] = None
    api_endpoints: Optional[List[Dict[str, Any]]] = None
    # ui_tests: Changed to Dict[str, str] to store test code associated with component names.
    ui_tests: Optional[Dict[str, str]] = None # Component name: test code
    errors: Optional[List[str]] = None
    iterations: int = 0
    # ui_dependencies: Added to track UI dependencies to prevent redundant re-generation.
    ui_dependencies: Optional[Dict[str, List[str]]] = None # Component name: [dependencies]
```

###  Implementing Persistence and Context in Nodes

###  Modify the nodes to use the GraphState and maintain context.
```bash
from langchain_community.chat_models import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY)

def generate_ui_components(state: GraphState):
    """Generates Angular UI components based on analysis results and previous components."""

    analysis_results = {
        "ui_components": ["login-form", "signup-form"], # example input, could be from previous nodes
        "state_management": "NgRx",
        "api_endpoints": ["/users", "/auth"],
        "accessibility": "WCAG guidelines",
        "styling": "Material UI with custom theme",
    }

    ui_components = state.ui_components or {}
    ui_dependencies = state.ui_dependencies or {}

    new_components = []
    for component in analysis_results.get("ui_components", []):
        if component not in ui_components:
            new_components.append(component)

    for component in new_components:
        prompt = ChatPromptTemplate.from_template(
            """Generate an Angular component for: {component}.
            Follow best practices, use existing components if needed.
            Existing components: {existing_components}
            {component_details}

            Provide the component code in a markdown format, including file content for each file.
            """
        )

        existing_components = list(ui_components.keys())
        component_details = f"Component Details: {component}" # Add any specific component details here.

        message = prompt.format_messages(component=component, existing_components=existing_components, component_details=component_details)
        response = groq_llm(message)

        # Parse the response and update ui_components and ui_dependencies
        # Example:
        component_code = {"login-form.component.ts": "...", "login-form.component.html": "..."} # replace with parsing logic
        ui_components[component] = component_code
        ui_dependencies[component] = ["dependency1", "dependency2"] # replace with dependency detection logic

    return {"ui_components": ui_components, "ui_dependencies": ui_dependencies}

def generate_ui_tests(state: GraphState):
    """Generates Cypress UI tests for the generated components."""

    ui_components = state.ui_components or {}
    ui_tests = state.ui_tests or {}

    new_tests = {}
    for component, code in ui_components.items():
        if component not in ui_tests:
            prompt = ChatPromptTemplate.from_template(
                """Generate Cypress UI tests for the following Angular component: {component}.
                Ensure proper unit tests, integration tests, and end-to-end tests.
                {component_code}

                Provide the test code in a markdown format, including file content.
                """
            )

            message = prompt.format_messages(component=component, component_code=code)
            response = groq_llm(message)
            new_tests[component] = response.content

    ui_tests.update(new_tests)

    return {"ui_tests": ui_tests}
```
