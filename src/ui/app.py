"""Gradio demo UI for the Support Ticket Triage Assistant. See #24 and
docs/01_architecture/ARCHITECTURE.md 'UI layer'.

v0.1 wiring choice (documented in ARCHITECTURE.md): the UI calls
`run_triage_pipeline()` in-process rather than the FastAPI `/triage` endpoint.
This keeps the demo to a single `python -m src.ui` command with no separate
uvicorn process, while the HTTP API remains available for programmatic clients
and integration tests.
"""

from typing import Callable

import gradio as gr
from pydantic import ValidationError

from src.llm import MissingAPIKeyError
from src.schemas import TicketInput, TriageResult
from src.ui.formatting import format_triage_result
from src.workflows import run_triage_pipeline

TriageRunner = Callable[[TicketInput], TriageResult]


def build_ticket_input(
    subject: str,
    body: str,
    product_sku: str,
    customer_persona: str,
    channel: str,
) -> TicketInput:
    """Build and validate a `TicketInput` from the UI form fields."""
    payload: dict = {"subject": subject.strip(), "body": body.strip()}
    if product_sku.strip():
        payload["product_sku"] = product_sku.strip()
    if customer_persona.strip():
        payload["customer_persona"] = customer_persona.strip()
    if channel.strip():
        payload["channel"] = channel.strip()
    return TicketInput.model_validate(payload)


def triage_from_form(
    subject: str,
    body: str,
    product_sku: str,
    customer_persona: str,
    channel: str,
    *,
    run_pipeline: TriageRunner = run_triage_pipeline,
) -> str:
    """Validate the form, run triage, and return Markdown for the output panel."""
    if not subject.strip():
        return "**Error:** Subject is required."
    if not body.strip():
        return "**Error:** Body is required."

    try:
        ticket = build_ticket_input(subject, body, product_sku, customer_persona, channel)
    except ValidationError as exc:
        return f"**Validation error:** {exc.errors()[0]['msg']}"

    try:
        result = run_pipeline(ticket)
    except MissingAPIKeyError as exc:
        return (
            f"**Configuration error:** {exc}\n\n"
            "Set `OPENAI_API_KEY` in your environment or `.env` file (see `.env.example`) "
            "and restart the UI."
        )
    except Exception as exc:
        return (
            f"**Unexpected error while triaging this ticket:** {exc}\n\n"
            "Check the server logs for details."
        )

    return format_triage_result(result)


def build_demo() -> gr.Blocks:
    with gr.Blocks(title="NorthPeak Audioworks — Ticket Triage") as demo:
        gr.Markdown(
            "# Support Ticket Triage Assistant\n"
            "Paste a customer ticket below and click **Triage ticket** to see category, "
            "priority, readiness, likely issue, next action, draft response, references, "
            "confidence, and human-review flag together."
        )

        with gr.Row():
            with gr.Column():
                subject = gr.Textbox(label="Subject", placeholder="Speaker won't reconnect to Wi-Fi")
                body = gr.Textbox(
                    label="Body",
                    lines=8,
                    placeholder="Describe the customer's issue in their own words…",
                )
                product_sku = gr.Textbox(
                    label="Product SKU (optional)",
                    placeholder="e.g. SUM1-ACT",
                )
                with gr.Row():
                    customer_persona = gr.Textbox(
                        label="Customer persona (optional)",
                        placeholder="e.g. returning-customer",
                    )
                    channel = gr.Dropdown(
                        label="Channel (optional)",
                        choices=["", "email", "chat", "phone"],
                        value="",
                    )
                submit = gr.Button("Triage ticket", variant="primary")

            with gr.Column():
                output = gr.Markdown(label="Triage result")

        submit.click(
            triage_from_form,
            inputs=[subject, body, product_sku, customer_persona, channel],
            outputs=output,
        )

        gr.Examples(
            examples=[
                [
                    "Speaker won't reconnect to Wi-Fi",
                    "My Summit One Active speakers stopped connecting to Wi-Fi right after the last firmware update.",
                    "SUM1-ACT",
                    "returning-customer",
                    "email",
                ],
                [
                    "Quick question about warranty",
                    "I bought a Cedar 200 last month and want to register it. Do I need the receipt?",
                    "CDR-200",
                    "",
                    "chat",
                ],
            ],
            inputs=[subject, body, product_sku, customer_persona, channel],
        )

    return demo


demo = build_demo()


def main() -> None:
    demo.launch()


if __name__ == "__main__":
    main()
