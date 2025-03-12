from io import BytesIO
import logging
import os
from typing import Any, Dict
from dotenv import load_dotenv
#from groq import Groq
import base64
import json

from langchain_groq import ChatGroq
import requests

from PIL import Image

logging.basicConfig(level=logging.INFO)

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MEDIA_PATH = os.getenv("MEDIA_PATH")

#client = Groq(api_key=GROQ_API_KEY)

groq_llm = ChatGroq(groq_api_key=GROQ_API_KEY,model="llama-3.2-11b-vision-preview", #"llama-3.3-70b-versatile", #"mistral-saba-24b" or "llama-3.1-8b-instant",
                    temperature=0)

def encode_image(screenshot_path):
    screenshot_details:  Dict[str, Any] = {} 
    if not screenshot_path:
        logging.error("Screenshot Path not found.")
        screenshot_details["errors"] = screenshot_details["errors"] or []
        screenshot_details["errors"].append("Screenshot URL not found.")
        return screenshot_details  # Return without changes
    #with open(screenshot_path, "rb") as image_file:
        #return base64.b64encode(image_file.read()).decode("utf-8")
    response = requests.get(screenshot_path, stream=True)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content)).convert("RGB")
    buffered = BytesIO()
    #img.save(buffered, format="JPEG")
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8') #img_base64

def get_image_info(encoded_image):
    response = groq_llm.invoke( #chat.completions.create
        #messages=[
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
    return response.content#choices[0].message.content

# image_paths = [MEDIA_PATH + "Test1.png", MEDIA_PATH + "Test2.png"]
screenshot_paths = ["https://raw.githubusercontent.com/dbarayev/user-dashboard/master/src/assets/screenshot.png", # "https://colorlib.com/wp/wp-content/uploads/sites/2/free-dashboard-templates-1.jpg" 
                    "https://raw.githubusercontent.com/dbarayev/user-dashboard/master/src/assets/screenshot2.png"] 


encoded_images = [encode_image(screenshot_path) for screenshot_path in screenshot_paths]

results = {}
for i, encoded_image in enumerate(encoded_images):
    results[f"image_{i+1}"] = get_image_info(encoded_image)

with open(MEDIA_PATH + "analyzed_images.json", "w") as f:
    json.dump(results, f, indent=4)

print("UI Analysis Saved in " + MEDIA_PATH + "analyzed_images.json")