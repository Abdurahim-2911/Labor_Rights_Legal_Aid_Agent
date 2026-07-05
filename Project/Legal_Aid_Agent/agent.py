"""
Legal Aid Agent — Root Entry Point

ADK requires this file. It must export a variable called `root_agent`.
When you run `adk web`, ADK imports root_agent from this file and serves it.

root_agent → legal_aid_orchestrator (in orchestrator.py)
  └─ tool: process_labour_complaint (Python pipeline function)
      ├─ intake_agent (ADK Agent — classification + safety)
      ├─ legal_analysis_agent (ADK Agent — legal summary + complaint letter)
      ├─ search_legal_corpus (ChromaDB vector search)
      ├─ generate_complaint_pdf (ReportLab PDF)
      └─ lookup_ngo_contacts (JSON file lookup)
"""

from dotenv import load_dotenv

# Load GOOGLE_API_KEY / GEMINI_API_KEY from .env before anything else
load_dotenv()

from .orchestrator import legal_aid_orchestrator

root_agent = legal_aid_orchestrator
