import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_PROMPT = """
You are Travelwright's Finance & Budgeting Agent.

Your responsibilities:
1. Create realistic travel budget breakdowns (Transport, Accommodation, Food,
   Local Commute/Activities, and Emergency Buffer).
2. Evaluate whether the user's target budget (in INR or specified currency) is
   realistic for the destination, duration, and number of travelers.
3. Provide per-person and total trip cost estimates.
4. Suggest practical cost-saving trade-offs if the budget is tight.

Rules:
- All costs must be clearly marked as estimates.
- Never claim to check live ticket or hotel prices.
- Never initiate payments or claim a booking was paid.
- Respect the total trip budget provided in the context.
- Respond in the user's language.
"""


def _get_client() -> OpenAI:
    api_key = os.getenv("ASI_ONE_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ASI_ONE_API_KEY is missing from environment/.env.")
    base_url = os.getenv("ASI_ONE_BASE_URL", "https://api.asi1.ai/v1").strip().rstrip("/")
    return OpenAI(api_key=api_key, base_url=base_url, timeout=45.0, max_retries=2)


def plan_budget(user_request: str, trip_context: dict = None) -> str:
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
    print("  TRAVELWRIGHT - FINANCE & BUDGET AGENT")
    print("=" * 45)
    request = input("\nDescribe your trip budget question: ").strip()
    if not request:
        print("Please enter your budget details.")
    else:
        print("\nCalculating budget breakdown...\n")
        try:
            print(plan_budget(request))
        except Exception as error:
            print(f"Error: {error}")
            