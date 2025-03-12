# run source .env on linux to get the needed environment api keys
from app.services.analysis_service import GROQ_API_KEY
from langchain_groq import ChatGroq

llm = ChatGroq(
    groq_api_key=GROQ_API_KEY,
    model="llama-3.2-11b-vision-preview", #"llama-3.3-70b-versatile", #"mistral-saba-24b" or "llama-3.1-8b-instant",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)

print(llm.invoke("Hello, world!"))
