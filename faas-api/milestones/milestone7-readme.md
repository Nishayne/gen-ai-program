### Milestone 7, focusing on LangSmith logging and debugging. This involves setting up a LangSmith project and integrating logging into the LangGraph workflow

## Setting up LangSmith

* Create an Account: If you don't have one, create an account on LangSmith (langsmith.com).
* Create a Project: Create a new project in LangSmith to track your workflow executions.
* Get API Key: Obtain your LangSmith API key from your LangSmith settings.
* Set Environment Variable: Set the LANGCHAIN_API_KEY environment variable to your LangSmith API key.

##  Integrating LangSmith Logging

## We'll modify the LangGraph workflow to use LangChain's tracing capabilities, which automatically log data to LangSmith.

```bash
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import functional_graph
from langgraph.graph import END
from langgraph.prebuilt import draw_mermaid_png
from PIL import Image
from io import BytesIO
from langchain_community.chat_models import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from langchain.callbacks.tracers.langchain import LangChainTracer
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")

groq_llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY)

# Initialize LangChainTracer -- This initializes the LangChain tracer with your LangSmith project name.
tracer = LangChainTracer(project_name="AI-Frontend-Generation")

# Assuming you have your GraphState and workflow defined as 'workflow'
# Example:
# workflow = create_graph() # from previous steps

# Modify your nodes to use tracer.run()
def generate_ui_components(state):
    with tracer.run("generate_ui_components") as run:
        # ... your component generation logic ...
        # run.log(key="ui_components", value=state.ui_components) # log relevant values
        return {"ui_components": state.ui_components} # return results

def generate_api_integration(state):
    with tracer.run("generate_api_integration") as run:
        # ... your api integration logic ...
        # run.log(key="api_endpoints", value=state.api_endpoints) # log relevant values
        return {"api_endpoints": state.api_endpoints} # return results

def generate_ui_tests(state):
    with tracer.run("generate_ui_tests") as run:
        # ... your ui tests generation logic ...
        # run.log(key="ui_tests", value=state.ui_tests) # log relevant values
        return {"ui_tests": state.ui_tests} # return results

def generate_frontend_dockerfile(state):
    with tracer.run("generate_frontend_dockerfile") as run:
        # ... your docker file generation logic ...
        # run.log(key="dockerfile_content", value=state.dockerfile_content) # log relevant values
        return {"dockerfile_content": state.dockerfile_content} # return results

def generate_documentation(state):
    with tracer.run("generate_documentation") as run:
        # ... your documentation generation logic ...
        # run.log(key="readme_content", value=state.readme_content) # log relevant values
        return {"readme_content": state.readme_content} # return results

# Example of a node using an API call.
import requests
def example_api_node(state):
    with tracer.run("example_api_node") as run:
        api_url = "https://jsonplaceholder.typicode.com/todos/1"
        response = requests.get(api_url)
        run.log(key="api_response", value=response.json())
        return {"api_response": response.json()}

# Example of a node with error handling
def example_error_node(state):
    with tracer.run("example_error_node") as run:
        try:
            result = 1/0
        except Exception as e:
            run.log(key="error", value=str(e))
            return {"error": str(e)}

# Example of logging iterations
def example_iteration_node(state):
    with tracer.run("example_iteration_node") as run:
        state["iterations"] = state.get("iterations", 0) + 1
        run.log(key="iterations", value=state["iterations"])
        return {"iterations": state["iterations"]}

# Example of creating a graph.
# workflow = StateGraph(GraphState)
# workflow.add_node("generate_ui_components", generate_ui_components)
# workflow.add_node("example_api_node", example_api_node)
# workflow.add_node("example_error_node", example_error_node)
# workflow.add_node("example_iteration_node", example_iteration_node)
# workflow.add_edge("generate_ui_components", "example_api_node")
# workflow.add_edge("example_api_node", "example_error_node")
# workflow.add_edge("example_error_node", "example_iteration_node")
# workflow.set_entry_point("generate_ui_components")
# workflow.set_finish_point("example_iteration_node")
# compiled_workflow = workflow.compile()

# Example of running a graph.
# inputs = {"srs_content": "some srs content", "screenshot_details": "some screenshot details"}
# for output in compiled_workflow.stream(inputs):
#     for key, value in output.items():
#         print(f"Node: {key}, Output: {value}")
```
