import asyncio
from agents import Agent, Runner
from custom_agents.config import get_groq_model


async def main():
    # Create a simple test agent using Groq
    agent = Agent(
        name="Test Agent",
        instructions="You are a helpful assistant. Respond in one sentence.",
        model=get_groq_model(),
    )
    # Run the agent with a simple prompt
    result = await Runner.run(agent, input="Say hello and confirm you are working!")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())