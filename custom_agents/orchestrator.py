import asyncio
import re
from agents import Agent, Runner
from custom_agents.config import get_groq_model
from custom_agents.researcher import create_researcher
from custom_agents.analyst import create_analyst
from custom_agents.writer import create_writer


def create_orchestrator():
    """Create the Orchestrator agent with specialists as tools."""
    researcher = create_researcher()
    analyst = create_analyst()
    writer = create_writer()

    orchestrator = Agent(
        name="Research Pipeline Orchestrator",
        instructions=(
            "You manage a research pipeline. For any given topic:\n"
            "1. Call research_topic to gather comprehensive information\n"
            "2. Call analyze_findings with the research results to extract insights\n"
            "3. Call write_report with both the research and analysis to produce the final report\n\n"
            "Always follow this sequence. Pass the full output from each step to the next. "
            "Return the final report from the writer as your output."
        ),
        tools=[
            researcher.as_tool(
                tool_name="research_topic",
                tool_description="Research a topic by searching for information from multiple sources. Pass the topic as input.",
            ),
            analyst.as_tool(
                tool_name="analyze_findings",
                tool_description="Analyze raw research findings to extract key insights, themes, and statistics. Pass the research text as input.",
            ),
            writer.as_tool(
                tool_name="write_report",
                tool_description="Write a polished markdown research report from research findings and analysis. Pass the combined research and analysis as input.",
            ),
        ],
        model=get_groq_model(),
    )
    return orchestrator
async def run_pipeline(topic: str, max_retries: int = 3) -> str:
    """Run the full research pipeline for a given topic with retry logic."""
    orchestrator = create_orchestrator()

    for attempt in range(max_retries):
        try:
            result = await Runner.run(
                orchestrator,
                input=f"Research the following topic and produce a comprehensive report: {topic}",
                max_turns=10,
            )
            return result.final_output
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                wait_time = 2 ** (attempt + 1)
                print(f"[Rate Limit] Attempt {attempt + 1}/{max_retries}. Waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise

    raise RuntimeError("Max retries exceeded due to rate limiting.")
