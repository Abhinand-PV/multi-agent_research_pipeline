"""
Orchestrator — coordinates the four-stage multi-agent research pipeline.

Pipeline flow:
    Stage 1: Researcher  — web search and fact collection
    Stage 2: Analyst     — insight extraction and trend analysis
    Stage 3: Writer      — professional report composition
    Stage 4: Judge       — quality review with optional revision loop
"""

import asyncio
import logging
import re
from collections.abc import Callable

from agents import Agent, Runner

from custom_agents.researcher import create_researcher
from custom_agents.analyst import create_analyst
from custom_agents.writer import create_writer
from custom_agents.judge import create_judge

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pipeline configuration
# ---------------------------------------------------------------------------

MAX_RETRIES = 3          # maximum retry attempts per agent on transient errors
MAX_REVISIONS = 2        # maximum revision cycles before accepting the report
QUALITY_THRESHOLD = 4.0  # minimum average Judge score (out of 5) to approve

# Errors that warrant a retry (transient API/network issues)
RETRY_ERROR_PATTERNS: list[str] = [
    "429",
    "503",
    "timeout",
    "connection error",
    "temporarily unavailable",
    "service unavailable",
]

# Keywords that indicate a genuine pipeline failure in agent output
# Kept narrow to avoid false positives on normal report content.
ERROR_KEYWORDS: list[str] = [
    "429 too many requests",
    "rate limit exceeded",
    "quota exceeded",
    "tool call failed",
    "tool failure",
    "traceback (most recent call last)",
    "research stage failed",
]

# Progress percentages for each pipeline stage
_STAGE_PROGRESS: dict[str, int] = {
    "research": 20,
    "analysis": 45,
    "writing": 70,
    "review_start": 80,
    "review_done": 95,
    "done": 100,
}

# Type alias for the optional progress callback
ProgressCallback = Callable[[str, int], None]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _notify(
    message: str,
    pct: int,
    callback: ProgressCallback | None,
) -> None:
    """Emit a progress update to the logger and optional UI callback."""
    logger.info(message)
    if callback:
        callback(message, pct)


def validate_output(stage: str, text: str) -> None:
    """
    Raise RuntimeError if an agent's output contains a known failure signal.

    Uses exact sub-string matching on lowercased text to avoid false positives
    on common words like 'exception' that may legitimately appear in reports.

    Args:
        stage: Human-readable stage name for the error message.
        text:  The agent output to validate.

    Raises:
        RuntimeError: If a failure keyword is found in the output.
    """
    lower = text.lower()
    for keyword in ERROR_KEYWORDS:
        if keyword in lower:
            raise RuntimeError(
                f"[{stage}] Pipeline error: output contains '{keyword}'."
            )


def parse_judge_score(judge_output: str) -> float:
    """
    Extract the AVERAGE score from a Judge agent response.

    Returns QUALITY_THRESHOLD (pass) when the score cannot be parsed,
    logging a warning so the issue is visible without silently looping.

    Args:
        judge_output: The raw text output from the Judge agent.

    Returns:
        Parsed average score, or QUALITY_THRESHOLD as a safe default.
    """
    match = re.search(r"AVERAGE:\s*([\d.]+)", judge_output)
    if match:
        return float(match.group(1))

    logger.warning(
        "Could not parse Judge score from output. "
        "Defaulting to QUALITY_THRESHOLD (%.1f) to avoid revision loop.",
        QUALITY_THRESHOLD,
    )
    return QUALITY_THRESHOLD


async def run_with_retry(
    agent: Agent,
    prompt: str,
    stage_name: str,
    callback: ProgressCallback | None = None,
    progress_pct: int = 0,
) -> str:
    """
    Execute one agent with exponential-backoff retry on transient errors.

    Args:
        agent:        The Agent instance to run.
        prompt:       Input prompt for the agent.
        stage_name:   Human-readable name used in log messages.
        callback:     Optional progress callback for the UI.
        progress_pct: Progress percentage to report when this stage starts.

    Returns:
        The agent's final output text.

    Raises:
        RuntimeError: After MAX_RETRIES failures or on non-retryable errors.
    """
    for attempt in range(MAX_RETRIES):
        try:
            _notify(f"⚙️  [{stage_name}] Running (attempt {attempt + 1})...", progress_pct, callback)

            result = await Runner.run(agent, input=prompt)
            output: str = result.final_output

            validate_output(stage_name, output)

            logger.info("[%s] Completed successfully.", stage_name)
            return output

        except Exception as exc:
            error_text = str(exc).lower()
            is_retryable = any(pat in error_text for pat in RETRY_ERROR_PATTERNS)

            if is_retryable and attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                logger.warning(
                    "[%s] Retryable error on attempt %d/%d. Waiting %ds. Error: %s",
                    stage_name, attempt + 1, MAX_RETRIES, wait, exc,
                )
                _notify(
                    f"⏳ [{stage_name}] Rate limit hit — retrying in {wait}s...",
                    progress_pct,
                    callback,
                )
                await asyncio.sleep(wait)
            else:
                logger.error("[%s] Non-retryable error: %s", stage_name, exc)
                raise

    raise RuntimeError(f"[{stage_name}] Failed after {MAX_RETRIES} attempts.")


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

async def run_pipeline(
    topic: str,
    progress_callback: ProgressCallback | None = None,
) -> str:
    """
    Execute the full four-stage research pipeline for a given topic.

    Args:
        topic:             The research topic entered by the user.
        progress_callback: Optional callable(message: str, pct: int) for
                           real-time UI progress updates.

    Returns:
        The final approved research report as a Markdown string.
    """
    researcher = create_researcher()
    analyst = create_analyst()
    writer = create_writer()
    judge = create_judge()

    logger.info("========== PIPELINE STARTED — topic: %s ==========", topic)

    # ------------------------------------------------------------------
    # Stage 1 — Research
    # ------------------------------------------------------------------
    _notify("🔎 Stage 1/4 — Researching topic...", 10, progress_callback)
    research = await run_with_retry(
        researcher,
        topic,
        "Research Stage",
        callback=progress_callback,
        progress_pct=_STAGE_PROGRESS["research"],
    )

    # ------------------------------------------------------------------
    # Stage 2 — Analysis
    # ------------------------------------------------------------------
    _notify("📊 Stage 2/4 — Analysing findings...", 35, progress_callback)
    analysis = await run_with_retry(
        analyst,
        research,
        "Analysis Stage",
        callback=progress_callback,
        progress_pct=_STAGE_PROGRESS["analysis"],
    )

    # ------------------------------------------------------------------
    # Stage 3 — Writing
    # ------------------------------------------------------------------
    _notify("✍️  Stage 3/4 — Writing report...", 60, progress_callback)
    writer_prompt = (
        f"Research\n\n{research}\n\n"
        f"Analysis\n\n{analysis}"
    )
    report = await run_with_retry(
        writer,
        writer_prompt,
        "Writer Stage",
        callback=progress_callback,
        progress_pct=_STAGE_PROGRESS["writing"],
    )

    # ------------------------------------------------------------------
    # Stage 4 — Judge review + revision loop
    # ------------------------------------------------------------------
    for revision in range(MAX_REVISIONS + 1):
        review_label = (
            "reviewing report..."
            if revision == 0
            else f"reviewing revision {revision}..."
        )
        _notify(
            f"✅ Stage 4/4 — Judge {review_label}",
            _STAGE_PROGRESS["review_start"],
            progress_callback,
        )
        logger.info("[Judge] Review cycle %d/%d", revision + 1, MAX_REVISIONS + 1)

        judge_result = await Runner.run(judge, input=report)
        feedback = judge_result.final_output

        score = parse_judge_score(feedback)
        logger.info("[Judge] Score = %.2f / 5.0", score)

        if score >= QUALITY_THRESHOLD:
            logger.info("[Judge] Report approved (score %.2f >= %.1f).", score, QUALITY_THRESHOLD)
            _notify(
                f"✅ Report approved by Judge (score: {score:.2f}/5.0)",
                _STAGE_PROGRESS["review_done"],
                progress_callback,
            )
            break

        if revision == MAX_REVISIONS:
            # Exhausted revisions — accept the best report we have
            logger.warning(
                "[Judge] Max revisions reached. Accepting report with score %.2f.", score
            )
            _notify(
                f"⚠️  Max revisions reached — accepting report (score: {score:.2f}/5.0)",
                _STAGE_PROGRESS["review_done"],
                progress_callback,
            )
            break

        logger.info("[Judge] Revision required. Sending feedback to Writer.")
        _notify(
            f"🔄 Revision {revision + 1}/{MAX_REVISIONS} — improving report...",
            _STAGE_PROGRESS["review_start"],
            progress_callback,
        )

        revision_prompt = (
            f"Please improve this report based on the reviewer's feedback.\n\n"
            f"ORIGINAL REPORT\n\n{report}\n\n"
            f"REVIEWER FEEDBACK\n\n{feedback}"
        )
        report = await run_with_retry(
            writer,
            revision_prompt,
            f"Writer Revision {revision + 1}",
            callback=progress_callback,
            progress_pct=_STAGE_PROGRESS["writing"],
        )

    logger.info("========== PIPELINE FINISHED ==========")
    return report