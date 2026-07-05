"""
Legal Aid Agent — Pydantic Data Schemas

All structured data models used across the multi-agent system.
Each agent's output_schema points to one of these models, which
forces the LLM to return valid structured JSON.
"""

from pydantic import BaseModel, Field
from typing import Literal


# --- Combined Intake + Safety Agent Output ---

class IntakeSafetyOutput(BaseModel):
    """Structured output from the combined Intake & Safety Agent."""

    query_type: Literal["LABOUR_COMPLAINT", "GENERAL_QUESTION"] = Field(
        description="Classify if the user is describing a specific labour issue or asking a general/random question."
    )

    language: str = Field(
        description="Detected language and style (e.g. 'English', 'Arabic', 'Hindi', 'Roman Urdu', 'Hinglish')."
    )
    issue_type: Literal[
        "unpaid_wages",
        "contract_violation",
        "workplace_abuse",
        "illegal_termination",
        "unsafe_conditions",
        "other",
    ] = Field(description="The category of labour issue.")
    urgency: Literal["low", "medium", "high", "emergency"] = Field(
        description="How urgent the situation is."
    )
    missing_info: list[str] = Field(
        default_factory=list,
        description="Key details the user did NOT provide.",
    )
    risk_level: Literal["SAFE", "CAUTION", "HIGH_RISK"] = Field(
        description="SAFE=standard dispute, CAUTION=power imbalance, HIGH_RISK=physical danger."
    )
    risk_reasoning: str = Field(
        description="Why this risk level was assigned."
    )


# --- Legal Guidance Agent Output ---

class LegalAnalysisOutput(BaseModel):
    """Structured output from the Legal Guidance Agent."""

    legal_summary: str = Field(
        description="Plain-language explanation of the user's rights, grounded in legal documents."
    )
    cited_articles: list[str] = Field(
        default_factory=list,
        description="Specific article numbers cited (e.g., ['Article 51', 'Article 54']).",
    )
    evidence_checklist: list[str] = Field(
        default_factory=list,
        description="Documents/evidence the user should gather before visiting MOHRE.",
    )
    filing_guide: list[str] = Field(
        default_factory=list,
        description="Step-by-step instructions for registering a complaint via mohre.gov.ae or in person.",
    )


class TranslationOutput(BaseModel):
    """Lightweight compatibility schema for translated responses."""

    translated_text: str = Field(default="", description="Translated user-facing text.")


# --- NGO Contact (used by pure-Python routing, not an LLM) ---

class NGOContact(BaseModel):
    """A single NGO/authority contact record."""
    name: str = Field(default="")
    type: str = Field(default="")
    phone: str = Field(default="")
    url: str = Field(default="")
    notes: str = Field(default="")


# --- Unified Case Object (Session State) ---

class CaseObject(BaseModel):
    """
    Master record that flows through the entire pipeline.
    Each agent fills in its section progressively.
    """

    # User input
    user_input: str = Field(default="", description="Original user message.")

    # Intake + Safety Agent
    language: str = Field(default="English")
    issue_type: str = Field(default="")
    urgency: str = Field(default="")
    missing_info: list[str] = Field(default_factory=list)
    risk_level: str = Field(default="")
    risk_reasoning: str = Field(default="")

    # Legal Guidance Agent
    legal_summary: str = Field(default="")
    cited_articles: list[str] = Field(default_factory=list)
    evidence_checklist: list[str] = Field(default_factory=list)
    filing_guide: list[str] = Field(default_factory=list)

    # Routing (pure Python)
    ngo_contacts: list[dict] = Field(default_factory=list)
