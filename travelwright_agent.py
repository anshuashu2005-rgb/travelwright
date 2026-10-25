import os, sys, asyncio
from dotenv import load_dotenv
from uagents_core.contrib.protocols.chat import CardContent

if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"): sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import ChatMessage, ChatAcknowledgement, TextContent, EndSessionContent, chat_protocol_spec
from orchestrator import orchestrate_travel_request

# SAARE 4 AGENTS KE IMPORTS
from messages import FoodRequest, FoodResponse, TransportRequest, TransportResponse, PaymentRequest, PaymentResponse, RouteRequest, RouteResponse

# =================================================================
# MAS DEMO: Agent Addresses
# =================================================================
FOOD_AGENT_ADDRESS = "agent1qf62kvu8ch7v98putrlzkjwyp9pdthyppyjshp2l59mckncwpusawddg5a0"
TRANSPORT_AGENT_ADDRESS = "agent1qy5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k8y5k eight"
PAYMENT_AGENT_ADDRESS = "agent1qggal4uvj3geudgjka9xzxakg5jz49cnljqwr060fgnr3q0ceje7qnky"
ROUTE_AGENT_ADDRESS = "agent1qwpj-fivegdlnmp0azd64mc2gcdyush4x72ztlty32gf7 eightjyg4 eightds9sxt3few3" # NAYA

load_dotenv()
PORT = int(os.getenv("PORT", " eighty01"))
AGENT_SEED = os.getenv("AGENT_SEED", "travelwright-stable-agent-seed-2026")
USE_MAILBOX = os.getenv("AGENT_MAILBOX", "true").strip().lower() in ("true", "1", "yes")

agent = Agent(name="travelwright", seed=AGENT_SEED, port=PORT, mailbox=USE_MAILBOX, network="testnet")
chat_protocol = Protocol(spec=chat_protocol_spec)
conversation_memory, trip_states = {}, {}

def get_trip_state(sender: str) -> dict:
    if sender not in trip_states:
        trip_states[sender] = {"starting_city": None, "destination": None, "travellers": None, "budget_inr": None, "duration_days": None, "duration_nights": None, "travel_dates": None, "interests": []}
    return trip_states[sender]

@chat_protocol.on_message(ChatMessage)
async def handle_chat(ctx: Context, sender: str, msg: ChatMessage):
    await ctx.send(sender, ChatAcknowledgement(acknowledged_msg_id=msg.msg_id))
    user_message = (msg.text() or "").strip()
    if not user_message: return

    history = conversation_memory.setdefault(sender, [])
    trip_state = get_trip_state(sender)
    history.append({"role": "user", "content": user_message})
    history[:] = history[-30:]

    # 1. FOOD
    if any(word in user_message.lower() for word in ["food", "eat", "restaurant", "khana"]):
        await ctx.send(FOOD_AGENT_ADDRESS, FoodRequest(user_query=user_message, trip_context=str(trip_state)))
        await ctx.send(sender, ChatMessage(content=[TextContent(text="I've asked the Food Specialist to look into this!")]))
        return  

    # 2. TRANSPORT
    if any(word in user_message.lower() for word in ["transport", "cab", "taxi", "bus", "train", "flight"]):
        await ctx.send(TRANSPORT_AGENT_ADDRESS, TransportRequest(user_query=user_message, trip_context=str(trip_state)))
        await ctx.send(sender, ChatMessage(content=[TextContent(text="I've asked the Transport Specialist to look into this!")]))
        return  

    # 3. PAYMENT
    if any(word in user_message.lower() for word in ["pay", "payment", "upi", "card", "cash", "budget", "cost"]):
        await ctx.send(PAYMENT_AGENT_ADDRESS, PaymentRequest(user_query=user_message, trip_context=str(trip_state)))
        await ctx.send(sender, ChatMessage(content=[TextContent(text="I've asked the Payment Specialist to handle finances!")]))
        return  

    # 4. ROUTE (NAYA)
    if any(word in user_message.lower() for word in ["route", "map", "itinerary", "direction", "path", "way", "best possible route"]):
        await ctx.send(ROUTE_AGENT_ADDRESS, RouteRequest(user_query=user_message, trip_context=str(trip_state)))
        await ctx.send(sender, ChatMessage(content=[TextContent(text="I've asked the Route Specialist to map this out!")]))
        return  

    try:
        reply = await orchestrate_travel_request(user_message=user_message, history=history, trip_state=trip_state)
        history.append({"role": "assistant", "content": reply})
    except Exception:
        reply = "AI is temporarily unavailable."

    await ctx.send(sender, ChatMessage(content=[TextContent(text=reply)]))

@chat_protocol.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement): pass

@agent.on_message(model=FoodResponse)
async def handle_food_response(ctx: Context, sender: str, msg: FoodResponse): ctx.logger.info(f"Food Result: {msg.recommendations}")
@agent.on_message(model=TransportResponse)
async def handle_transport_response(ctx: Context, sender: str, msg: TransportResponse): ctx.logger.info(f"Transport Result: {msg.recommendations}")
@agent.on_message(model=PaymentResponse)
async def handle_payment_response(ctx: Context, sender: str, msg: PaymentResponse): ctx.logger.info(f"Payment Result: {msg.recommendations}")
@agent.on_message(model=RouteResponse)
async def handle_route_response(ctx: Context, sender: str, msg: RouteResponse): ctx.logger.info(f"Route Result: {msg.recommendations}")

agent.include(chat_protocol, publish_manifest=True)
if __name__ == "__main__": agent.run()