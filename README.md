# Legal Aid Agent

Legal Aid Agent is a workflow-based pipeline built using the Google Agent Development Kit (ADK) that provides UAE labor rights assistance. The agent gives clear, compassionate guidance on rights, complaint filing procedures, and directs individuals to the proper authorities based on UAE labor law.

# Problem

Many workers in the UAE face issues such as unpaid wages, unfair termination, contract violations, and unsafe working conditions. While legal protections exist, understanding labour laws and navigating the complaint process can be difficult, particularly for migrant workers facing language barriers or unfamiliar government procedures.

As a result, many legitimate cases go unreported because workers are unsure of their rights or the steps required to seek assistance.

# Solution

The Labor Rights Legal Aid Agent is a multi-agent AI assistant built with Google Agent Development Kit (ADK) that helps workers understand their rights under UAE labour law and navigate the complaint process with confidence.

Using a Retrieval-Augmented Generation (RAG) pipeline over a curated legal corpus, the system provides grounded legal explanations with article citations, generates complaint documents and evidence checklists, and guides users to the appropriate government authority or support organization.

To improve accessibility, the agent supports four commonly spoken languages among UAE workers:

Arabic\
English\
Urdu\
Hindi

By combining multilingual support, specialized AI agents, and legally grounded responses, the system makes reliable labour rights guidance more accessible and actionable.

## Features

- **Intake & Risk Assessment**: Classifies the user's issue (e.g., unpaid wages, contract violation), detects language/dialect, and assesses risk level for physical danger (SAFE, CAUTION, HIGH_RISK).
- **Legal Guidance**: Uses vector search across a UAE legal corpus to retrieve relevant articles, builds a legal summary, creates evidence checklists, and generates complaint PDFs.
- **Multilingual & Compassionate Responses**: Translates complex legal information into plain language, matching the user's tone and language, and prioritizes safety with emergency NGO contacts in high-risk situations.
- **Dynamic Orchestration**: Uses an ADK Workflow to pass structured case data seamlessly between specialized sub-agents.

## Architecture

The project is built around the Google ADK and utilizes the `gemini-3.1-flash-lite` model. The root workflow (`legal_aid_orchestrator`) connects three core sub-agents sequentially:

1. **Intake & Safety Agent** (`intake_agent.py`): Triages the user's query, classifying issue type and urgency, and performs a strict risk assessment without giving legal advice.
2. **Legal Analysis Agent** (`legal_analysis_agent.py`): Receives the intake classification, searches the legal corpus using ChromaDB, builds a structured case object, and generates a formal complaint PDF if needed.
3. **Final Response Agent** (`orchestrator.py`): Consolidates the structured data into a 7-part response covering situation assessment, legal rights, missing information, evidence gathering, MOHRE filing steps, NGO contacts, and a legal disclaimer.

## Installation :

    ### 1. Clone the Repository

    ```cmd
    git clone https://github.com/Abdurahim-2911/Labor_Rights_Legal_Aid_Agent.git
    cd Labor_Rights_Legal_Aid_Agent
    ```
    

    ### 2. Create a `.env` File

    Create a `.env` file in the project root and paste the following contents:

    ```
    GOOGLE_API_KEY='PUT YOUR API KEY HERE'
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    ```

    ### 3. Create a Virtual Environment

    Open a terminal (Command Prompt) in the project directory and run:

    ```cmd
    python -m venv venv
    ```

    ### 4. Activate the Virtual Environment

    **Windows**

    ```cmd
    venv\Scripts\activate
    ```

    **Linux / macOS**

    ```bash
    source venv/bin/activate
    ```

    ### 5. Install the Required Dependencies

    ```bash
    pip install -r requirements.txt
    ```

    ---

## Usage:

    ### 1. Activate the Virtual Environment

    **Windows**

    ```bash
    venv\Scripts\activate
    ```

    **Linux / macOS**

    ```bash
    source venv/bin/activate
    ```

    ### 2. Build the Vector Database

    The following command processes the legal corpus and creates the ChromaDB vector database used for Retrieval-Augmented Generation (RAG).

    ```bash
    python scripts/ingest_corpus.py
    ```

    > **Note:** This step only needs to be run once unless the legal corpus is modified.

    ### 3. Launch the Agent

    Start the Google ADK web interface:

    ```bash
    adk web
    ```

    Once the server starts, open the local URL displayed in your terminal to begin interacting with the Labor Rights Legal Aid Agent.

## Tech Stack

1.Google Agent Development Kit (ADK)

2.Gemini models (LLM + embeddings)

3.ChromaDB (local vector database)

4.ReportLab (PDF generation)

5.Pydantic (structured outputs)

6.Python 3.10+

## Constraints

Single jurisdiction: UAE labour law only

No live web scraping or external API enrichment

No real user data storage (synthetic testing only)

No messaging integrations (WhatsApp/Telegram/etc.)

Safety Agent overrides all downstream processing in high-risk cases

## Project Structure

```text
Legal_Aid_Agent/
├── .env                        # Environment variables (API keys)
├── agent.py                    # Root entry point exposing `root_agent`
├── orchestrator.py             # Defines the ADK Workflow pipeline & final response agent
├── requirements.txt            # Python dependencies
├── data/                       # Contains ChromaDB instance, legal corpus, and NGO contacts
├── schemas/                    # Pydantic models for structured data passing
├── scripts/                    # Helper scripts for the project
├── sub_agents/                 # Specialized ADK agents
│   ├── intake_agent.py         # Handles triage and safety checks
│   └── legal_analysis_agent.py # Handles corpus retrieval and case structuring
└── tools/                      # Tool functions used by the agents
    ├── embedding_helper.py     # ChromaDB and embedding utilities
    ├── ngo_lookup_tool.py      # Retrieves emergency/NGO contacts
    ├── pdf_generator_tool.py   # Generates complaint PDFs with ReportLab
    ├── vector_search_tool.py   # Tool for querying the legal corpus
    └── web_search_tool.py      # Fallback web search for general questions
```
