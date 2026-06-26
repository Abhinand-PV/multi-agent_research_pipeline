import asyncio
import re

from agents import Runner

from custom_agents.researcher import create_researcher
from custom_agents.analyst import create_analyst
from custom_agents.writer import create_writer
from custom_agents.judge import create_judge


# -----------------------------
# Configuration
# -----------------------------

MAX_RETRIES = 3
MAX_REVISIONS = 2
QUALITY_THRESHOLD = 4.0

RETRY_ERRORS = [
    "429",
    "503",
    "timeout",
    "connection",
    "temporarily unavailable",
]

ERROR_KEYWORDS = [
    "429",
    "rate limit",
    "quota exceeded",
    "api error",
    "tool failure",
    "traceback",
    "stack trace",
    "exception",
]


# -----------------------------
# Helpers
# -----------------------------

def validate_output(stage: str, text: str):
    """
    Stop the pipeline if an agent returns an obvious error.
    """
    lower = text.lower()

    for keyword in ERROR_KEYWORDS:
        if keyword in lower:
            raise RuntimeError(
                f"{stage} failed because the output contains '{keyword}'."
            )


def parse_judge_score(judge_output: str) -> float:
    match = re.search(r"AVERAGE:\s*([\d.]+)", judge_output)

    if match:
        return float(match.group(1))

    return 0.0


async def run_with_retry(agent, prompt, stage_name):
    """
    Execute one agent with retry logic.
    """

    for attempt in range(MAX_RETRIES):

        try:

            print(f"\n[{stage_name}] Running...")

            result = await Runner.run(
                agent,
                input=prompt,
            )

            output = result.final_output

            validate_output(stage_name, output)

            print(f"[{stage_name}] Complete")

            return output

        except Exception as e:

            error = str(e).lower()

            if any(err in error for err in RETRY_ERRORS):

                wait = 2 ** (attempt + 1)

                print(
                    f"[{stage_name}] Retry {attempt+1}/{MAX_RETRIES} "
                    f"in {wait} seconds..."
                )

                await asyncio.sleep(wait)

            else:
                raise

    raise RuntimeError(f"{stage_name} failed after maximum retries.")


# -----------------------------
# Main Pipeline
# -----------------------------

async def run_pipeline(topic: str):

    researcher = create_researcher()
    analyst = create_analyst()
    writer = create_writer()
    judge = create_judge()

    print("\n========== PIPELINE STARTED ==========")

    # -----------------------------
    # Stage 1
    # -----------------------------

    research = await run_with_retry(
        researcher,
        topic,
        "Research Stage",
    )

    # -----------------------------
    # Stage 2
    # -----------------------------

    analysis = await run_with_retry(
        analyst,
        research,
        "Analysis Stage",
    )

    # -----------------------------
    # Stage 3
    # -----------------------------

    report = await run_with_retry(
        writer,
        f"""
Research

{research}

Analysis

{analysis}
""",
        "Writer Stage",
    )

    # -----------------------------
    # Stage 4
    # -----------------------------

    for revision in range(MAX_REVISIONS):

        print(f"\n[Judge] Review {revision+1}")

        judge_result = await Runner.run(
            judge,
            input=report,
        )

        feedback = judge_result.final_output

        score = parse_judge_score(feedback)

        print(f"[Judge] Score = {score}/5")

        if score >= QUALITY_THRESHOLD:

            print("[Judge] Approved")

            break

        print("[Judge] Revision required")

        report = await run_with_retry(
            writer,
            f"""
Please improve this report.

REPORT

{report}

FEEDBACK

{feedback}
""",
            "Writer Revision",
        )

    print("\n========== PIPELINE FINISHED ==========")

    return report