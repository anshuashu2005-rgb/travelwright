import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_PROMPT = """
You are Travelwright's Food Agent.

Responsibilities:
1. Recommend local dishes and food options.
2. Help users plan meals within their budget.
3. Consider dietary preferences.
4. Estimate a reasonable daily food budget.
5. Suggest criteria for selecting suitable restaurants.

Rules:
- Use the trip details and context provided.
- Do not ask again for information already provided.
- Ask follow-up questions only when essential information
  for the food recommendation is genuinely missing.
- If optional details are missing, provide useful recommendations
  and clearly state your assumptions.
- Live restaurant data and food-ordering APIs are not connected.
- Never invent live prices, ratings, opening hours, or availability.
- Clearly label unverified prices as estimates.
- Never claim to have placed a food order.
- Respond in the user's preferred language.
"""

def _get_client() -> OpenAI:
    api_key = os.getenv("ASI_ONE_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ASI_ONE_API_KEY is missing from environment/.env.")
    base_url = os.getenv("ASI_ONE_BASE_URL", "https://api.asi1.ai/v1").strip().rstrip("/")
    return OpenAI(api_key=api_key, base_url=base_url, timeout=45.0, max_retries=2)

def recommend_food(user_request: str, trip_context: dict = None) -> str:
    client = _get_client()
    context = trip_context or {}

    response = client.chat.completions.create(
        model=os.getenv("ASI_ONE_MODEL", "asi1"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "TRIP CONTEXT:\n"
                    f"{context}\n\n"
                    "USER REQUEST:\n"
                    f"{user_request}\n\n"
                    "Use the supplied trip context. "
                    "Do not repeat questions already answered."
                ),
            },
        ],
        temperature=0.3,
    )
    return (response.choices[0].message.content or "").strip()

if __name__ == "__main__":
    print("=== TRAVELWRIGHT FOOD AGENT ===")
    request = input("\nDescribe your food preferences: ").strip()
    if request:
        try:
            print("\nFood recommendations:\n")
            print(recommend_food(request))
        except Exception as error:
            print(f"Error: {error}")
    else:
        print("Please enter your food preferences.")
        