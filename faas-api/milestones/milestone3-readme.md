### Milestone 3, focusing on autonomous UI generation, API integration, and testing/debugging workflows using LLMs.
## UI Component Generation (Using Groq LLM)
```bash
from langchain_community.chat_models import ChatGroq
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_llm = ChatGroq(temperature=0, groq_api_key=GROQ_API_KEY)

def generate_ui_components(analysis_results):
    """Generates Angular UI components based on analysis results."""

    ui_components = analysis_results.get("ui_components", [])
    if not ui_components:
        return {}

    generated_components = {}
    for component in ui_components:
        prompt = ChatPromptTemplate.from_template(
            """Generate an Angular component for: {component}.
            Follow best practices: component-based architecture, accessibility, styling consistency, modular design.
            Use TypeScript, SCSS, and Angular Material themes if applicable.
            {component_details}

            Provide the component code in a markdown format, including file content for each file.
            """
        )

        component_details = f"Component Details: {component}" # Add any specific component details here.

        message = prompt.format_messages(component=component, component_details=component_details)
        response = groq_llm(message)
        generated_components[component] = response.content

    return generated_components

# Example usage (assuming analysis_results from the previous step)
analysis_results = {
    "ui_components": ["button", "modal", "form"],
    "state_management": "NgRx",
    "api_endpoints": ["/users", "/auth"],
    "accessibility": "WCAG guidelines",
    "styling": "Material UI with custom theme",
}

generated_components = generate_ui_components(analysis_results)
for component, code in generated_components.items():
    print(f"Generated Component: {component}\n", code)

```

##  API Integration (Using Groq LLM)]
```bash
def generate_api_integration(analysis_results):
    """Generates Angular API integration code."""

    api_endpoints = analysis_results.get("api_endpoints", [])
    if not api_endpoints:
        return {}

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
        response = groq_llm(message)
        generated_services[endpoint] = response.content

    return generated_services

# Example usage (assuming analysis_results from the previous step)
generated_services = generate_api_integration(analysis_results)
for endpoint, code in generated_services.items():
    print(f"Generated Service: {endpoint}\n", code)
```

## UI Testing (Using Groq LLM)
```bash
def generate_ui_tests(analysis_results, generated_components):
    """Generates Cypress UI tests for the generated components."""

    tests = {}
    for component, code in generated_components.items():
        prompt = ChatPromptTemplate.from_template(
            """Generate Cypress UI tests for the following Angular component: {component}.
            Ensure proper unit tests, integration tests, and end-to-end tests.
            {component_code}

            Provide the test code in a markdown format, including file content.
            """
        )

        message = prompt.format_messages(component=component, component_code=code)
        response = groq_llm(message)
        tests[component] = response.content

    return tests

# Example usage (assuming analysis_results and generated_components from the previous steps)
generated_tests = generate_ui_tests(analysis_results, generated_components)
for component, test in generated_tests.items():
    print(f"Generated Test: {component}\n", test)
```
