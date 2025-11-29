from langchain_google_genai import ChatGoogleGenerativeAI
from crewai import LLM
import os

def get_llm():
    return LLM(
        model="gemini/gemini-2.0-flash",
        api_key=os.environ.get('GOOGLE_API_KEY'),
        temperature=0.7
    )
