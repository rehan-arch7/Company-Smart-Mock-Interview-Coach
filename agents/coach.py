"""
Coach Agent
- Retrieves historical feedback patterns from ChromaDB (RAG)
- Generates personalised coaching grounded in real feedback patterns
"""

from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from chains.prompts import COACH_PROMPT
from vectorstore.chroma_setup import query_feedback


def get_coach_llm(model: str = "llama3.2") -> ChatOllama:
    return ChatOllama(model=model, temperature=0.6, base_url="http://localhost:11434")


def _format_feedback_context(feedbacks: list[dict]) -> str:
    """Format historical feedback into a readable context string."""
    if not feedbacks:
        return "No historical feedback data available for this company/role."

    lines = []
    for i, fb in enumerate(feedbacks, 1):
        lines.append(
            f"Pattern {i} (avg score {fb.get('candidate_score', 'N/A')}/10):\n"
            f"  Historical insight: {fb.get('pattern_summary', '')}\n"
            f"  Common strengths seen: {', '.join(fb.get('strengths', []))}\n"
            f"  Frequent gaps: {', '.join(fb.get('gaps', []))}"
        )
    return "\n\n".join(lines)


def generate_coaching(
    company: str,
    role: str,
    num_questions: int,
    avg_score: float,
    main_gaps: list[str],
    strengths: list[str],
    model: str = "llama3.2"
) -> str:
    """
    Generate personalised coaching using RAG-retrieved historical feedback patterns.

    Args:
        company: Target company name
        role: Target role name
        num_questions: Number of questions answered
        avg_score: Average score across all answers
        main_gaps: List of identified gaps from evaluations
        strengths: List of demonstrated strengths
        model: Ollama model to use

    Returns:
        Formatted coaching text
    """
    # RAG: Retrieve historical feedback patterns for this company/role
    historical_feedbacks = query_feedback(company=company, role=role, n_results=5)
    feedback_context = _format_feedback_context(historical_feedbacks)

    llm = get_coach_llm(model=model)
    chain = COACH_PROMPT | llm | StrOutputParser()

    coaching = chain.invoke({
        "company": company,
        "role": role,
        "historical_feedback": feedback_context,
        "num_questions": num_questions,
        "avg_score": avg_score,
        "main_gaps": ", ".join(main_gaps) if main_gaps else "None identified",
        "strengths": ", ".join(strengths) if strengths else "To be determined"
    })

    return coaching


def get_quick_coaching_tip(company: str, role: str, gap: str, model: str = "llama3.2") -> str:
    """Generate a single quick coaching tip for a specific gap."""
    from langchain_core.messages import HumanMessage

    historical = query_feedback(company=company, role=role, n_results=2)
    context = _format_feedback_context(historical)

    llm = get_coach_llm(model=model)
    prompt = (
        f"Given historical patterns for {company} {role} interviews:\n{context}\n\n"
        f"Provide ONE specific, actionable coaching tip (3-4 sentences) to address this gap: {gap}\n"
        f"Focus on what {company} specifically looks for."
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
