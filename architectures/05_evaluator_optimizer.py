"""
Architecture 05: EVALUATOR-OPTIMIZER
======================================
Draft, critique, refine.

Flow: Query → Generator LLM → Draft → Evaluator LLM → if ACCEPT → Final Answer
                                  ↑                        |
                                  └──────── REJECT ────────┘
                                       (loops until quality threshold met)

Use-case: Python function generator with automated quality review.
  - Generator: Writes a Python function for the given task
  - Evaluator: Scores it on correctness, edge-case handling, and style (0-10)
               Returns ACCEPT (score ≥ 7) or REJECT with actionable feedback
  - Loop:      Max 3 iterations to stay within budget
"""

import os
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"
MAX_ITERATIONS = 3
ACCEPT_THRESHOLD = 7

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def llm_call(system: str, user: str, max_tokens: int = 1024) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": user}],
        system=system,
    )
    return response.content[0].text.strip()


# ── Generator ─────────────────────────────────────────────────────────────────

def generate(task: str, feedback: str = "") -> str:
    extra = f"\n\nPrevious feedback to address:\n{feedback}" if feedback else ""
    return llm_call(
        system=(
            "You are an expert Python developer. Write clean, well-named Python code. "
            "Include a brief docstring and handle common edge cases."
        ),
        user=f"Write a Python function for: {task}{extra}",
    )


# ── Evaluator ─────────────────────────────────────────────────────────────────

def evaluate(task: str, code: str) -> tuple[str, int, str]:
    """
    Returns (verdict, score, feedback).
    verdict is 'ACCEPT' or 'REJECT'.
    """
    raw = llm_call(
        system=(
            "You are a strict code reviewer. Evaluate the Python function below on:\n"
            "  1. Correctness – does it solve the task?\n"
            "  2. Edge cases  – does it handle None, empty input, type errors?\n"
            "  3. Style       – clear names, docstring, no dead code?\n\n"
            f"Score from 0-10. ACCEPT if score >= {ACCEPT_THRESHOLD}, else REJECT.\n\n"
            "Reply in this exact format (no extra text):\n"
            "VERDICT: <ACCEPT|REJECT>\n"
            "SCORE: <0-10>\n"
            "FEEDBACK: <one paragraph of specific, actionable feedback>"
        ),
        user=f"Task: {task}\n\nCode:\n{code}",
        max_tokens=512,
    )

    verdict_match = re.search(r"VERDICT:\s*(ACCEPT|REJECT)", raw, re.IGNORECASE)
    score_match   = re.search(r"SCORE:\s*(\d+)",             raw)
    feedback_match = re.search(r"FEEDBACK:\s*(.+)",           raw, re.DOTALL)

    verdict  = verdict_match.group(1).upper()  if verdict_match  else "REJECT"
    score    = int(score_match.group(1))        if score_match    else 0
    feedback = feedback_match.group(1).strip()  if feedback_match else raw

    return verdict, score, feedback


# ── Pipeline ──────────────────────────────────────────────────────────────────

def evaluator_optimizer_pipeline(task: str) -> str:
    print(f"\n{'='*60}")
    print("ARCHITECTURE 05: EVALUATOR-OPTIMIZER")
    print(f"Task: {task}")
    print('='*60)

    feedback = ""
    draft = ""

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n[Iteration {iteration}] Generating draft...")
        draft = generate(task, feedback)
        print(draft)

        print(f"\n[Evaluator] Reviewing draft {iteration}...")
        verdict, score, feedback = evaluate(task, draft)
        print(f"  Verdict : {verdict}")
        print(f"  Score   : {score}/10")
        print(f"  Feedback: {feedback[:200]}{'...' if len(feedback) > 200 else ''}")

        if verdict == "ACCEPT":
            print(f"\n✓ ACCEPTED on iteration {iteration}")
            break
        else:
            print(f"\n✗ REJECTED — refining with feedback...")

    print("\n--- FINAL OUTPUT ---")
    print(draft)
    return draft


if __name__ == "__main__":
    evaluator_optimizer_pipeline(
        "a function that safely parses a JSON string and returns a default value if parsing fails"
    )
