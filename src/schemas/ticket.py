import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from src.schemas.enums import Category, Priority


def _generate_ticket_id() -> str:
    return f"TCK-GEN-{uuid.uuid4().hex[:8].upper()}"


class TicketInput(BaseModel):
    """A support ticket submitted for triage. See DATA_MODEL.md Section 1."""

    ticket_id: Optional[str] = None
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)
    product_sku: Optional[str] = None
    customer_persona: Optional[str] = None
    channel: Optional[Literal["email", "chat", "phone"]] = None
    submitted_at: Optional[datetime] = None

    @model_validator(mode="after")
    def _fill_generated_ticket_id(self) -> "TicketInput":
        if not self.ticket_id:
            self.ticket_id = _generate_ticket_id()
        return self


class ReadinessResult(BaseModel):
    """Deterministic readiness verdict for a ticket. See DATA_MODEL.md Section 1 and Section 4."""

    is_ready: bool
    missing_fields: list[str] = Field(default_factory=list)


class Reference(BaseModel):
    """A cited knowledge-base article backing a suggested response. See DATA_MODEL.md Section 7."""

    doc_id: str
    title: str
    excerpt: str


class TriageResult(BaseModel):
    """Full triage output for a ticket. See DATA_MODEL.md Section 1."""

    category: Category
    category_confidence: float = Field(ge=0.0, le=1.0)
    category_explanation: str
    priority: Priority
    priority_reason: str
    readiness: ReadinessResult
    likely_issue: str
    suggested_next_action: str
    suggested_response: str
    references: list[Reference] = Field(default_factory=list)
    confidence_level: Literal["high", "medium", "low"]
    human_review_required: bool
    human_review_reason: Optional[str] = None
