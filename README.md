# Company-Smart Mock Interview Coach

An agentic interview-preparation system that helps students practise for company- and role-specific interviews. It combines a Streamlit interface, specialised Python agents, LangChain prompt workflows, and ChromaDB-based retrieval.

> **Dataset note:** The supplied question and feedback files are sample/synthetic data. They demonstrate the intended workflow and are not represented as an institution's verified 10-year corporate interview archive.

## Problem Statement

Generic interview preparation does not reflect how specific companies actually interview. Students lack realistic, company-specific practice and personalised feedback before placement drives.

This project aims to let a student select a target company and role, practise through a realistic mock interview, receive evaluation of each answer, and get coaching based on the available company/role feedback patterns.

## Objectives

- Conduct company- and role-specific mock interviews.
- Retrieve relevant questions and feedback examples using RAG and ChromaDB.
- Evaluate responses for correctness, depth, and communication.
- Generate personalised coaching and an actionable improvement plan.
- Retain relevant context during an interview session.

## Agent Architecture

| Agent | Responsibility |
|---|---|
| Interviewer Agent | Retrieves relevant company- and role-specific questions and conducts the interview turn by turn. |
| Evaluator Agent | Scores answers for correctness, depth, and communication against expected criteria. |
| Coach Agent | Generates personalised feedback using the available historical/sample feedback patterns. |
| Report Agent | Compiles scores, strengths, gaps, and a focused improvement plan. |

The repository also includes intent-routing and conversation-memory modules. The intent router should be tested in the full application flow before claiming that every intent is automatically routed end to end.

## Technology Stack

- **Frontend:** Streamlit
- **Backend:** Python
- **LLM:** Local model or API-based model, depending on configuration
- **Prompt orchestration:** LangChain prompt templates and LCEL
- **Vector database:** ChromaDB
- **Retrieval approach:** Agentic Retrieval-Augmented Generation (RAG)

## Project Structure

The contents of the original `Agentic-AI/` project directory belong directly at the repository root:

```text
Company-Smart-Mock-Interview-Coach/
├── agents/
│   ├── __init__.py
│   ├── interviewer.py
│   ├── evaluator.py
│   ├── coach.py
│   └── report.py
├── chains/
│   ├── __init__.py
│   ├── intent_router.py
│   ├── memory.py
│   └── prompts.py
├── chroma_db/
├── data/
│   ├── __init__.py
│   ├── feedback.json
│   ├── questions.json
│   └── seed_data.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
├── vectorstore/
│   ├── __init__.py
│   └── chroma_setup.py
├── .env.example
├── app.py
├── requirements.txt
├── setup.py
└── README.md
```

## Installation and Setup

### 1. Prerequisites

- Windows 10/11, macOS, or Linux
- Python version compatible with the packages in `requirements.txt`
- Git
- Access to the configured local LLM or API provider

### 2. Clone the repository

```bash
git clone https://github.com/rehan-arch7/Company-Smart-Mock-Interview-Coach.git
cd Company-Smart-Mock-Interview-Coach
```

### 3. Create a virtual environment

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

### 5. Configure environment variables

Copy `.env.example` to `.env` and fill in the values required by your selected model/provider and application configuration.

Never commit real API keys, passwords, access tokens, or private credentials.

### 6. Prepare the data and vector store

Review the setup script and vector-store configuration, then run the project setup step if required:

```bash
python setup.py
```

If the ChromaDB persistence directory is not present or is incompatible with the installed package/embedding configuration, initialise or rebuild it using the project's vector-store setup code.

### 7. Run the application

```bash
streamlit run app.py
```

Open the local URL printed by Streamlit in your browser.

## How the System Works

1. The student selects a target company and job role.
2. The interviewer workflow retrieves relevant questions from the available question bank.
3. The Interviewer Agent asks questions turn by turn.
4. The Evaluator Agent assesses each response for correctness, depth, and communication.
5. The Coach Agent provides personalised feedback and improvement suggestions.
6. The Report Agent compiles the session results, strengths, weaknesses, and improvement plan.

The exact available workflow depends on the current application implementation and configured model.

## Main Modules

- **`app.py`:** Streamlit application entry point and user interface.
- **`agents/`:** Interviewer, evaluator, coach, and report agent logic.
- **`chains/`:** Prompt templates, memory, and intent-routing logic.
- **`data/`:** Sample interview questions, feedback records, and seed-data utilities.
- **`vectorstore/`:** ChromaDB setup and retrieval utilities.
- **`chroma_db/`:** Persisted local vector database files, when included.
- **`utils/`:** Shared helper functions.
- **`requirements.txt`:** Python dependencies.
- **`.env.example`:** Example environment configuration.

## Current Scope and Limitations

- The supplied question and feedback records are sample/synthetic data, not independently verified company interview records.
- The system's company-specific usefulness depends on the quality, coverage, and authenticity of the question bank and feedback corpus.
- Intent-routing and memory modules exist in the codebase; their end-to-end integration should be validated with application tests.
- Model availability, response quality, and setup steps depend on the selected local model or API configuration.

## Future Enhancements

- Integrate an authorised and anonymised institutional interview archive.
- Complete and test end-to-end intent routing for interview practice, answer evaluation, and coaching.
- Improve retrieval relevance with metadata filters for company, role, topic, and difficulty.
- Add candidate progress tracking and session history.
- Add automated tests for retrieval, agent behaviour, and error handling.
- Provide transparent scoring rubrics and explainable feedback.

## Security and Privacy

- Keep `.env` and all secrets out of version control.
- Do not commit private candidate information or unredacted institutional interview records.
- Use only interview data that the institution is authorised to store and process.
- Anonymise personal information before indexing documents in the vector database.

## Repository

[Company-Smart-Mock-Interview-Coach on GitHub](https://github.com/rehan-arch7/Company-Smart-Mock-Interview-Coach)
