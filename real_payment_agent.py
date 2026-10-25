import os
import sys
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from uagents import Agent, Context
from messages import PaymentRequest, PaymentResponse

# Windows Python 3.13 Fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

payment_agent = Agent(
    name="payment_specialist",
    port=8004,
    seed="travelwright-real-payment-agent-seed",
    endpoint=["http://127.0.0.1:8004/submit"],
)

SYSTEM_PROMPT = """You are Travelwright's Payment & Budget Agent.
Help the user with payment options (UPI, Credit Cards, Cash), budget estimation, and cost tracking for their trip.
Keep it concise, helpful, and clearly state that no real transactions are being processed unless it's a premium booking."""

@payment_agent.on_message(model=PaymentRequest, replies=PaymentResponse)
async def handle_payment_request(ctx: Context, sender: str, msg: PaymentRequest):
    ctx.logger.info(f"Main Agent se request aayi: {msg.user_query}")
    
    # =====================================================================
    # HACKATHON BONUS: Mock Payment Protocol Logic (Monetization Model)
    # =====================================================================
    if "premium" in msg.user_query.lower() or "book" in msg.user_query.lower():
        ctx.logger.info("Initiating Fetch.ai Payment Protocol for premium booking...")
        # Yahan hum mock kar rahe hain ki agent 1 FET token maang raha hai
        payment_status = "🔒 **Payment Protocol Triggered:**\nTo confirm this premium booking, please authorize a transaction of **1.0 FET** from your Fetch wallet."
        await ctx.send(sender, PaymentResponse(recommendations=payment_status))
        return

    # Normal AI Budget calculation logic
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
        # Nudge for the premium feature so judges know it exists
        result += "\n\n*(Tip: To book securely using the Fetch.ai Payment Protocol, just say **'Book my trip'**)*"
    except Exception as e:
        result = f"Error in Payment Agent API call: {e}"

    ctx.logger.info("Main Agent ko payment info wapas bhej rahe hain...")
    await ctx.send(sender, PaymentResponse(recommendations=result))

if __name__ == "__main__":
    try:
        payment_agent.run()
    except KeyboardInterrupt:
        print("\nPayment Agent stopped.")
        