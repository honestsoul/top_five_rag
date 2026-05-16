"""
Run all five agent architecture examples in sequence.
Set ANTHROPIC_API_KEY in your environment or in a .env file before running.

Usage:
    python run_all.py
    python run_all.py --arch 1        # run only architecture 01
    python run_all.py --arch 3 4      # run architectures 03 and 04
"""

import argparse
import sys

from architectures.01_prompt_chaining      import prompt_chaining_pipeline
from architectures.02_routing              import routing_pipeline
from architectures.03_parallelization      import parallelization_pipeline
from architectures.04_orchestrator_workers import orchestrator_workers_pipeline
from architectures.05_evaluator_optimizer  import evaluator_optimizer_pipeline

DEMOS = {
    1: (
        prompt_chaining_pipeline,
        "The impact of AI agents on software development in 2026",
    ),
    2: (
        routing_pipeline,
        "I was charged twice this month and need help fixing my invoice.",
    ),
    3: (
        parallelization_pipeline,
        "Large Language Models in enterprise software",
    ),
    4: (
        orchestrator_workers_pipeline,
        "Launch a marketing campaign for a new AI-powered productivity app targeting remote teams",
    ),
    5: (
        evaluator_optimizer_pipeline,
        "a function that safely parses a JSON string and returns a default value if parsing fails",
    ),
}


def main():
    parser = argparse.ArgumentParser(description="Run Top-5 Agent Architecture demos")
    parser.add_argument(
        "--arch",
        nargs="+",
        type=int,
        choices=list(DEMOS.keys()),
        help="Which architecture(s) to run (1-5). Default: all.",
    )
    args = parser.parse_args()

    targets = args.arch if args.arch else list(DEMOS.keys())

    for num in targets:
        fn, demo_input = DEMOS[num]
        try:
            fn(demo_input)
        except Exception as exc:
            print(f"\n[ERROR] Architecture {num:02d} failed: {exc}", file=sys.stderr)

    print("\n\nAll selected architectures completed.")


if __name__ == "__main__":
    main()
