"""CLI entry point for the evaluation scenario suite."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.llm import OpenAILLMClient

from evals.loader import load_eval_scenarios
from evals.report import write_report
from evals.runner import run_eval_suite


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the triage pipeline evaluation suite against data/sample/tickets.json."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Base path for report files (writes .json and .md). Defaults to data/generated/eval-report-<timestamp>.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Evaluate only the first N scenarios (useful for quick manual runs).",
    )
    args = parser.parse_args(argv)

    scenarios = load_eval_scenarios()
    if args.limit is not None:
        scenarios = scenarios[: args.limit]

    llm_client = OpenAILLMClient()
    run = run_eval_suite(llm_client, scenarios=scenarios)
    json_path, md_path = write_report(run, args.output)

    print(f"Evaluated {len(run.scenario_results)} tickets")
    print(f"Category accuracy: {run.category_accuracy:.1%}")
    print(f"Priority accuracy: {run.priority_accuracy:.1%}")
    print(f"Missing-fields accuracy: {run.missing_fields_accuracy:.1%}")
    print(f"Mismatches: {len(run.mismatches)}")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
