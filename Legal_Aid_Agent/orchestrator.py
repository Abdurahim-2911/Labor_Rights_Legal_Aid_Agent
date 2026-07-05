"""
Legal Aid Orchestrator — ADK Workflow

The root agent is now an ADK Workflow that runs the core pipeline in order:

    1. Intake & Safety Agent → classify the issue and assess risk
    2. Legal Guidance Agent → gather legal guidance and case-specific next steps
    3. Final Response Agent → turn the gathered state into a clear answer

The workflow keeps the current safety logic, general-question web search, and
emergency contact handling while removing the old single-tool Processor pattern.
"""

from google.adk.agents import Agent
from google.adk.workflow import Workflow
from google.adk.planners import BuiltInPlanner
from google.genai import types

try:
    from .sub_agents.intake_agent import intake_agent
    from .sub_agents.legal_analysis_agent import legal_analysis_agent
    from .tools.ngo_lookup_tool import lookup_ngo_contacts
    from .tools.web_search_tool import search_web_for_info
except ImportError:
    from sub_agents.intake_agent import intake_agent
    from sub_agents.legal_analysis_agent import legal_analysis_agent
    from tools.ngo_lookup_tool import lookup_ngo_contacts
    from tools.web_search_tool import search_web_for_info


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


def _build_response_instruction(context) -> str:
    """Build a dynamic instruction for the final response agent from shared state."""
    intake_result = context.state.get("intake_result", {}) or {}
    legal_result = context.state.get("legal_analysis_result", {}) or {}
    user_text = _extract_text(context.user_content)

    query_type = intake_result.get("query_type", "LABOUR_COMPLAINT")
    language = intake_result.get("language", "English")
    issue_type = intake_result.get("issue_type", "other")
    urgency = intake_result.get("urgency", "medium")
    risk_level = intake_result.get("risk_level", "SAFE")
    risk_reasoning = intake_result.get("risk_reasoning", "")
    missing_info = intake_result.get("missing_info", [])

    legal_summary = legal_result.get("legal_summary", "")
    cited_articles = legal_result.get("cited_articles", [])
    evidence_checklist = legal_result.get("evidence_checklist", [])
    filing_guide = legal_result.get("filing_guide", [])

    if query_type == "GENERAL_QUESTION":
        return f"""You are the final response agent for the Legal Aid Agent.

The user asked: {user_text}

First interaction rule:
- Do not always start by introducing yourself.
- Only introduce yourself briefly on the very first interaction if the user is greeting you, asking who you are, or asking what you can do.
- For normal casual chat, simple greetings, or quick follow-ups, respond naturally and directly without leading with your role.
- If the user asks what you can do or what your capabilities are, answer more fully and clearly. Mention that you can help explain rights, guide complaint filing, explain procedures, point people to the right authorities, and help with next steps in a labour-related issue.

For general chat, follow-up, or non-complaint questions:
- Reply warmly, clearly, and in the user's language and tone.
- Keep the answer short and easy to read.
- Use short paragraphs and small bullet lists when helpful.
- If the user asks for more detail, expand the explanation with a bit more context.
- Sound natural and conversational, not robotic or overly formal.

Do not use web search for labour complaint or case-specific legal analysis. Use it only for unrelated general facts.
"""

    if risk_level == "HIGH_RISK":
        return f"""You are the final response agent for the Legal Aid Agent.

The user asked: {user_text}

Safety check: the intake agent marked this as HIGH_RISK because: {risk_reasoning}

Priority rule (HIGH_RISK):
- Stop the normal guidance flow. Safety is the only priority.
- Immediately tell the user to seek emergency help now and provide the most relevant emergency contacts.
- Use the `lookup_ngo_contacts` tool to find nearby and relevant contacts and present them clearly.
- Keep the message calm, compassionate, and actionable. Do not ask for non-essential details that delay help.

Return only emergency instructions and contact details; do not include the full legal-summary/evidence/filing sections.
"""

    missing_info_text = "\n".join(f"- {m}" for m in missing_info) if missing_info else "None"
    cited_articles_text = "\n".join(f"- {a}" for a in cited_articles) if cited_articles else "None"
    evidence_text = "\n".join(f"- {e}" for e in evidence_checklist)
    filing_text = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(filing_guide))

    return f"""You are the final response agent for the Legal Aid Agent.

The user asked: {user_text}

Use the structured case data below to write the final answer. Follow this required 7-part structure exactly and include every section inline:

1. Situation Assessment
- State the risk level, urgency, and issue type in plain language.
- If `risk_level` is HIGH_RISK, immediately follow the HIGH_RISK priority rule and do not continue to other sections.

2. Your Legal Rights
- Explain the `legal_summary` clearly and briefly.
- Quote or paraphrase any `cited_articles` and explain what each article means in simple terms.
- If `cited_articles` is empty, say so and give general guidance for the `issue_type`.

3. What Information Would Strengthen Your Case
- If `missing_info` contains items, list a short set of the most important ones and explain why they matter.

4. Evidence to Gather Before Filing
- Present the main items from `evidence_checklist` as a short checklist with a one-line explanation for each.

5. How to Register Your Complaint with MOHRE
- Present the main steps from `filing_guide` in a short numbered list.

6. Authorities and Organisations That Can Help
- List the most relevant NGO/authority contacts with name, phone, website, and a short note on when to contact them.

7. Disclaimer
- End with a short disclaimer that this is informational guidance grounded in official UAE labour law texts. It is not legal advice. For binding legal advice, consult a licensed lawyer or contact MOHRE directly at mohre.gov.ae or call 800 60

Critical rules:
- NEVER say "as mentioned above", "as stated previously", or similar.
- NEVER skip a required section.
- NEVER invent laws, article numbers, contacts, or procedural steps not present in the structured case data.
- ALWAYS reply in the exact language, dialect, and script the user used.
- NEVER use `transfer_to_agent` or delegate to another agent.

Tone and style:
- Use warm, empathetic, plain-language phrasing suitable for low-income and migrant workers.
- Keep the answer concise, well spaced, and easy to scan.
- Add blank lines between sections and between paragraphs.
- Use short bullet lists and short numbered lists; do not overload the user.
- If the user asks for more detail, expand the relevant section with extra context and explanation.
"""


response_agent = Agent(
    name="response_agent",
    model="gemini-3.1-flash-lite",
    description="Acts as the Legal Aid Agent by giving clear, compassionate guidance on rights, complaint filing, procedures, and the right authorities.",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=False,
            thinking_budget=1024,
        )
    ),
    instruction=_build_response_instruction,
    tools=[search_web_for_info, lookup_ngo_contacts],
    mode="single_turn",
    include_contents="none",
    output_key="final_response",
)


legal_aid_orchestrator = Workflow(
    name="legal_aid_orchestrator",
    description=(
        "Workflow-based Legal Aid Agent pipeline for UAE labour rights, covering intake, legal guidance, and final responses."
    ),
    edges=[
        ("START", intake_agent, legal_analysis_agent, response_agent),
    ],
)

