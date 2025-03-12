## Milestone 1, Focus on implementing the "Analysis" milestone. This involves creating an AI workflow using LangChain and LangGraph 
## to analyze the SRS document and UI screenshots, extracting the necessary details for frontend generation.

from langchain_groq import ChatGroq
# or
# from langchain_groq.chat_models import ChatGroq
# from langchain_community.chat_models import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from dotenv import load_dotenv
import os
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage
#from langchain_openai import ChatOpenAI
from PIL import Image
import requests
from io import BytesIO
import base64
import os
from dotenv import load_dotenv
import logging
from app.services.common_service import GraphState;

logging.basicConfig(level=logging.INFO)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
MEDIA_PATH = os.getenv("MEDIA_PATH")

groq_llm = ChatGroq(groq_api_key=GROQ_API_KEY,model="llama-3.2-11b-vision-preview", #"llama-3.3-70b-versatile", #"mistral-saba-24b" or "llama-3.1-8b-instant",
                    temperature=0)

"""
Takes the SRS content and screenshot details as input.
Uses a ChatPromptTemplate to create a prompt for the LLM.
Defines ResponseSchema for structured output parsing.
Uses StructuredOutputParser to parse the LLM response.
Returns a dictionary containing extracted information.
"""
def analyze_srs(srs_content: str, screenshot_details:  Dict[str, Any]):
    """Analyzes the SRS document and screenshot details, using Groq LLM, saving results to GraphState."""

    analysis_results:  Dict[str, Any] = {}

    if not srs_content or not screenshot_details:
        logging.error("SRS content or screenshot details not found in GraphState.")
        return analysis_results  # Return empty

    srs_prompt = ChatPromptTemplate.from_template(
        """Analyze the following SRS document: {srs_content} and screenshot details: {screenshot_details}.
        Extract UI components, state management, API endpoints, accessibility, and styling.
        {format_instructions}"""
    )

    response_schemas = [
        ResponseSchema(name="ui_components", description="List of UI components"),
        ResponseSchema(name="state_management", description="State management requirements"),
        ResponseSchema(name="api_endpoints", description="API endpoints and responses"),
        ResponseSchema(name="accessibility", description="UI accessibility requirements"),
        ResponseSchema(name="styling", description="Styling and branding guidelines"),
    ]
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = output_parser.get_format_instructions()

    srs_message = srs_prompt.format_messages(srs_content=srs_content, screenshot_details=screenshot_details, format_instructions=format_instructions)
    srs_response = groq_llm.invoke(srs_message) # llm(srs_message) #groq_llm(message)

    try:
        parsed_data = output_parser.parse(srs_response.content)

        # print("parsed_data... ")
        # print(parsed_data)

        # Update GraphState with parsed data
        analysis_results["ui_components"] = parsed_data.get("ui_components")
        analysis_results["state_management"] = parsed_data.get("state_management")
        analysis_results["api_endpoints"] = parsed_data.get("api_endpoints")
        analysis_results["accessibility"] = parsed_data.get("accessibility")
        analysis_results["styling"] = parsed_data.get("styling")

    except Exception as e:
        logging.error(f"Parsing Error: {e}")
        analysis_results.errors = analysis_results.errors or []
        analysis_results.errors.append(f"SRS Analysis Parsing Error: {e}")

    # print(analysis_results)\
    
    # Return analysis results
    # return {"ui_components": ["button", "form"], "state_management": "NgRx"} # Example data
    return analysis_results

def encode_image(screenshot_path):
    with open(MEDIA_PATH + screenshot_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_info(encoded_image):
    response = groq_llm.invoke( 
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract UI components, design language, and layout details from this image."},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}},
                ],
            }
        ],
        model="llama-3.2-11b-vision-preview",
    )
    return response.content

"""
Takes the screenshot local file path as input.
Encodes the image as a base64 string.
Creates a prompt for Llama 3 Vision (Groq) with the image and text.
Sends the prompt to the Groq LLM.
Returns the response content (design details).
Handles potential errors during image fetching or processing.
"""
def analyze_screenshot(screenshot_path: str):
    """Analyzes a screenshot using Llama 3 Vision (Groq)."""
    screenshot_details:  Dict[str, Any] = {} 
    if not screenshot_path:
        logging.error("Screenshot Path not found.")
        screenshot_details["errors"] = screenshot_details["errors"] or []
        screenshot_details["errors"].append("Screenshot Path not found.")
        return screenshot_details  # Return without changes

    try:
        img_base64 = encode_image(screenshot_path)

        message = get_image_info(img_base64)
        
        screenshot_details["screenshot_details"] = {"description": message}  
        logging.info(f"Screenshot processing response: {message}")
    except Exception as e:
        screenshot_details["screenshot_details"] = {"error": f"Error processing screenshot: {e}"}
        logging.exception(f"Error processing screenshot: {e}")
        screenshot_details["errors"] = screenshot_details["errors"] or []
        screenshot_details["errors"].append(f"Groq LLM Error: {e}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching screenshot: {e}")
        screenshot_details["screenshot_details"] = {"error": f"Error fetching screenshot: {e}"}
        screenshot_details["errors"] = screenshot_details["errors"] or []
        screenshot_details["errors"].append(f"Request Error: {e}")

    return screenshot_details 

# screenshot_path = MEDIA_PATH + "Test1.png" #" MEDIA_PATH + "Test2.png"
# print(analyze_screenshot(screenshot_path))
