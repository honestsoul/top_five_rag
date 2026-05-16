"""
Architecture 02: ROUTING
=========================
Classify first, specialize after.

Flow: Query → Router LLM → Specialist A / B / C → Answer

Use-case: Customer support system that routes tickets to the right specialist.
  - Router: Classify the query as billing / technical / refund / general
  - Specialist A: Billing expert
  - Specialist B: Technical support expert
  - Specialist C: Refund policy expert
  - Fallback:    General support agent
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def llm_call(system: str, user: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": user}],
        system=system,
    )
    return response.content[0].text.strip()


# ── Router ────────────────────────────────────────────────────────────────────

def router(query: str) -> str:
    """Classify the incoming query into one of four categories."""
    category = llm_call(
        system=(
            "You are a customer support router. "
            "Classify the user's message into EXACTLY one category from this list:\n"
            "  billing | technical | refund | general\n"
            "Reply with only the category word, nothing else."
        ),
        user=query,
    )
    return category.lower().strip()


# ── Specialists ───────────────────────────────────────────────────────────────

SPECIALISTS: dict[str, str] = {
    "billing": (
        "You are a billing specialist. You help customers with invoices, charges, "
        "subscription plans, and payment methods. Be concise and empathetic."
    ),
    "technical": (
        "You are a senior technical support engineer. You diagnose and solve software "
        "bugs, integration issues, and configuration problems. Use clear steps."
    ),
    "refund": (
        "You are a refund policy expert. You explain refund eligibility, timelines, "
        "and initiate refund requests when appropriate. Be clear about policy limits."
    ),
    "general": (
        "You are a friendly general support agent. Answer any question politely "
        "and direct the customer to the right resource when needed."
    ),
}


def specialist_response(category: str, query: str) -> str:
    system_prompt = SPECIALISTS.get(category, SPECIALISTS["general"])
    return llm_call(system=system_prompt, user=query)


# ── Pipeline ──────────────────────────────────────────────────────────────────

def routing_pipeline(query: str) -> str:
    print(f"\n{'='*60}")
    print("ARCHITECTURE 02: ROUTING")
    print(f"Query: {query}")
    print('='*60)

    print("\n[Router] Classifying query...")
    category = router(query)
    print(f"  → Routed to specialist: '{category}'")

    print(f"\n[Specialist: {category.upper()}] Generating answer...")
    answer = specialist_response(category, query)

    print("\n--- ANSWER ---")
    print(answer)
    return answer


if __name__ == "__main__":
    queries = [
        "I was charged twice this month and need help fixing my invoice.",
        "My API integration keeps returning a 401 error even with a valid key.",
        "I bought the wrong plan yesterday, can I get a refund?",
        "What are your business hours?",
    ]
    for q in queries:
        routing_pipeline(q)
        print()
