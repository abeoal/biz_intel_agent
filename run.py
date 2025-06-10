# run.py

import asyncio
from orchestrator.agent1_pipeline import run_agent1_pipeline
# from orchestrator.agent3_pipeline import run_agent3_pipeline
# from orchestrator.agent4_pipeline import run_agent4_pipeline

async def main():
    """
    Main entry point for starting all desired pipelines/agents.
    """
    print("Starting Business Intelligence Agent System...")

    # Start Agent 1 (News Fetching & Cleanup)
    # This will run continuously in the background
    agent1_task = asyncio.create_task(run_agent1_pipeline())

    # You can start other agents here as you implement them
    # For example:
    # agent3_task = asyncio.create_task(run_agent3_pipeline())
    # agent4_task = asyncio.create_task(run_agent4_pipeline())

    # Keep the main loop running
    # You might want a more sophisticated way to manage tasks in a real system,
    # but for now, just waiting on the primary fetcher is sufficient.
    await agent1_task
    # await agent3_task
    # await agent4_task

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("System stopped by user (Ctrl+C).")
    except Exception as e:
        print(f"An unexpected error occurred in the main system: {e}")