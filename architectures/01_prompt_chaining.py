"""
Architecture 01: PROMPT CHAINING
=================================
One step feeds the next.

Flow: Query → LLM Step 1 → Gate Check → LLM Step 2 → Gate Check → LLM Step 3 → Final Output

Use-case: Writing a blog article in structured stages.
  - Step 1: Generate an outline
  - Gate:   Outline must have at least 3 sections
  - Step 2: Write a draft from the outline
  - Gate:   Draft must be at least 200 words
  - Step 3: Polish and format the draft
  - Output: Publish-ready article
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
        max_tokens=1024,
        messages=[{"role": "user", "content": user}],
        system=system,
    )
    return response.content[0].text.strip()


# ── Gate checks ──────────────────────────────────────────────────────────────

def gate_outline(outline: str) -> tuple[bool, str]:
    """Reject if the outline has fewer than 3 numbered sections."""
    sections = [l for l in outline.splitlines() if l.strip() and l.strip()[0].isdigit()]
    if len(sections) < 3:
        return False, f"Outline only has {len(sections)} section(s); need at least 3."
    return True, "OK"


def gate_draft(draft: str) -> tuple[bool, str]:
    """Reject if the draft is shorter than 200 words."""
    word_count = len(draft.split())
    if word_count < 200:
        return False, f"Draft is only {word_count} words; need at least 200."
    return True, "OK"


# ── Pipeline ─────────────────────────────────────────────────────────────────

def prompt_chaining_pipeline(topic: str) -> str:
    print(f"\n{'='*60}")
    print("ARCHITECTURE 01: PROMPT CHAINING")
    print(f"Topic: {topic}")
    print('='*60)

    # ── Step 1: Outline ──────────────────────────────────────────
    print("\n[Step 1] Generating outline...")
    outline = llm_call(
        system="You are a content strategist. Produce a numbered outline with at least 4 sections.",
        user=f"Create a blog article outline for: {topic}",
    )
    print(outline)

    passed, reason = gate_outline(outline)
    if not passed:
        raise ValueError(f"Gate 1 FAILED: {reason}")
    print(f"\n✓ Gate 1 passed")

    # ── Step 2: Draft ────────────────────────────────────────────
    print("\n[Step 2] Writing draft...")
    draft = llm_call(
        system="You are a blog writer. Write a thorough draft (at least 250 words) following the outline exactly.",
        user=f"Write a blog draft based on this outline:\n\n{outline}",
    )
    print(draft[:300] + "..." if len(draft) > 300 else draft)

    passed, reason = gate_draft(draft)
    if not passed:
        raise ValueError(f"Gate 2 FAILED: {reason}")
    print(f"\n✓ Gate 2 passed ({len(draft.split())} words)")

    # ── Step 3: Polish ───────────────────────────────────────────
    print("\n[Step 3] Polishing final article...")
    final = llm_call(
        system=(
            "You are a senior editor. Fix grammar, improve flow, add a compelling title "
            "and a one-sentence conclusion. Return only the polished article."
        ),
        user=f"Polish this draft:\n\n{draft}",
    )

    print("\n--- FINAL OUTPUT ---")
    print(final)
    return final


if __name__ == "__main__":
    prompt_chaining_pipeline("The impact of AI agents on software development in 2026")
