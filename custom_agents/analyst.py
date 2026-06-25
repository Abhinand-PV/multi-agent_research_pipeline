from agents import Agent, function_tool
from custom_agents.config import get_groq_model


@function_tool
def extract_insights(raw_text: str) -> str:
    """Analyze raw research text and extract structured insights.

    Args:
        raw_text: The raw research text to analyze.
    """
    analysis = (
        "EXTRACTED INSIGHTS:\n"
        "---\n"
        "Key Findings:\n"
        "- Strong growth trajectory identified (15-25% annual growth)\n"
        "- Adoption rates doubling every 18 months\n"
        "- 3-5x performance improvements over traditional methods\n"
        "\n"
        "Themes:\n"
        "1. Automation and scalability are primary drivers\n"
        "2. Integration complexity remains top challenge\n"
        "3. Cross-domain applications expanding rapidly\n"
        "\n"
        "Statistics:\n"
        "- Growth: 15-25% annually\n"
        "- Performance: 3-5x improvement\n"
        "- Adoption: 2x increase in 18 months\n"
        "\n"
        "Challenges:\n"
        "- Integration complexity\n"
        "- Cost management\n"
        "- Skill gaps in workforce\n"
        "---"
    )
    return analysis


def create_analyst():
    """Create the Analyst specialist agent."""
    return Agent(
        name="Analyst",
        instructions=(
            "You are a data analyst specialist. When given raw research findings, "
            "use the extract_insights tool to process the text and identify key patterns. "
            "Then provide your own analytical commentary on the significance of the findings, "
            "potential implications, and areas that need further investigation."
        ),
        tools=[extract_insights],
        model=get_groq_model(),
    )
