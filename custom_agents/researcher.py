"""
Researcher agent — Stage 1 of the multi-agent research pipeline.

Uses DuckDuckGo to perform real web searches and organises findings
into a structured Research Summary for the Analyst to process.
"""

import logging
from duckduckgo_search import DDGS
from agents import Agent, function_tool
from custom_agents.config import get_groq_model

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Search tool
# ---------------------------------------------------------------------------

@function_tool
def search_web(query: str) -> str:
    """
    Search the web using DuckDuckGo and return structured results.

    Performs up to three targeted queries to gather broad coverage
    of the topic, then formats results for the Researcher agent.

    Args:
        query: The search query string.

    Returns:
        Formatted string of search results with titles, URLs, and snippets.
    """
    queries = [
        query,
        f"{query} overview applications",
        f"{query} challenges future trends",
    ]

    all_results: list[dict] = []
    seen_urls: set[str] = set()

    with DDGS() as ddgs:
        for q in queries:
            try:
                hits = ddgs.text(q, max_results=4)
                for hit in hits:
                    url = hit.get("href", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        all_results.append(hit)
            except Exception as exc:
                logger.warning("DuckDuckGo query failed for '%s': %s", q, exc)

    if not all_results:
        return (
            "No search results found. "
            "The topic may be too narrow or the search service is temporarily unavailable."
        )

    lines: list[str] = []
    for i, result in enumerate(all_results[:12], start=1):
        title = result.get("title", "Untitled")
        url = result.get("href", "N/A")
        snippet = result.get("body", "No description available.")
        lines.append(
            f"[{i}] {title}\n"
            f"Source: {url}\n"
            f"{snippet}\n"
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Agent factory
# ---------------------------------------------------------------------------

def create_researcher() -> Agent:
    """Create and return the Researcher specialist agent."""

    return Agent(
        name="Researcher",
        instructions="""
You are a Senior Research Specialist.

Your ONLY responsibility is collecting information from the provided search results.

Workflow:

1. Use the search_web tool with the given topic.
2. Read every result carefully.
3. Remove duplicate information.
4. Organise findings clearly under the sections below.
5. Preserve all important facts, statistics, dates, and technical terms exactly as found.
6. Never invent facts or statistics.
7. Never perform analysis — that belongs to the Analyst.
8. Never write the final report — that belongs to the Writer.
9. If search results contain an API error, rate limit, stack trace, tool failure,
   or completely unrelated content, STOP and report the issue clearly.

Return EXACTLY this Markdown structure:

# Research Summary

## Overview
(What is this topic? Define it concisely.)

## Important Findings
(Key facts and discoveries from the search results.)

## Statistics & Data
(Any numbers, percentages, dates, or measurable data found.)

## Technologies & Methods
(Specific tools, platforms, techniques, or methodologies mentioned.)

## Challenges
(Problems, limitations, or barriers identified in the sources.)

## Sources
(List each source as: [n] Title — URL)

The next agent will perform analysis on this output.
""",
        tools=[search_web],
        model=get_groq_model(temperature=0.2),
    )