from agents import Agent, function_tool
from custom_agents.config import get_groq_model


@function_tool
def search_web(query: str) -> str:
    """
    Mock web search tool.

    Replace this with Tavily, SerpAPI, Exa, Brave Search,
    or another real search provider in the future.
    """

    results = [
        {
            "title": f"Overview of {query}",
            "source": "Academic Database",
            "snippet": (
                f"{query} is an actively evolving field with applications "
                "across multiple industries."
            ),
        },
        {
            "title": f"Industry Trends in {query}",
            "source": "Industry Report",
            "snippet": (
                f"Organizations continue adopting {query} to improve "
                "efficiency, scalability, and automation."
            ),
        },
        {
            "title": f"Future of {query}",
            "source": "Technology Review",
            "snippet": (
                f"Experts predict continued innovation, increased adoption, "
                "and new research opportunities."
            ),
        },
    ]

    output = []

    for i, result in enumerate(results, start=1):
        output.append(
            f"""
[{i}] {result['title']}
Source: {result['source']}

{result['snippet']}
"""
        )

    return "\n".join(output)


def create_researcher():

    return Agent(

        name="Researcher",

        instructions="""
You are a Senior Research Specialist.

Your ONLY responsibility is collecting information.

Workflow:

1. Use the search_web tool.
2. Gather all available information.
3. Remove duplicate information.
4. Organize findings clearly.
5. Preserve important facts.
6. Preserve statistics.
7. Preserve dates.
8. Preserve technical terminology.
9. Never invent facts.
10. Never analyze the information.
11. Never summarize beyond what was found.
12. Never write the final report.
13. If search results contain an API error,
    rate limit,
    stack trace,
    tool failure,
    or unrelated content,

    STOP.

Return:

# Research Summary

## Overview

## Important Findings

## Statistics

## Technologies

## Challenges

## Sources

The next agent will perform analysis.
""",

        tools=[search_web],

        model=get_groq_model(),
    )