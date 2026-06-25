import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

load_dotenv()


def get_groq_model():
    """Create a Groq-backed model for the OpenAI Agents SDK."""
    groq_client = AsyncOpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )
    return OpenAIChatCompletionsModel(
        model="llama-3.3-70b-versatile",
        openai_client=groq_client,
    )