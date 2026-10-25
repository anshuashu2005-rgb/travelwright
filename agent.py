import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from travelwright_agent import agent

if __name__ == "__main__":
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\nTravelwright agent stopped cleanly by user.")

        