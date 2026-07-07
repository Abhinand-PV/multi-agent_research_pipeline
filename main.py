"""
CLI entry point for the Multi-Agent Research Pipeline.

Usage:
    python main.py "your research topic"
    python main.py                        # prompts for input
"""

import asyncio
import logging
import sys
import time

from dotenv import load_dotenv

load_dotenv()

# Configure logging for CLI output
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

from custom_agents.orchestrator import run_pipeline  # noqa: E402


async def main() -> None:
    """Run the research pipeline from the command line."""
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter a research topic: ").strip()

    if not topic:
        print("Error: topic cannot be empty.", file=sys.stderr)
        sys.exit(1)

    print(f"\n{'=' * 60}")
    print(f"  Multi-Agent Research Pipeline")
    print(f"  Topic: {topic}")
    print(f"{'=' * 60}\n")

    start_time = time.time()

    def cli_progress(message: str, pct: int) -> None:
        print(f"[{pct:3d}%] {message}")

    try:
        report = await run_pipeline(topic, progress_callback=cli_progress)
        elapsed = time.time() - start_time

        print(f"\n{'=' * 60}")
        print("  RESEARCH REPORT")
        print(f"{'=' * 60}\n")
        print(report)
        print(f"\n{'=' * 60}")
        print(f"  Pipeline completed in {elapsed:.1f} seconds")
        print(f"{'=' * 60}\n")

    except Exception as exc:
        logger.exception("Pipeline failed.")
        print(f"\nError: {exc}", file=sys.stderr)
        print("If this is a rate limit error, wait a moment and try again.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
