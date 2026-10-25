import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_PROMPT = """
You are Travelwright's Accommodation Agent.

Your responsibilities:
1. Help users choose hotels, hostels, guesthouses, and budget stays.
2. Consider destination, dates, number of guests, budget, location,
   amenities, and accessibility requirements.
3. Compare accommodation types and explain their trade-offs.
4. Recommend a reasonable accommodation budget for the trip.

Rules:
- Live hotel inventory and booking APIs are not connected yet.
- Never invent current prices, ratings, reviews, or room availability.
- Label prices as estimates when they are not verified.
- Never claim to have reserved or booked a room.
- Never initiate payments.
- Ask concise questions when essential trip details are missing.
- Respond in the user's language.
"""


def _get_client() -> OpenAI:
    api_key = os.getenv("ASI_ONE_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ASI_ONE_API_KEY is missing from environment/.env.")
    base_url = os.getenv("ASI_ONE_BASE_URL", "https://api.asi1.ai/v1").strip().rstrip("/")
    return OpenAI(api_key=api_key, base_url=base_url, timeout=45.0, max_retries=2)


def find_accommodation(user_request: str, trip_context: dict = None) -> str:
    client = _get_client()
    context = trip_context or {}
    user_content = (
        f"TRIP CONTEXT:\n{context}\n\nUSER REQUEST:\n{user_request}"
        if context
        else user_request
    )

    response = client.chat.completions.create(
        model=os.getenv("ASI_ONE_MODEL", "asi1"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        temperature=0.3,
    )
    return (response.choices[0].message.content or "").strip()


if __name__ == "__main__":
    print("=" * 45)
    print("  TRAVELWRIGHT - ACCOMMODATION AGENT")
    print("=" * 45)
    request = input("\nDescribe your stay requirements: ").strip()
    if not request:
        print("Please enter your accommodation requirements.")
    else:
        print("\nFinding suitable accommodation options...\n")
        try:
            print(find_accommodation(request))
        except Exception as error:
            print(f"Error: {error}")
            