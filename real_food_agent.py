import os
import sys
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from uagents import Agent, Context
from messages import FoodRequest, FoodResponse
FOOD_AGENT_ADDRESS = "agent1qf62kvu8ch7v98putrlzkjwyp9pdthyppyjshp2l59mckncwpusawddg5a0"

# Windows Python 3.13 Fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

food_agent = Agent(
    name="food_specialist",
    port=8002,
    seed="travelwright-real-food-agent-seed",
    endpoint=["http://127.0.0.1:8002/submit"],
)

SYSTEM_PROMPT = """You are Travelwright's Food Agent.
Recommend local dishes and food options based on the user's query.
Keep it concise and helpful."""

@food_agent.on_message(model=FoodRequest, replies=FoodResponse)
async def handle_food_request(ctx: Context, sender: str, msg: FoodRequest):
    ctx.logger.info(f"Main Agent se request aayi: {msg.user_query}")
    
    try:
        api_key = os.getenv("ASI_ONE_API_KEY", "").strip()
        client = AsyncOpenAI(api_key=api_key, base_url="https://api.asi1.ai/v1")
        
        prompt = f"TRIP CONTEXT: {msg.trip_context}\n\nUSER QUERY: {msg.user_query}"
        
        response = await client.chat.completions.create(
            model="asi1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3
        )
        result = response.choices[0].message.content.strip()
    except Exception as e:
        result = f"Error in Food Agent API call: {e}"

    ctx.logger.info("Main Agent ko recommendations wapas bhej rahe hain...")
    await ctx.send(sender, FoodResponse(recommendations=result))

if __name__ == "__main__":
    try:
        food_agent.run()
    except KeyboardInterrupt:
        print("\nFood Agent stopped.")