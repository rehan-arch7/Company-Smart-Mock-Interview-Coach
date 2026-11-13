"""
Interviewer Agent
- Retrieves company/role-specific questions from ChromaDB (RAG)
- Conducts turn-by-turn interview conversation via LangChain LCEL
"""

from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from chains.prompts import INTERVIEWER_PROMPT
from vectorstore.chroma_setup import query_questions
import random


def get_interviewer_llm(model: str = "llama3.2") -> ChatOllama:
    return ChatOllama(model=model, temperature=0.7, base_url="http://localhost:11434")


def fetch_interview_questions(company: str, role: str, num_questions: int = 5) -> list[dict]:
    """
    RAG: Retrieve company+role specific questions from ChromaDB.
    Returns a list of question dicts ordered by difficulty progression.
    """
    questions = query_questions(company=company, role=role, n_results=num_questions + 3)

    if not questions:
        # Fallback: generic questions if no company-specific ones found
        questions = query_questions(company=company, role=role, n_results=10)

    # Order: easy → medium → hard for progressive difficulty
    order = {"easy": 0, "medium": 1, "hard": 2}
    questions.sort(key=lambda q: order.get(q.get("difficulty", "medium"), 1))

    # Ensure variety in difficulty
    easy = [q for q in questions if q.get("difficulty") == "easy"]
    medium = [q for q in questions if q.get("difficulty") == "medium"]
    hard = [q for q in questions if q.get("difficulty") == "hard"]

    selected = []
    if easy:
        selected.append(random.choice(easy))
    for q in medium[:2]:
        selected.append(q)
    for q in hard[:2]:
        selected.append(q)

    # Fill remaining slots
    remaining = [q for q in questions if q not in selected]
    while len(selected) < num_questions and remaining:
        selected.append(remaining.pop(0))

    return selected[:num_questions]


def conduct_interview_turn(
    company: str,
    role: str,
    question: dict,
    user_input: str,
    history: list,
    model: str = "llama3.2"
) -> str:
    """
    One turn of the interview: given the current question and user's reply,
    return the interviewer's response.
    """
    llm = get_interviewer_llm(model=model)
    chain = INTERVIEWER_PROMPT | llm | StrOutputParser()

    response = chain.invoke({
        "company": company,
        "role": role,
        "question": question["question"],
        "difficulty": question.get("difficulty", "medium"),
        "tags": question.get("tags", ""),
        "history": history,
        "user_input": user_input
    })

    return response


def get_opening_message(company: str, role: str, first_question: dict) -> str:
    """Generate the interviewer's opening message."""
    return (
        f"Hello! I'm your interviewer for the **{role}** position at **{company}** today. "
        f"We'll go through {5} questions covering different aspects of the role. "
        f"Take your time, and feel free to think out loud.\n\n"
        f"Let's begin.\n\n"
        f"**Question 1:** {first_question['question']}"
    )
