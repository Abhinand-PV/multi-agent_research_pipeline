from agents import Agent
from custom_agents.config import get_groq_model


def create_writer():
    """Create the Writer specialist agent."""
    return Agent(
        name="Writer",
        instructions=(
            "You are a professional technical writer. Given research findings and analysis, "
            "produce a polished markdown research report with the following structure:\n\n"
            "# [Topic] Research Report\n\n"
            "## Executive Summary\n"
            "A 2-3 sentence overview of the key findings.\n\n"
            "## Key Findings\n"
            "Bullet points of the most important discoveries.\n\n"
            "## Analysis\n"
            "A paragraph discussing implications and significance.\n\n"
            "## Challenges and Risks\n"
            "Known obstacles and potential issues.\n\n"
            "## Conclusion\n"
            "A brief forward-looking conclusion.\n\n"
            "Write clearly and concisely. Use data from the research where available."
        ),
        model=get_groq_model(),
    )
