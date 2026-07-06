# Legal Aid Agent

Legal Aid Agent is a workflow-based pipeline built using the Google Agent Development Kit (ADK) that provides UAE labor rights assistance. The agent gives clear, compassionate guidance on rights, complaint filing procedures, and directs individuals to the proper authorities based on UAE labor law.

# Problem

Every day, thousands of workers in the UAE experience labour issues such as delayed salaries, unfair termination, unsafe working conditions, contract violations, and employer misconduct. Although legal protections exist, many workers never seek help.

The barrier is often not the absence of laws—it is the lack of accessible legal guidance.

Many workers are unfamiliar with UAE labour regulations, struggle to understand legal documents written in technical language, or simply do not know where to report their issue. Others fear retaliation, believe their case is too weak, or assume the complaint process is too complicated. Language barriers further limit access to reliable information, especially for migrant workers whose primary languages are Arabic, English, Urdu, or Hindi.

As a result, legitimate labour disputes frequently go unresolved because workers lack the confidence and knowledge to take the first step.

# Solution

The **Labor Rights Legal Aid Agent** is an AI-powered multi-agent assistant designed to make UAE labour rights understandable and actionable for everyone.

Instead of expecting workers to interpret complex legal documents or navigate government procedures on their own, the agent explains labour laws, employment contracts, and worker rights in simple, easy-to-understand language.

Using a specialized multi-agent architecture built with Google ADK, the system analyzes a worker's situation, retrieves the relevant UAE labour law articles through Retrieval-Augmented Generation (RAG), and provides grounded explanations supported by official legal sources.

Beyond answering questions, the agent guides workers through the complaint process by providing clear, step-by-step instructions on where to file a complaint, what documents are required, and which government authority or support organization is appropriate for their specific case.

To maximize accessibility, the system supports four of the most widely spoken languages among UAE workers:

* Arabic
* English
* Urdu
* Hindi

By combining multilingual communication, grounded legal retrieval, and practical procedural guidance, the Labor Rights Legal Aid Agent helps workers better understand their rights, make informed decisions, and confidently access the legal support available to them.

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
    
    !<img width="1104" height="641" alt="Cloning" src="https://github.com/user-attachments/assets/60b0028f-7158-4560-8792-4e08ae7bd420" />

    ```
    

    ### 2. Create a `.env` File

    Create a `.env` file in the project root and paste the following contents:

    ```
    GOOGLE_API_KEY='PUT YOUR API KEY HERE'
    GOOGLE_GENAI_USE_VERTEXAI=FALSE
    
    ![ENV](https://github.com/user-attachments/assets/f3bcc8c7-da54-48b3-899d-577f6e125631)
    ```

    ### 3. Create a Virtual Environment

    Open a terminal (Command Prompt) in the project directory and run:

    ```cmd
    python -m venv venv
    
    <img width="1103" height="638" alt="venv create" src="https://github.com/user-attachments/assets/326b6351-1455-4a22-beee-dcd14e043186" />
    ```

    ### 4. Activate the Virtual Environment

    **Windows**

    ```bash
    venv\Scripts\activate

    <img width="1104" height="636" alt="venv activate" src="https://github.com/user-attachments/assets/15acaa21-1bb4-49aa-8df1-c68c9baf6b0e" />
    ```

    **Linux / macOS**

    ```bash
    source venv/bin/activate
    ```

    ### 5. Install the Required Dependencies

    ```bash
    pip install -r requirements.txt
    <img width="1109" height="1028" alt="Capture" src="https://github.com/user-attachments/assets/ddf22a5d-39bc-4cba-aa76-691216d6d761" />
    <img width="1898" height="947" alt="Capture2" src="https://github.com/user-attachments/assets/a054604b-a4de-4add-80f3-eb0088915ab9" />
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
