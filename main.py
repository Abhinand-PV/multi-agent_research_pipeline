import asyncio
import time
import sys
from dotenv import load_dotenv
from custom_agents.orchestrator import run_pipeline

# Load environment variables from .env
load_dotenv()


async def main():
    # Accept topic from command line args or prompt the user
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        topic = input("Enter a research topic: ")

    print(f"\nStarting research pipeline for: '{topic}'")
    print("=" * 50)
    print("Orchestrating agents: Researcher -> Analyst -> Writer")
    print("=" * 50)

    start_time = time.time()

    try:
        report = await run_pipeline(topic)
        elapsed = time.time() - start_time

        print(f"\n{'=' * 50}")
        print("RESEARCH REPORT")
        print(f"{'=' * 50}\n")
        print(report)
        print(f"\n{'=' * 50}")
        print(f"Pipeline completed in {elapsed:.1f} seconds")
        print(f"{'=' * 50}")

    except Exception as e:
        print(f"\nError running pipeline: {e}")
        print("If this is a rate limit error, wait a moment and try again.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
