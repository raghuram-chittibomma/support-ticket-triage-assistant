"""Record an evaluation baseline snapshot under evals/baselines/."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

from src.config import settings
from src.llm import OpenAILLMClient

from evals.fixture_llm import PerScenarioScriptedLLM
from evals.loader import load_eval_scenarios
from evals.report import format_markdown_report, write_report
from evals.runner import run_eval_suite

_BASELINES_DIR = Path(__file__).resolve().parent / "baselines"


def _prepend_metadata(md_body: str, *, lines: list[str]) -> str:
    header = "\n".join(lines) + "\n\n"
    return header + md_body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Record an eval baseline under evals/baselines/ (fixture or live OpenAI)."
    )
    parser.add_argument(
        "--mode",
        choices=("fixture", "live"),
        required=True,
        help="fixture = scripted LLM (reproducible, no API key); live = OpenAILLMClient.",
    )
    parser.add_argument(
        "--tag",
        default="v0.1.0",
        help="Release tag folder name, e.g. v0.1.0 (default).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Base path for .json/.md (default: evals/baselines/<tag>/<mode>-baseline).",
    )
    args = parser.parse_args(argv)

    if args.mode == "live" and not settings.openai_api_key:
        print("OPENAI_API_KEY is required for --mode live (set in .env or environment)", file=sys.stderr)
        return 1

    recorded_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    output_base = args.output or (_BASELINES_DIR / args.tag / f"{args.mode}-baseline")

    llm_client = PerScenarioScriptedLLM() if args.mode == "fixture" else OpenAILLMClient()
    run = run_eval_suite(llm_client, scenarios=load_eval_scenarios())
    json_path, md_path = write_report(run, output_base)

    meta_lines = [
        f"<!-- baseline-mode: {args.mode} -->",
        f"<!-- recorded-at: {recorded_at} -->",
        f"<!-- tag: {args.tag} -->",
    ]
    if args.mode == "live":
        meta_lines.append(f"<!-- openai-model: {settings.openai_model} -->")

    md_path.write_text(
        _prepend_metadata(format_markdown_report(run), lines=meta_lines),
        encoding="utf-8",
    )

    print(f"Mode: {args.mode}")
    print(f"Recorded: {recorded_at}")
    print(f"Category accuracy: {run.category_accuracy:.1%}")
    print(f"Priority accuracy: {run.priority_accuracy:.1%}")
    print(f"Missing-fields accuracy: {run.missing_fields_accuracy:.1%}")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
