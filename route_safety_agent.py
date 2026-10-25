import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_PROMPT = """
You are Travelwright's Route and Safety Agent.

Your responsibilities:
1. Explain possible travel routes between the user's locations.
2. Discuss transport options and approximate journey durations.
3. Identify practical travel precautions and common safety considerations.
4. Help travelers plan sensible departure times.
5. Consider accessibility and traveler-specific requirements when provided.

Important rules:
- You do not have live maps, traffic, or location tracking yet.
- Never present unverified routes, journey times, or safety conditions as live facts.
- Clearly label estimates and general guidance.
- Do not claim to have checked live traffic or verified current conditions.
- Ask for the starting point and destination if either is missing.
- Respond in the user's language.
"""


def _get_client() -> OpenAI:
    api_key = os.getenv("ASI_ONE_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ASI_ONE_API_KEY is missing from environment/.env.")
    base_url = os.getenv("ASI_ONE_BASE_URL", "https://api.asi1.ai/v1").strip().rstrip("/")
    return OpenAI(api_key=api_key, base_url=base_url, timeout=45.0, max_retries=2)


def analyze_route(user_request: str, trip_context: dict = None) -> str:
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
    print("  TRAVELWRIGHT - ROUTE & SAFETY AGENT")
    print("=" * 45)
    request = input("\nEnter your route request: ").strip()
    if not request:
        print("Please enter a route request.")
    else:
        print("\nAnalyzing route and safety considerations...\n")
        try:
            print(analyze_route(request))
        except Exception as error:
            print(f"Error: {error}")
            