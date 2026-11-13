# Company-Smart Mock Interview Coach

An agentic interview-preparation application that helps students practise for company- and role-specific interviews. The project combines a Streamlit interface, specialised Python agents, LangChain prompt workflows, and ChromaDB-based retrieval.

> **Data note:** The archive currently included with this project is a synthetic/sample question and feedback dataset. It demonstrates the intended workflow; it should not be described as an institution's verified 10-year corporate interview archive unless that real archive is supplied and validated.

## Problem Statement

Generic interview preparation often fails to reflect how individual companies interview. Students need realistic, company-specific practice and personalised feedback before placement drives. This project aims to address that gap by retrieving relevant questions and feedback patterns for a selected company and role, conducting a mock interview, evaluating answers, and producing an actionable improvement plan.

## Project Objectives

- Provide company- and role-oriented interview practice.
- Retrieve relevant questions and feedback examples from a vector database.
- Evaluate candidate answers for correctness, depth, and communication.
- Generate coaching feedback and a structured session report.
- Retain relevant interview context during a session.

## Agent Design

| Agent | Responsibility |
|---|---|
| Interviewer Agent | Retrieves relevant company/role questions and conducts the interview turn by turn. |
| Evaluator Agent | Evaluates answers against expected criteria, including correctness, depth, and communication. |
| Coach Agent | Produces personalised feedback using available retrieved feedback patterns. |
| Report Agent | Compiles scores, strengths, improvement areas, and a focused improvement plan. |

The codebase also contains intent-routing and conversation-memory modules. The intent router is currently a separate module; verify its integration with the Streamlit request flow before describing it as fully active end-to-end.

## Technology Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **LLM:** Ollama/local model or configured model integration (see project configuration and source)
- **Prompt orchestration:** LangChain prompt templates / LCEL
- **Vector database:** ChromaDB
- **Retrieval:** Agentic RAG workflow

## Repository Structure

```text
Agentic-AI/
├── app.py
├── setup.py
├── requirements.txt
├── .env.example
├── agents/
│   ├── interviewer.py
│   ├── evaluator.py
│   ├── coach.py
│   └── report.py
├── chains/
│   ├── intent_router.py
│   ├── memory.py
│   └── prompts.py
├── data/
│   ├── seed_data.py
│   ├── questions.json
│   └── feedback.json
├── vectorstore/
│   └── chroma_setup.py
├── chroma_db/             # local persisted vector-store data, if included
└── utils/
    └── helpers.py
```

## Setup and Run

### 1. Prerequisites

- Python version supported by the pinned packages in `requirements.txt`
- Git
- Ollama or the model/API provider configured by the application

### 2. Clone the repository

```bash
git clone https://github.com/rehan-arch7/Company-Smart-Mock-Interview-Coach.git
cd Company-Smart-Mock-Interview-Coach/Agentic-AI
```

### 3. Create and activate a virtual environment

**Windows PowerShell**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure environment

Copy `.env.example` to `.env` and set the model and vector-store settings required by your local environment. Do not commit real API keys, passwords, or private credentials.

### 6. Prepare data and vector store

Run the setup script if the project requires initial data generation or ChromaDB indexing:

```bash
python setup.py
```

If a compatible persisted ChromaDB directory is already present, check the setup script before rebuilding it.

### 7. Launch the application

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit in your browser.

## Typical Workflow

1. Start the Streamlit application.
2. Select the target company and role.
3. Begin a mock interview.
4. Answer each question in the interview flow.
5. Review evaluation scores and coaching feedback.
6. Read or export the session report and improvement plan, where supported by the current UI.

## Configuration and Data

- `.env.example` documents the environment variables expected by the project.
- `data/seed_data.py` contains the sample-data generation logic.
- `data/questions.json` and `data/feedback.json` contain generated/sample records when present.
- `vectorstore/chroma_setup.py` contains vector-store setup and retrieval utilities.
- ChromaDB persistence files are generated runtime artifacts and may need to be rebuilt when package versions or embedding configurations change.

## Current Scope and Limitations

- The supplied question and feedback records are synthetic/sample data, not independently verified company interview records.
- Coaching quality depends on the coverage and quality of the available question and feedback corpus.
- The intent-routing module exists in the codebase; its end-to-end integration should be tested before claiming all request types are automatically routed.
- Model availability, response quality, and setup steps depend on the selected local model or API configuration.

## Future Enhancements

- Replace sample data with an authorised, anonymised institutional interview archive.
- Complete and test end-to-end intent routing for interview practice, evaluation, and coaching.
- Add robust session persistence, authentication, and candidate progress tracking.
- Add tests for retrieval relevance, agent outputs, and error handling.
- Provide configurable evaluation rubrics and transparent score explanations.

## Security

Never commit `.env`, API keys, access tokens, passwords, private candidate information, or unredacted institutional interview records. Use anonymised data and ensure you have permission to store and process any interview archive.

## Author

**Repository:** [rehan-arch7/Company-Smart-Mock-Interview-Coach](https://github.com/rehan-arch7/Company-Smart-Mock-Interview-Coach)
