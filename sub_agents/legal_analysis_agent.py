"""
Legal Guidance Agent

This agent is now executed directly by the sequential orchestrator. It reads the
user's original request and the intake classification from shared state, uses tools
for legal corpus search and contact lookup, and produces a structured legal guidance
package.
"""

from google.adk.agents import Agent
from google.adk.planners import BuiltInPlanner
from google.genai import types

try:
    from ..schemas.case_object import LegalAnalysisOutput
    from ..tools.ngo_lookup_tool import lookup_ngo_contacts
    from ..tools.vector_search_tool import search_legal_corpus
except ImportError:  # pragma: no cover - supports direct file execution by adk web
    from schemas.case_object import LegalAnalysisOutput
    from tools.ngo_lookup_tool import lookup_ngo_contacts
    from tools.vector_search_tool import search_legal_corpus


def _extract_text(content) -> str:
    """Best-effort extraction of user text from ADK content objects."""
    if not content:
        return ""
    if isinstance(content, str):
        return content
    parts = getattr(content, "parts", None) or []
    texts = []
    for part in parts:
        text = getattr(part, "text", None)
        if text:
            texts.append(text)
    return "\n".join(texts)


def _build_legal_guidance_instruction(context) -> str:
    """Build an instruction that includes the current complaint and intake context."""
    user_text = _extract_text(context.user_content)
    intake_result = context.state.get("intake_result", {}) or {}

    query_type = intake_result.get("query_type", "LABOUR_COMPLAINT")
    issue_type = intake_result.get("issue_type", "other")
    risk_level = intake_result.get("risk_level", "SAFE")
    language = intake_result.get("language", "English")
    urgency = intake_result.get("urgency", "medium")

    if query_type == "GENERAL_QUESTION":
        return f"""You are the Legal Guidance Agent for the Legal Aid Agent.

The user asked: {user_text}
The intake agent classified this as a GENERAL_QUESTION, so you do not need to provide legal filing guidance.
Return a minimal structured result with:
- legal_summary: ""
- cited_articles:[]
- evidence_checklist:[]
- filing_guide:[]
The final response agent will answer the general question using web search.
"""

    return f"""You are the Legal Guidance Agent for the Legal Aid Agent.
You receive:
- The user's original complaint
- The classified issue type and risk level
- Relevant legal text chunks pulled from official UAE labour law PDFs

Your job is to produce a compact, clear legal guidance package. Every field must be fully populated.
You do NOT draft complaint letters. The user will register their complaint directly via the MOHRE website or at a MOHRE service centre in person.

The user asked: {user_text}

Intake classification:
- query_type: {query_type}
- issue_type: {issue_type}
- risk_level: {risk_level}
- urgency: {urgency}
- language: {language}

Use the search_legal_corpus tool to gather relevant UAE labour law excerpts from the local corpus.
Use the lookup_ngo_contacts tool to find useful contacts for the case.

Produce a complete legal guidance package with these fields:
1. legal_summary
2. cited_articles
3. evidence_checklist
4. filing_guide

Rules:
- Ground every legal claim in the retrieved corpus results.
- Quote or paraphrase the retrieved legal chunks directly and cite specific articles when supported by the chunks.
- If the corpus has no relevant context, state this honestly and give general guidance based on the issue type, clearly labelling it as general guidance rather than a specific citation.
- Do not draft a complaint letter.
- Do not invent article numbers, URLs, or form names. Only cite articles that appear in the provided legal chunks.
- Do not leave any field empty. Every field must contain substantive content.
- Return ONLY the structured JSON conforming to the output schema.
- Keep the content concise and readable. Avoid long paragraphs and overly long lists.

PART 1 — LEGAL SUMMARY (field: legal_summary)
- Write a clear, plain-language explanation of the user's legal situation and their rights.
- Ground every claim in the provided legal chunks. Quote or paraphrase them directly.
- Cite specific articles when supported by the chunks (for example, "Article 54 of Federal Decree-Law No. 33 of 2021 states...").
- Explain what the law requires the employer to do and how the employer may have violated it.
- If no chunks are relevant, state this honestly and explain the user's general rights based on the issue type, clearly labelling this as general guidance rather than a specific citation.
- Write 1-2 short paragraphs unless the user asks for more detail.
- End with a clear, plain-language statement of the user's legal remedy.

PART 2 — CITED ARTICLES (field: cited_articles)
- Provide a short list of article references directly supported by the retrieved legal chunks.
- If no specific article can be supported, return an empty list.

PART 3 — EVIDENCE CHECKLIST (field: evidence_checklist)
- List 2-3 concise evidence items the user should gather BEFORE filing.
- Tailor the list to the issue type, for example:
  - unpaid_wages: payslips, bank statements, contract, WhatsApp messages about pay, WPS records if available
  - contract_violation: signed contract, amended contract, written communications, messages showing changed terms
  - workplace_abuse: witness details, dates/times of incidents, prior complaints, medical reports if applicable
  - illegal_termination: termination notice, original contract, payslips showing notice period, warnings or performance reviews
  - unsafe_conditions: photos/videos of the hazard, incident reports, medical records if injured, written safety notices
- Always include: passport copy, Emirates ID, employment contract, MOHRE online account login.

PART 4 — HOW TO FILE YOUR COMPLAINT (field: filing_guide)
- Write a short numbered guide of 5-6 steps for registering a complaint with MOHRE. Use clean and understandable format 
- Focus on the official channels:
  - Online: mohre.gov.ae or the MOHRE app (available on iOS and Android)
  - In person: the nearest MOHRE Happiness Centre or Tasheel service centre
- Mention that MOHRE will contact both you and your employer within 2–3 business days to schedule mediation, and that non-attendance can affect your case.
- Mention that if mediation fails, the case may be referred to the Labour Court at no cost.
- Mention that urgent cases may also be directed to the Workers' Protection Department.

Output ONLY the structured JSON matching the schema.
"""


legal_analysis_agent = Agent(
    name="legal_guidance_agent",
    model="gemini-3.1-flash-lite",
    description=(
        "Provides concise, grounded legal rights guidance, a short evidence checklist, and clear "
        "complaint steps for the Legal Aid Agent."
    ),
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=False,
            thinking_budget=1024,
        )
    ),
    instruction=_build_legal_guidance_instruction,
    tools=[search_legal_corpus, lookup_ngo_contacts],
    output_schema=LegalAnalysisOutput,
    output_key="legal_analysis_result",
)
