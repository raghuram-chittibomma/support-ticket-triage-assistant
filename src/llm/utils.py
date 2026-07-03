"""Small shared helpers for parsing raw LLMClient text completions. See classifier.py and
response_drafter.py, both of which ask the model for a JSON object and need to tolerate
minor formatting deviations.
"""

import re


def strip_markdown_code_fence(raw: str) -> str:
    """Models sometimes wrap JSON in ```json ... ``` despite instructions not to; strip it."""
    stripped = raw.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```[a-zA-Z]*\n?", "", stripped)
        stripped = re.sub(r"\n?```$", "", stripped)
    return stripped.strip()
