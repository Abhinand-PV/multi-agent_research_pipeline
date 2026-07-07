"""
Configuration module for the multi-agent research pipeline.

Model and inference settings are controlled via environment variables
so they can be changed without modifying source code.
"""

import os
from openai import AsyncOpenAI
from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------

# Override via GROQ_MODEL env var. Available Groq models:
#   llama-3.1-8b-instant   — fastest, lowest cost (default)
#   llama-3.3-70b-versatile — best quality, higher latency
#   llama3-70b-8192         — alternative 70B option
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.1-8b-instant")

# Groq API base URL
GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def get_groq_model(temperature: float = 0.3) -> OpenAIChatCompletionsModel:
    """
    Create a Groq-backed model for the OpenAI Agents SDK.

    Args:
        temperature: Sampling temperature. Lower = more deterministic.
                     Recommended: 0.1–0.3 for factual agents, 0.5–0.7 for writing.
    """
    groq_client = AsyncOpenAI(
        api_key=os.environ.get("GROQ_API_KEY"),
        base_url=GROQ_BASE_URL,
    )
    return OpenAIChatCompletionsModel(
        model=GROQ_MODEL,
        openai_client=groq_client,
    )