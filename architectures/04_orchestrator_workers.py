"""
Architecture 04: ORCHESTRATOR-WORKERS
=======================================
A manager that delegates.

Flow: Query → Orchestrator LLM → [Worker 1 | Worker 2 | Worker 3] → Synthesizer → Answer

The number and nature of subtasks are decided at RUNTIME by the Orchestrator.

Use-case: Marketing plan generator.
  - Orchestrator: Reads the goal, breaks it into 3-5 concrete subtasks
  - Workers:      Each worker executes exactly one subtask
  - Synthesizer:  Merges all worker outputs into a cohesive plan
"""

import os
import json
import concurrent.futures
import anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def llm_call(system: str, user: str, max_tokens: int = 512) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": user}],
        system=system,
    )
    return response.content[0].text.strip()


# ── Orchestrator ──────────────────────────────────────────────────────────────

def orchestrate(goal: str) -> list[dict]:
    """
    Ask the orchestrator to break the goal into subtasks.
    Returns a list of {"id": int, "title": str, "instruction": str}.
    """
    raw = llm_call(
        system=(
            "You are a project orchestrator. Break the user's goal into 3-5 independent subtasks. "
            "Return ONLY a JSON array with objects having keys: id (int), title (str), instruction (str). "
            "No markdown, no explanation — pure JSON array."
        ),
        user=f"Goal: {goal}",
        max_tokens=768,
    )

    # Strip markdown code fences if the model wraps the JSON
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    subtasks = json.loads(raw)
    return subtasks


# ── Workers ───────────────────────────────────────────────────────────────────

def worker(subtask: dict) -> dict:
    """Execute a single subtask and return the result alongside its metadata."""
    result = llm_call(
        system=(
            "You are a skilled specialist. Complete the assigned subtask thoroughly "
            "in 3-6 bullet points or a short paragraph."
        ),
        user=subtask["instruction"],
    )
    return {"id": subtask["id"], "title": subtask["title"], "result": result}


# ── Synthesizer ───────────────────────────────────────────────────────────────

def synthesize(goal: str, worker_outputs: list[dict]) -> str:
    sections = "\n\n".join(
        f"### {o['title']}\n{o['result']}" for o in sorted(worker_outputs, key=lambda x: x["id"])
    )
    return llm_call(
        system=(
            "You are a senior consultant. Merge the worker outputs below into one cohesive, "
            "well-structured plan. Use clear headings. Keep it under 400 words."
        ),
        user=f"Original goal: {goal}\n\nWorker outputs:\n{sections}",
        max_tokens=1024,
    )


# ── Pipeline ──────────────────────────────────────────────────────────────────

def orchestrator_workers_pipeline(goal: str) -> str:
    print(f"\n{'='*60}")
    print("ARCHITECTURE 04: ORCHESTRATOR-WORKERS")
    print(f"Goal: {goal}")
    print('='*60)

    print("\n[Orchestrator] Breaking goal into subtasks...")
    subtasks = orchestrate(goal)
    for t in subtasks:
        print(f"  [{t['id']}] {t['title']}")

    print(f"\n[Workers] Executing {len(subtasks)} subtasks in parallel...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(subtasks)) as executor:
        futures = [executor.submit(worker, t) for t in subtasks]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    for r in sorted(results, key=lambda x: x["id"]):
        print(f"\n  Worker {r['id']} – {r['title']}:\n  {r['result'][:150]}...")

    print("\n[Synthesizer] Merging all outputs...")
    plan = synthesize(goal, results)

    print("\n--- FINAL PLAN ---")
    print(plan)
    return plan


if __name__ == "__main__":
    orchestrator_workers_pipeline(
        "Launch a marketing campaign for a new AI-powered productivity app targeting remote teams"
    )
