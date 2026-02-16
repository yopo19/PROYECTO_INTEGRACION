from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def get_llm():
    """Returns the configured ChatOpenAI instance."""
    # Ensure OPENAI_API_KEY is set in the environment
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)
