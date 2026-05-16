"""
Architecture 03: PARALLELIZATION
==================================
Many minds, one answer.

Flow: Query → [LLM Call 1 | LLM Call 2 | LLM Call 3] → Aggregator → Final Answer

Use-case: Research assistant that investigates a topic from three angles simultaneously,
          then merges everything into one balanced report.
  - LLM Call 1: Advantages / benefits
  - LLM Call 2: Challenges / drawbacks
  - LLM Call 3: Recent developments & future outlook
  - Aggregator: Synthesize all three into a structured report
"""

import os
import concurrent.futures
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


# ── Worker callables (run in parallel) ───────────────────────────────────────

def analyze_advantages(topic: str) -> str:
    return llm_call(
        system="You are a research analyst. List 3-5 key advantages or benefits. Be concise.",
        user=f"What are the main advantages of: {topic}",
    )


def analyze_challenges(topic: str) -> str:
    return llm_call(
        system="You are a critical analyst. List 3-5 key challenges or drawbacks. Be concise.",
        user=f"What are the main challenges or drawbacks of: {topic}",
    )


def analyze_future(topic: str) -> str:
    return llm_call(
        system="You are a technology forecaster. Describe recent developments and future outlook in 3-5 points.",
        user=f"What are the recent developments and future outlook for: {topic}",
    )


# ── Aggregator ────────────────────────────────────────────────────────────────

def aggregate(topic: str, advantages: str, challenges: str, future: str) -> str:
    combined = (
        f"TOPIC: {topic}\n\n"
        f"ADVANTAGES:\n{advantages}\n\n"
        f"CHALLENGES:\n{challenges}\n\n"
        f"FUTURE OUTLOOK:\n{future}"
    )
    return llm_call(
        system=(
            "You are a senior research editor. Synthesize the three sections below into a "
            "single, well-structured report with the headings: Overview, Advantages, "
            "Challenges, and Future Outlook. Keep it under 300 words."
        ),
        user=combined,
    )


# ── Pipeline ──────────────────────────────────────────────────────────────────

def parallelization_pipeline(topic: str) -> str:
    print(f"\n{'='*60}")
    print("ARCHITECTURE 03: PARALLELIZATION")
    print(f"Topic: {topic}")
    print('='*60)

    print("\n[Parallel] Running 3 LLM calls simultaneously...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        future_adv = executor.submit(analyze_advantages, topic)
        future_chl = executor.submit(analyze_challenges, topic)
        future_fut = executor.submit(analyze_future, topic)

        advantages = future_adv.result()
        challenges = future_chl.result()
        future_out = future_fut.result()

    print("\n[LLM 1 – Advantages]\n" + advantages)
    print("\n[LLM 2 – Challenges]\n" + challenges)
    print("\n[LLM 3 – Future]\n" + future_out)

    print("\n[Aggregator] Synthesizing into final report...")
    report = aggregate(topic, advantages, challenges, future_out)

    print("\n--- FINAL REPORT ---")
    print(report)
    return report


if __name__ == "__main__":
    parallelization_pipeline("Large Language Models in enterprise software")
