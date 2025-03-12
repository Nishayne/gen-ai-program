## Implement Milestone 2, which involves generating the Angular 17 project setup based on the analysis results from the previous step.
## Focus on creating the project structure, setting up state management, and installing dependencies.

## Milestone 3, focusing on autonomous UI generation, API integration, and testing/debugging workflows using LLMs.

## Milestone 4, focusing on persistence (GraphState) and iterations in the LangGraph workflow. This involves ensuring that the system 
## retains previously generated UI components, maintains context, and aligns new generations with previous iterations.

## Milestone 5, focusing on using an LLM to generate a Dockerfile for the frontend project.

## Milestone 6, focusing on generating documentation, including a LangGraph workflow visualization 
## and essential project documentation using an LLM.

## Milestone 7, focusing on LangSmith logging and debugging. 
## This involves setting up a LangSmith project and integrating logging into the LangGraph workflow

##  Python script that uses Groq's Llama 3 model and LangChain 
## to generate the necessary commands and file structures (Angular project setup)

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import subprocess
from typing import Dict, List, Optional, Any
from langgraph.graph import StateGraph, START, END
import logging
from app.services.analysis_service import analyze_screenshot, analyze_srs
from PIL import Image
from io import BytesIO
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langchain.callbacks.tracers.langchain import LangChainTracer
from app.services.common_service import GraphState
from .common_service import deploy_frontend

from langchain_community.graphs.graph_document import GraphDocument
#from langchain.graphs.graph_document import GraphDocument
import networkx as nx
import matplotlib.pyplot as plt

import re

logging.basicConfig(level=logging.INFO)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY") # from the .env file
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
MEDIA_PATH = os.getenv("MEDIA_PATH")

# Initialize LangChainTracer -- This initializes the LangChain tracer with your LangSmith project name.
tracer = LangChainTracer(project_name="AI-Frontend-Generation11223")

# initialize 
groq_llm = ChatGroq(groq_api_key=GROQ_API_KEY,
    model="llama-3.2-11b-vision-preview", #"llama-3.3-70b-versatile", #"mistral-saba-24b" or "llama-3.1-8b-instant",
    temperature=0)

"""
    Parses the response content from an LLM to extract component code and filenames.

    Args:
        response_content (str): The string content returned by the language model,
                                    expected to contain code blocks and file names.

    Returns:
        component_code: A dictionary where keys are file names and values are the corresponding code content.
                Returns an empty dictionary if parsing fails or no code blocks are found.
"""
def parse_component_code(response_content):
    """Parses component code from LLM response (Markdown code blocks)."""

    # Match filenames like ui_components.component.ts, .html, .scss
    file_names = re.findall(r"([\w\-]+\.(?:ts|html|scss))", response_content)

    # Match code blocks that specify a language (typescript, html, scss)
    file_code_blocks = re.findall(r"```(?:typescript|html|scss)\s*([\s\S]*?)```", response_content)

    # Validate parsed data
    if not file_names or not file_code_blocks or len(file_names) != len(file_code_blocks):
        logging.error("Parsing failed: file names or code blocks missing/mismatched.")
        return {}

    # Map filenames to corresponding code blocks
    component_code = {file_name: file_code_blocks[i].strip() for i, file_name in enumerate(file_names)}

    return component_code


"""
    Detects import statements and potential dependencies within a given component code string.

    Args:
        component_code (dict): The dict containing the component's code.

    Returns:
        dict: A list of detected dependencies (imported modules/components).
"""
def detect_dependencies(component_code):
    # with LangChainTracer("detect_dependencies",project_name="AI-Frontend-Generation11223") as run:
    """Detects dependencies using string matching."""

    typescript_code = component_code.get("component.ts", "") # or component.component.ts
    html_code = component_code.get("component.html", "") # or component.component.html

    module_dependencies = re.findall(r"import\s*{[^}]*}\s*from\s*['\"]@angular/[^'\"]+['\"]", typescript_code)
    component_dependencies = re.findall(r"<([\w-]+)[^>]*>", html_code)

    # remove html tags.
    component_dependencies = list(set(component_dependencies))

    return {"modules": module_dependencies, "components": component_dependencies}
    
"""
    Generates Angular project setup commands and file structure using Groq LLM.

    Args:
        analysis_results: The analysis results to be used in the prompt.

    Returns:
        The generated Angular project setup commands and file structure.
             Returns None if an error occurs during LLM interaction.
"""    
def generate_angular_setup(analysis_results):
    """Generates Angular project setup commands and file structure using Groq LLM."""
    # with LangChainTracer("generate_angular_setup",project_name="AI-Frontend-Generation11223") as run:

    # --skip-install 
    #     8.  **styling**
    #     * The SCSS block should include button { display: inline-block; } to prevent stacking issues.
    #     * Consider adding spacing between buttons with display: flex; gap: 10px;
    #     * Add aria-label attributes to buttons for better screen reader support
    
    prompt = ChatPromptTemplate.from_template(
        """Given the following analysis results: {analysis_results},
        generate the necessary Angular CLI commands to create a new Angular 17 project named 'project_root',
        set up state management (NgRx or Services-based), install dependencies (RxJS, Angular Material),
        and create the following folder structure, including creating directories as needed:
        {folder_structure}

        To ensure the commands execute correctly, follow these steps:

        1.  **Workspace Creation:**
            * Create a new Angular workspace named 'project_root' and generate code using `ng new project_root --skip-git --routing --style=scss`.
        2.  **Workspace Navigation:**
            * Navigate into the 'project_root' directory using `cd project_root`.
        3.  **Angular CLI configuration:**
            * configure the angular cli to use the project_root using the command `ng config cli.defaultProject project_root`
        4.  **ng add Commands:**
            For libraries like @angular/material and @ngrx/store, use ng add to handle installation and configuration automatically.
            Specifically use these commands:
                * ng add @angular/material
                * ng add @ngrx/store
                * ng add @ngrx/effects
                * ng add @ngrx/entity
                * ng add @ngrx/router-store
        5.  **Install Dependencies:**
            * Install the dependencies and devDependencies one after the other, after navigating into the workspace.
        6.  **Documentation:**
            * Generate any readme or md documentation is in sub-folder docs of project_root
        7.  **app.module.ts**
            * Since mat-card and mat-button are to be used, import the necessary Angular Material modules in app.module.ts

        Ensure the generated project is compilable and compatible by:

        1.  Setting the `package.json` scripts to:
            ```json
            "scripts": {{
                "ng": "ng",
                "start": "ng serve",
                "build": "ng build",
                "watch": "ng build --watch --configuration development",
                "test": "ng test",
                "json-server": "json-server --watch db.json --port 3000"
            }}
            ```

        2.  Including the following dependencies in the `package.json`:
            ```json
            "dependencies": {{
                "@angular/animations": "^17.3.0",
                "@angular/cdk": "^17.3.10",
                "@angular/common": "^17.3.0",
                "@angular/compiler": "^17.3.0",
                "@angular/core": "^17.3.0",
                "@angular/forms": "^17.3.0",
                "@angular/material": "^17.3.10",
                "@angular/platform-browser": "^17.3.0",
                "@angular/platform-browser-dynamic": "^17.3.0",
                "@angular/platform-server": "^17.3.0",
                "@angular/router": "^17.3.0",
                "@angular/ssr": "^17.3.8",
                "apexcharts": "^4.5.0",
                "chart.js": "^4.4.8",
                "express": "^4.18.2",
                "leaflet": "^1.9.4",
                "material-icons": "^1.13.14",
                "ngx-apexcharts": "^0.7.0",
                "rxjs": "~7.8.0",
                "tslib": "^2.3.0",
                "zone.js": "~0.14.3"
            }}
            ```

        3.  Including the following devDependencies in the `package.json`:
            ```json
            "devDependencies": {{
                "@angular-devkit/build-angular": "^17.3.8",
                "@angular/cli": "^17.3.8",
                "@angular/compiler-cli": "^17.3.0",
                "@types/express": "^4.17.17",
                "@types/jasmine": "~5.1.0",
                "@types/jest": "^29.5.14",
                "@types/leaflet": "^1.9.16",
                "@types/node": "^18.18.0",
                "jasmine-core": "~5.1.0",
                "json-server": "^1.0.0-beta.3",
                "karma": "~6.4.0",
                "karma-chrome-launcher": "~3.2.0",
                "karma-coverage": "~2.2.0",
                "karma-jasmine": "~5.1.0",
                "karma-jasmine-html-reporter": "~2.1.0",
                "typescript": "~5.4.2"
            }}
            ```

        Provide the commands and file structure in a markdown format, including file content where appropriate, with routing, components and services as needed.
        When creating a file, if the parent folders do not exist, create them.
        """
    )

    folder_structure = """
    project_root/
    │── src/
    │   ├── app/
    │   │   ├── components/
    │   │   │   ├── button.component.ts
    │   │   │   ├── modal.component.ts
    │   │   │   ├── form.component.ts
    │   │   │   └── index.ts
    │   │   ├── pages/
    │   │   │   ├── home.component.ts
    │   │   │   ├── dashboard.component.ts
    │   │   │   ├── login.component.ts
    │   │   │   ├── signup.component.ts
    │   │   │   └── index.ts
    │   │   ├── services/
    │   │   │   ├── api.service.ts
    │   │   │   ├── auth.service.ts
    │   │   │   ├── user.service.ts
    │   │   │   └── index.ts
    │   │   ├── state/
    │   │   │   ├── store.ts
    │   │   │   ├── user.reducer.ts
    │   │   │   ├── settings.reducer.ts
    │   │   ├── assets/
    │   │   ├── styles/
    │   │   ├── app.module.ts
    │   │   ├── app-routing.module.ts
    │   │   └── app.component.ts
    │   ├── tests/
    │   ├── Dockerfile
    │   ├── angular.json
    │   ├── package.json
    │   ├── .env
    │   └── README.md
    """

    message = prompt.format_messages(analysis_results=analysis_results, folder_structure=folder_structure)
    response = groq_llm.invoke(message)
    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
    #logging.info(response)
    logging.info(" generate_angular_setup: success! ")
    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
    return response.content

"""
    Executes the generated Angular CLI commands.

    Args:
        commands (str): A string containing the Angular CLI commands to be executed,
                        separated by newlines.
    Returns:
        None: This function does not return a value.
"""
def execute_angular_setup(commands):
    """Executes the generated Angular CLI commands."""

    # with LangChainTracer("execute_angular_setup",project_name="AI-Frontend-Generation11223") as run:

    workspace_path="project_root"

    # original_cwd = os.getcwd()  # Store the original working directory
    try:
        # os.mkdir(workspace_path)  # mkdir Angular workspace directory should be done by ng new
        # os.chdir(workspace_path)  # Change to the Angular workspace directory

        lines = commands.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('ng new project_root'):
                try:
                    print(f"Executing command: {line}")
                    result = subprocess.run(line, shell=True, check=True, capture_output=True, text=True)
                    print(f"Command executed, return code: {result.returncode}")
                    if result.returncode != 0:
                        logging.error(f"Error creating Angular workspace. Stopping execution.")
                        return  # Stop if ng new fails.
                    # if not os.path.exists("./angular.json"):
                    #    logging.error(f"angular.json file not found. Stopping execution.")
                    #    return # stop if angular.json is not found.
                except subprocess.CalledProcessError as e:
                    logging.error(f"Error executing command: {line} - {e}")
                    logging.error(f"Stdout: {e.stdout}")
                    logging.error(f"Stderr: {e.stderr}")
                    return #stop execution.

            elif line.startswith('cd project_root'):
                try:
                    print(f"Executing command: {line}")
                    os.chdir("./project_root")
                    print(f"Current working directory: {os.getcwd()}")
                except Exception as e:
                    logging.error(f"Error changing directory: {e}")
                    return
            elif line.startswith('ng '):
                try:
                    print(f"Executing command: {line}")
                    result = subprocess.run(line, shell=True, check=True, capture_output=True, text=True)
                    print(f"Command executed, return code: {result.returncode}")
                except subprocess.CalledProcessError as e:
                    logging.error(f"Error executing command: {line} - {e}")
                    logging.error(f"Stdout: {e.stdout}")
                    logging.error(f"Stderr: {e.stderr}")
                    return # stop execution.
            elif line.startswith('mkdir '):
                try:
                    os.makedirs(line[6:])
                except FileExistsError:
                    logging.warning(f"Directory already exists: {line[6:]}")
                    pass
                except Exception as e:
                    logging.error(f"Error creating directory: {line[6:]} - {e}")
            elif line.startswith('touch '):
                try:
                    with open(line[6:], 'w') as f:
                        pass
                except Exception as e:
                    logging.error(f"Error creating file: {line[6:]} - {e}")
            elif line.startswith('echo '):
                parts = line.split(' > ')
                if len(parts) == 2:
                    content = parts[0][5:]
                    try:
                        with open(parts[1], 'w') as f:
                            f.write(content)
                    except Exception as e:
                        logging.error(f"Error writing to file: {parts[1]} - {e}")
    finally:
        # os.chdir(original_cwd)  # Return to the original directory
        logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
        #logging.info(commands)
        logging.info(" execute_angular_setup: success! ")
        logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")

"""
    Generates Angular UI components based on analysis results and previous components.

    Args:
        state (GraphState): The GraphState object containing project details and analysis results.
        analysis_results (Dict[str, Any]): The analysis results used for component generation. Defaults to an empty dictionary.

    Returns:
        GraphState: The updated GraphState object with generated UI components.
"""
def generate_ui_components(state: GraphState, analysis_results: Dict[str, Any] = {}):
    """Generates Angular UI components based on analysis results and previous components."""
    # with LangChainTracer("generate_ui_components",project_name="AI-Frontend-Generation11223") as run:

    """
    analysis_results = {
        "ui_components": ["login-form", "signup-form"], # example input, could be from previous nodes
        "state_management": "NgRx",
        "api_endpoints": ["/users", "/auth"],
        "accessibility": "WCAG guidelines",
        "styling": "Material UI with custom theme",
    }
    """
    ui_components = state.ui_components or {}
    ui_dependencies = state.ui_dependencies or {}

    new_components = []
    
    # Determine which components are new based on the analysis results
    for component in analysis_results:
        if component not in ui_components:
            new_components.append(component)
    
    # Generate each new UI component using the LLM
    for component in new_components:
        prompt = ChatPromptTemplate.from_template(
            """Generate an Angular component for: {component}.
            Follow best practices: component-based architecture, accessibility, styling consistency, modular design, 
            use existing components if needed.
            Existing components: {existing_components}
            Use TypeScript, SCSS, and Angular Material themes if applicable.
            {component_details}
            Provide the component code in a markdown format, including file content for each file.
            """
        )
        existing_components = list(ui_components.keys())
        component_details = f"Component Details: {component}"

        message = prompt.format_messages(
            component=component,
            existing_components=existing_components,
            component_details=component_details
        )
        response = groq_llm.invoke(message)

        #logging.info(response)
        # Parse the response and update ui_components and ui_dependencies
        component_code = parse_component_code(response.content)
        ui_components[component] = component_code
        ui_dependencies[component] = detect_dependencies(component_code)["components"]
    
    # Update the state with the newly generated components and dependencies
    state.ui_components = ui_components
    state.ui_dependencies = ui_dependencies

    # Call the save_generated_files function to persist the generated UI components to disk
    save_generated_files(state)

    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
    logging.info(" generate_ui_components: success! ")
    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")

    return {"ui_components": ui_components, "ui_dependencies": ui_dependencies}

"""
    Generates Angular API integration code and updates GraphState.

    Args:
        state (GraphState): The GraphState object containing project details and API specifications.

    Returns:
        GraphState: The updated GraphState object with generated API integration code.
"""
def generate_api_integration(state: GraphState):
    """Generates Angular API integration code and updates GraphState."""
    # with LangChainTracer("generate_api_integration",project_name="AI-Frontend-Generation11223") as run:

    api_endpoints = state.api_endpoints or []
    logging.info(api_endpoints)

    if not api_endpoints:
        return state
    
    generated_services = {}
    for endpoint in api_endpoints:
        prompt = ChatPromptTemplate.from_template(
            """Generate an Angular service for API endpoint: {endpoint}.
            Use HttpClientModule for API integration, implement error handling, and state management for responses.
            {endpoint_details}

            Provide the service code in a markdown format, including file content.
            """
        )

        endpoint_details = f"Endpoint Details: {endpoint}" # Add any specific endpoint details here.

        message = prompt.format_messages(endpoint=endpoint, endpoint_details=endpoint_details)
        response = groq_llm.invoke(message)
        generated_services["endpoint"] = response.content

    # Update GraphState with generated services
    state.api_services = generated_services # add api_services to graph state.

    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
    #logging.info(state)
    logging.info(" generate_api_integration: success! ")
    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")

    return state

"""
    Generates Cypress UI tests for the generated components.

    Args:
        state (GraphState): The GraphState object containing generated components and project details.

    Returns:
        GraphState: The updated GraphState object with generated Cypress test files.
"""
def generate_ui_tests(state: GraphState):
    """Generates Cypress UI tests for the generated components."""
    # with LangChainTracer("generate_ui_tests",project_name="AI-Frontend-Generation11223") as run:
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
        response = groq_llm.invoke(message)
        new_tests[component] = response.content

    ui_tests.update(new_tests)

    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
    #logging.info(ui_tests)
    logging.info(" generate_ui_tests: success! ")
    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")

    return {"ui_tests": ui_tests}

"""
    Generates a Dockerfile for the Angular frontend project and updates GraphState.

    Args:
        state (GraphState): The GraphState object containing project information.

    Returns:
        GraphState: The updated GraphState object with the Dockerfile content.
"""
def generate_frontend_dockerfile(state: GraphState): #(analysis_results, ui_components):
    """Generates a Dockerfile for the Angular frontend project and updates GraphState."""
    # with LangChainTracer("generate_frontend_dockerfile",project_name="AI-Frontend-Generation11223") as run:

    analysis_results = {
        "ui_components": state.ui_components.keys() if state.ui_components else [],
        "state_management": state.state_management,
        "api_endpoints": state.api_endpoints,
        "accessibility": "WCAG guidelines",
        "styling": "Material UI with custom theme"
    }
    ui_components = state.ui_components

    prompt = ChatPromptTemplate.from_template(
        """Generate a Dockerfile for an Angular frontend project.
        Use Node.js for building and Nginx for serving the application.
        Ensure best practices for Dockerfile creation.
        {project_details}

        Provide the Dockerfile content in a markdown format.
        """
    )

    project_details = f"Project Details: {analysis_results}, Components: {list(ui_components.keys()) if ui_components else []}"

    message = prompt.format_messages(project_details=project_details)
    try:
        response = groq_llm.invoke(message)
        state.dockerfile_content = response.content 
    except Exception as e:
        logging.error(f"Error generating Dockerfile: {e}")
        state.dockerfile_content = ""

    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
    #logging.info(state)
    logging.info(" generate_frontend_dockerfile: success! ")
    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")

    return state

"""
    Save UI components, API services, and tests to appropriate project directories.

    Args:
        graph_state (GraphState): The GraphState object containing the generated files.

    Returns:
        GraphState: The updated GraphState object.
"""
def save_generated_files(graph_state): 
    """Save UI components, API services, and tests to appropriate project directories.""" 
    # with LangChainTracer("save_generated_files",project_name="AI-Frontend-Generation11223") as run:

    #base_path = "project_root/src/app"
    base_path = "src/app"
    # Save UI components
    for component, files in (graph_state.ui_components or {}).items():
        component_path = os.path.join(base_path, "components", component)
        os.makedirs(component_path, exist_ok=True)
        for file_name, content in files.items():
            file_path = os.path.join(component_path, file_name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    # Save API services
    service_path = os.path.join(base_path, "services")
    os.makedirs(service_path, exist_ok=True)
    for endpoint, service_code in (graph_state.api_services or {}).items():
        file_name = endpoint.replace("/", "_").strip("_") + ".service.ts"
        file_path = os.path.join(service_path, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(service_code)

    # Save UI tests
    #test_path = "project_root/tests"
    test_path = "tests"
    os.makedirs(test_path, exist_ok=True)
    for component, test_code in (graph_state.ui_tests or {}).items():
        file_name = f"{component}.spec.ts"
        file_path = os.path.join(test_path, file_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(test_code)

    # Save Dockerfile
    #dockerfile_path = "project_root/Dockerfile"
    dockerfile_path = "Dockerfile"
    with open(dockerfile_path, "w", encoding="utf-8") as f:
        f.write(graph_state.dockerfile_content or "")


    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
    logging.info(" save_generated_files: success! ")
    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")

"""
    Generates a Mermaid diagram locally using the Mermaid CLI.

    Args:
        mermaid_syntax (str): The Mermaid syntax string.

    Returns:
        str or None: The file path to the generated PNG diagram, or None if an error occurs.
"""
# pip install mermaid.cli
def draw_mermaid_png_local(mermaid_syntax):
    """Generates a Mermaid diagram locally using the Mermaid CLI."""
    # with LangChainTracer("draw_mermaid_png_local",project_name="AI-Frontend-Generation11223") as run:

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
        img.save("project_root"+ "/" + "langgraph_workflow_local.png")


        logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
        logging.info(" draw_mermaid_png_local: success! ")
        logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")

        return image_bytes
    except subprocess.CalledProcessError as e:
        print(f"Error generating Mermaid diagram: {e}")
        return None
    
"""
    Generates a graph visualization of the LangGraph workflow.

    Args:
        workflow (StateGraph): The LangGraph workflow object.

    Returns:
        None: Displays the graph visualization using matplotlib.
"""
def generate_workflow_visualization(workflow):
    """Generates a graph visualization of the LangGraph workflow."""
    # with LangChainTracer("generate_workflow_visualization",project_name="AI-Frontend-Generation11223") as run:

    """Generates a graph visualization of the LangGraph workflow."""
    try:
        if not hasattr(workflow, "nodes") or not hasattr(workflow, "edges"):
            print("Error: The provided workflow does not have 'nodes' or 'edges'.")
            return

        if not workflow.nodes:
            print("Warning: The workflow has no nodes to visualize.")
            return

        # Create a NetworkX directed graph
        graph = nx.DiGraph()

        # Add nodes
        graph.add_nodes_from(workflow.nodes)

        # Add edges
        graph.add_edges_from(workflow.edges)

        # Visualize using Matplotlib
        pos = nx.kamada_kawai_layout(graph)  # Alternative: nx.spring_layout(graph)
        plt.figure(figsize=(10, 6))
        nx.draw(graph, pos, with_labels=True, node_size=3000, node_color="skyblue", font_size=10, font_weight="bold")

        output_file="project_root" + "/" + "langgraph_workflow.png"
        # Save visualization
        with BytesIO() as buffer:
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            img = Image.open(buffer)
            img.save(output_file)

        print(f"LangGraph workflow visualization generated: {output_file}")
        plt.close()  # Prevent memory leaks

    except Exception as e:
        print(f"Error generating LangGraph visualization: {e}")
        logging.error(f"Error generating LangGraph visualization: {e}")

    logging.info("\n" + "\n" + "=================================================" + "\n" + "\n")
    logging.info("generate_workflow_visualization: success!")
    logging.info("\n" + "=" * 50 + "\n")


"""
    Generates project documentation using Groq LLM.

    Args:
        state (GraphState): The current state of the workflow graph.

    Returns:
        GraphState: The updated state of the workflow graph.
"""
def generate_documentation(state: GraphState):
    """Generates project documentation using Groq LLM."""
    # Generate code comments (conceptual)
    # This would involve parsing the generated code and adding comments using LLM.

    # with LangChainTracer("generate_documentation",project_name="AI-Frontend-Generation11223") as run:
    analysis_results = {
        "ui_components": state.ui_components.keys() if state.ui_components else [],
        "state_management": state.state_management,
        "api_endpoints": state.api_endpoints,
        "accessibility": "WCAG guidelines",
        "styling": "Material UI with custom theme"
    }
    ui_components = state.ui_components

    workspace_path: str = f"project_root"
    project_details:str = f"Project Details: {analysis_results}, Components: {list(ui_components.keys()) if ui_components else []}" # Add project details here.

    # Generate README.md
    readme_prompt = ChatPromptTemplate.from_template(
        """if not in {workspace_path}, first, change the current directory to the workspace folder using the following command:
            cd {workspace_path}

        Then generate a README.md file for an Angular frontend project after cd to the workspace folder.
        Include setup instructions, usage guidelines, and project structure details.
        {project_details}

        Provide the README.md content in a markdown format.
        """
    )

    readme_message = readme_prompt.format_messages(project_details=project_details, workspace_path=workspace_path)
    readme_content = groq_llm.invoke(readme_message).content

    try:
        #with open(workspace_path + "/" +  "README.md", "w") as f:
        with open("README.md", "w") as f:
            f.write(readme_content)
    except Exception as e:
        pass
    print("README.md generated.")

    # Generate component documentation
    for component, code in ui_components.items():
        component_prompt = ChatPromptTemplate.from_template(
            """if not in {workspace_path}, first, change the current directory to the workspace folder using the following command:
            cd {workspace_path}

            Then, generate documentation for the following Angular component: {component}.
            Include props, states, API integration details, and usage examples.
            {component_code}

            Provide the component documentation in a markdown format.
            """
        )

        component_message = component_prompt.format_messages(workspace_path=workspace_path,component=component, component_code=code)
        component_content = groq_llm.invoke(component_message).content

        try:
            #with open(f"{workspace_path} + '/' + {component}.md", "w") as f:
            with open(f"{component}.md", "w") as f:
                f.write(component_content)
        except Exception as e:
            pass
        print(f"Component documentation generated: {component}.md")

    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
    logging.info(" generate_documentation: success! ") #print("Code comments generation (conceptual).")
    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
    

"""
    Validates the generated UI code using Groq LLM.

    Args:
        generated_code: The generated UI code.
        srs_content: The software requirements specification content.
        screenshot_details: Details about the screenshot (e.g., description, file path).

    Returns:
        str: The validation results from the LLM, or None if an error occurs.
"""
def validate_ui(generated_code, srs_content, screenshot_details):
    """Validates the generated UI code using Groq LLM."""

    prompt = ChatPromptTemplate.from_template(
        """Given the following generated UI code: {generated_code}, SRS document: {srs_content}, and screenshot details: {screenshot_details},
        validate the UI requirements and design specifications.
        Identify any discrepancies, inconsistencies, or potential issues.
        Provide a detailed report of the validation results.
        """
    )

    message = prompt.format_messages(generated_code=generated_code, srs_content=srs_content, screenshot_details=screenshot_details)
    response = groq_llm.invoke(message)

    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
    logging.info(" validate_ui: success! ") 
    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")

    return response.content  # Return the validation report

"""
    Creates a StateGraph representing the workflow for frontend generation.

    Returns:
        StateGraph: A StateGraph object representing the workflow.
"""
def create_graph():
    workflow = StateGraph(GraphState) 
    #workflow.add_edge("analyze_screenshot", START)
    workflow.add_node("analyze_screenshot", analyze_screenshot)
    workflow.add_node("analyze_srs", analyze_srs)
    workflow.add_node("generate_angular_setup", generate_angular_setup)
    workflow.add_node("execute_angular_setup", execute_angular_setup)
    workflow.add_node("generate_ui_components", generate_ui_components)
    workflow.add_node("generate_api_integration", generate_api_integration)
    workflow.add_node("generate_ui_tests", generate_ui_tests)
    workflow.add_node("generate_frontend_dockerfile", generate_frontend_dockerfile)
    workflow.add_node("validate_ui", validate_ui)
    workflow.add_node("generate_documentation", generate_documentation)
    workflow.add_node("save_generated_files", save_generated_files)
    workflow.add_node("deploy_frontend", deploy_frontend)
    #workflow.add_node("END", lambda state: GraphState(state.state_id)) 

    # Define edges
    workflow.add_edge("analyze_screenshot", "analyze_srs")
    workflow.add_edge("analyze_srs", "generate_angular_setup")
    workflow.add_edge("generate_angular_setup", "execute_angular_setup")
    workflow.add_edge("execute_angular_setup", "generate_ui_components")
    workflow.add_edge("generate_ui_components", "generate_api_integration")
    workflow.add_edge("generate_api_integration", "generate_ui_tests")
    workflow.add_edge("generate_ui_tests", "generate_frontend_dockerfile")
    workflow.add_edge("generate_frontend_dockerfile", "validate_ui")
    workflow.add_edge("validate_ui", "generate_documentation")
    workflow.add_edge("generate_documentation", "save_generated_files")
    workflow.add_edge("save_generated_files", "deploy_frontend")
    #workflow.add_edge("deploy_frontend", END)
    
    workflow.set_entry_point("analyze_screenshot") # add entry point
    #workflow.set_finish_point(END) # add finish point

    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")
    logging.info(" create_graph: success! ") 
    logging.info("\n" + "\n" + "=================================================" +"\n" +"\n")

    # Return the created StateGraph object.
    return workflow #.compile()




# Example usage (assuming analysis_results from the previous step)
analysis_results = {
    "ui_components": ["login-form", "signup-form", "button", "modal", "form"],
    "state_management": "NgRx",
    "api_endpoints": ["/users", "/auth"],
    "accessibility": "WCAG guidelines",
    "styling": "Material UI with custom theme",
}

ui_components = {
    "login-form": {"login-form.component.ts": "...", "login-form.component.html": "..."},
    "signup-form": {"signup-form.component.ts": "...", "signup-form.component.html": "..."},
}

# Example:
#setup_commands = generate_angular_setup(analysis_results)
#print("Generated Setup Commands:\n", setup_commands)

# Example: 
#generated_components = generate_ui_components(analysis_results)
#for component, code in generated_components.items():
#    print(f"Generated Component: {component}\n", code)

# Example usage (assuming analysis_results from the previous step)
#generated_services = generate_api_integration(analysis_results)
#for endpoint, code in generated_services.items():
 #   print(f"Generated Service: {endpoint}\n", code)

# Example usage (assuming analysis_results and generated_components from the previous steps)
#generated_tests = generate_ui_tests(analysis_results, generated_components)
#for component, test in generated_tests.items():
#    print(f"Generated Test: {component}\n", test)

# Example: 
#dockerfile_content = generate_frontend_dockerfile(analysis_results, ui_components)
#print("Generated Dockerfile:\n", dockerfile_content)

# Example: Execute the commands (be cautious when executing generated commands) # Uncomment below when ready
#execute_angular_setup(setup_commands)

# Example usage (in your LangGraph workflow):
# validation_report = validate_ui(graph_state.ui_components, graph_state.srs_content, graph_state.screenshot_details)
# logging.info(f"UI Validation Report: {validation_report}")

# # Example usage (assuming you have SRS content and screenshot URL)
graph_state = GraphState() 

#srs_content = """
# The application should have a dashboard with a table displaying user data. Users should be able to filter and sort the data.
# There should be a form to add new users. The application should use a REST API for data fetching.
# """

srs_content = """
Software Requirements Document (SRD)
1. Overview
This document outlines the requirements for the frontend development of three microservices/applications within the DNA ecosystem: Dashboard, LMS (Leave Management System), and PODs. The focus is on UI/UX design, API contracts for integration, and overall frontend development guidelines.

2. UI/UX Design Guidelines
2.1 Color Scheme
    • Primary Color: #007bff (Blue - for primary actions)
    • Secondary Color: #6c757d (Gray - for secondary actions)
    • Background Color: #f8f9fa (Light Gray - for application background)
    • Success Color: #28a745 (Green - for success messages)
    • Error Color: #dc3545 (Red - for error messages)
2.2 Typography
    • Font Family: "Inter", sans-serif
    • Heading Font Size: 24px (Bold)
    • Subheading Font Size: 18px (Medium)
    • Body Text Size: 16px (Regular)
    • Button Text Size: 14px (Bold)
2.3 Components
    • Buttons: Rounded corners (8px), filled for primary actions, outlined for secondary actions.
    • Cards: Shadow (box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1)) with padding (16px).
    • Modals: Centered popups with a semi-transparent background.
    • Forms: Input fields with a border radius of 5px and padding of 10px.

3. Application Features
3.1 Dashboard
    • Displays multiple tiles reflecting highlights from various applications.
    • Each tile fetches real-time data from APIs.
    • Users can customize which tiles appear on their dashboard.
API Contract
Fetch Dashboard Data
Request:
GET /api/dashboard
Headers: { Authorization: Bearer <token> }
Response:
{
  "tiles": [
    { "id": "1", "title": "Leave Summary", "content": "10 leaves remaining" },
    { "id": "2", "title": "Pod Members", "content": "3 active members" }
  ]
}

3.2 LMS (Leave Management System)
General User Features
    • Apply for leave.
    • View granted leaves.
    • Check available leave balance.
Manager Features
    • Approve/reject leave requests.
    • View team leave history.
API Contract
Apply for Leave
Request:
POST /api/lms/leave/apply
Headers: { Authorization: Bearer <token> }
Body:
{
  "startDate": "2025-03-15",
  "endDate": "2025-03-18",
  "reason": "Family event"
}
Response:
{
  "message": "Leave request submitted successfully",
  "status": "pending"
}
Approve Leave (Manager Only)
Request:
POST /api/lms/leave/approve
Headers: { Authorization: Bearer <token> }
Body:
{
  "leaveId": "12345",
  "status": "approved"
}
Response:
{
  "message": "Leave request approved",
  "status": "approved"
}

3.3 PODs
    • Managers can add employees to a pod.
    • Employees can view their pod details.
    • Employees can recommend other employees to join their pod.
API Contract
View Pod Details
Request:
GET /api/pods/details
Headers: { Authorization: Bearer <token> }
Response:
{
  "podId": "56789",
  "podName": "Innovation Team",
  "members": [
    { "id": "1", "name": "John Doe", "role": "Lead Developer" },
    { "id": "2", "name": "Jane Smith", "role": "UI/UX Designer" }
  ]
}
Recommend an Employee for a Pod
Request:
POST /api/pods/recommend
Headers: { Authorization: Bearer <token> }
Body:
{
  "podId": "56789",
  "recommendedUserId": "3"
}
Response:
{
  "message": "Recommendation sent successfully"
}

4. Authentication & Authorization
    • Users authenticate via JWT-based login.
    • Role-based access control (RBAC) to differentiate between managers and employees.
API Contract
Login
Request:
POST /api/auth/login
Body:
{
  "email": "user@example.com",
  "password": "securepassword"
}
Response:
{
  "token": "jwt-token-here",
  "user": { "id": "1", "role": "manager" }
}
Fetch Current User
Request:
GET /api/auth/me
Headers: { Authorization: Bearer <token> }
Response:
{
  "id": "1",
  "name": "John Doe",
  "role": "manager"
}

6. Deployment & Hosting Considerations
    • Frontend Framework: Angular with Angular with Material UI.
    • Hosting: Vercel, Netlify, or S3 with CloudFront.
    • CI/CD: GitHub Actions or GitLab CI/CD for automated deployment.

7. Conclusion
This document provides frontend implementation guidelines, UI/UX specifications, API contracts, and integration details for Dashboard, LMS, and PODs applications. 
"""

# screenshot_url = MEDIA_PATH + "Screenshot 2025-03-10 113424.png" #"Test2.png" # Replace with your screenshot URL

# # Calls analyze_screenshot to get screenshot details.
# screenshot_details = analyze_screenshot(screenshot_url) 

# if screenshot_details.get("screenshot_details", {}).get("error"):
#      logging.error("Screenshot Analysis Error: %s", screenshot_details["error"])
# else:
#      logging.info(screenshot_details)
#      # Calls analyze_srs with the SRS content and screenshot details.
#      analysis_results = analyze_srs(srs_content, screenshot_details)
#      # logging.info("Analysis Results: %s", analysis_results)

# # #Example: LangGraph workflow 
# workflow = create_graph() # from previous steps
# commands = generate_angular_setup(analysis_results)
# execute_angular_setup(commands)
# ui_generation_results = generate_ui_components(graph_state, analysis_results) 
# graph_state.ui_components = ui_generation_results["ui_components"] 
# graph_state.ui_dependencies = ui_generation_results["ui_dependencies"]
# graph_state.api_endpoints = analysis_results["api_endpoints"] 
# graph_state = generate_api_integration(graph_state)
# ui_test_results = generate_ui_tests(graph_state) 
# graph_state.ui_tests = ui_test_results["ui_tests"]
# generate_documentation(graph_state)
# graph_state = generate_frontend_dockerfile(graph_state)
# validation_report = validate_ui(graph_state.ui_components, graph_state.srs_content, graph_state.screenshot_details)
# logging.info(f"UI Validation Report: {validation_report}")
# save_generated_files(graph_state)
# deployment_url = deploy_frontend(graph_state.dockerfile_content)
# # Generate workflow visualization
# generate_workflow_visualization(workflow) # uncomment after creating workflow
# logging.info("Angular project setup complete with UI components, API services, tests, and Dockerfile and deployed at: " + deployment_url)