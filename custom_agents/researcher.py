from agents import Agent, function_tool
from custom_agents.config import get_groq_model


@function_tool
def search_web(query: str) -> str:
    """Search the web for information on a topic.

    Args:
        query: The search query to look up.
    """
    results = [
        {
            "title": f"Research findings on: {query}",
            "snippet": f"Recent studies show significant developments in {query}. "
            f"Experts highlight key trends including automation, scalability, "
            f"and cross-domain applications. Market growth is estimated at 15-25% annually.",
            "source": "Academic Research Database",
        },
        {
            "title": f"Industry report: {query}",
            "snippet": f"Industry leaders report that {query} is transforming workflows. "
            f"Key challenges include integration complexity, cost management, "
            f"and skill gaps. Adoption rates have doubled in the past 18 months.",
            "source": "Industry Analysis Report",
        },
        {
            "title": f"Technical overview: {query}",
            "snippet": f"Technical deep-dive into {query} reveals core components: "
            f"distributed architectures, event-driven processing, and intelligent routing. "
            f"Performance benchmarks show 3-5x improvements over traditional approaches.",
            "source": "Technical Review Journal",
        },
    ]

    output = ""
    for i, result in enumerate(results, 1):
        output += f"\n[{i}] {result['title']}\n"
        output += f"    Source: {result['source']}\n"
        output += f"    {result['snippet']}\n"
    return output


def create_researcher():
    """Create the Researcher specialist agent."""
    return Agent(
        name="Researcher",
        instructions=(
            "You are a research specialist. When given a topic, use the search_web tool "
            "to gather information. Make multiple searches with different angles to get "
            "comprehensive coverage. Compile all findings into a structured summary with "
            "sources cited."
        ),
        tools=[search_web],
        model=get_groq_model(),
    )
