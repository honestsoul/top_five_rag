# Top 5 Agent Architectures — Hands-On Examples

> Inspired by the **GenAI Architecture Guide 2026** by [@brijpandeyji](https://twitter.com/brijpandeyji)

This project gives you **one runnable Python file per architecture** so you can read the code, run it, and immediately see how each pattern works — no hand-waving, just real LLM calls.

---

## The 5 Architectures

| # | Name | Tagline | File |
|---|------|---------|------|
| 01 | **Prompt Chaining** | One step feeds the next | `architectures/01_prompt_chaining.py` |
| 02 | **Routing** | Classify first, specialize after | `architectures/02_routing.py` |
| 03 | **Parallelization** | Many minds, one answer | `architectures/03_parallelization.py` |
| 04 | **Orchestrator-Workers** | A manager that delegates | `architectures/04_orchestrator_workers.py` |
| 05 | **Evaluator-Optimizer** | Draft, critique, refine | `architectures/05_evaluator_optimizer.py` |

---

## Architecture Details

### 01 — Prompt Chaining
```
Query → LLM Step 1 → Gate Check → LLM Step 2 → Gate Check → LLM Step 3 → Final Output
```
**When to use:** Tasks with a natural sequence where each step depends on the previous output.  
**Demo:** Three-stage blog article pipeline — outline → draft → polished article — with quality gates between steps.

---

### 02 — Routing
```
Query → Router LLM → Specialist A
                   → Specialist B
                   → Specialist C  → Answer
```
**When to use:** Mixed-intent inputs that need different handling per category.  
**Demo:** Customer support router that classifies tickets as `billing`, `technical`, `refund`, or `general`, then sends each to the matching specialist.

---

### 03 — Parallelization
```
Query → LLM Call 1 ──┐
      → LLM Call 2 ──┼→ Aggregator → Final Answer
      → LLM Call 3 ──┘
```
**When to use:** Independent sub-questions that can be answered simultaneously.  
**Demo:** Research assistant that queries advantages, challenges, and future outlook in parallel, then synthesizes a balanced report.

---

### 04 — Orchestrator-Workers
```
Query → Orchestrator LLM → Worker 1 ──┐
                         → Worker 2 ──┼→ Synthesizer → Answer
                         → Worker 3 ──┘
                    (subtasks decided at runtime)
```
**When to use:** Complex goals where the breakdown of work is not known in advance.  
**Demo:** Marketing plan generator — the orchestrator decides the subtasks at runtime, workers execute them in parallel, the synthesizer merges results.

---

### 05 — Evaluator-Optimizer
```
Query → Generator LLM → Draft → Evaluator LLM → if ACCEPT → Final Answer
                    ↑                     |
                    └──────── REJECT ─────┘
                         (loops until quality threshold met)
```
**When to use:** Output quality matters more than latency; you have a measurable acceptance criterion.  
**Demo:** Python function generator with an automated code reviewer that scores each draft 0-10 and loops until score ≥ 7 (or max 3 iterations).

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/honestsoul/top_five_rag.git
cd top_five_rag
pip install -r requirements.txt
```

### 2. Set your API key

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

Or export it directly:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Run all architectures

```bash
python run_all.py
```

### 4. Run a single architecture

```bash
python run_all.py --arch 3          # parallelization only
python run_all.py --arch 1 5        # prompt chaining + evaluator-optimizer
```

### 5. Run an individual file directly

```bash
python architectures/02_routing.py
```

---

## Project Structure

```
top_five_rag/
├── architectures/
│   ├── 01_prompt_chaining.py       # Chained LLM steps with gate checks
│   ├── 02_routing.py               # Router + specialist LLMs
│   ├── 03_parallelization.py       # Concurrent LLM calls + aggregator
│   ├── 04_orchestrator_workers.py  # Dynamic task decomposition + workers
│   └── 05_evaluator_optimizer.py   # Generate-evaluate-refine loop
├── run_all.py                      # Run one or all demos from CLI
├── requirements.txt
├── .env.example
└── README.md
```

---

## Model Used

All examples use **`claude-haiku-4-5-20251001`** — fast and cost-efficient, ideal for learning.  
Swap `MODEL` at the top of any file to use `claude-sonnet-4-6` or `claude-opus-4-7` for higher-quality output.

---

## Key Takeaways

| Architecture | Best for | Main trade-off |
|---|---|---|
| Prompt Chaining | Sequential, dependent steps | Latency adds up per step |
| Routing | Mixed-intent traffic | Router errors cascade |
| Parallelization | Independent sub-tasks | Cost scales with # of calls |
| Orchestrator-Workers | Unknown task structure | Orchestrator quality is critical |
| Evaluator-Optimizer | High-stakes output quality | May loop; set a max iteration cap |

---

*Built with the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)*
