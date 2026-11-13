"""
Report Agent
- Compiles a comprehensive session report from all Q&A data
- Structures scores, strengths, gaps, and improvement plans
"""

import json
from datetime import datetime
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from chains.prompts import REPORT_PROMPT


def get_report_llm(model: str = "llama3.2") -> ChatOllama:
    return ChatOllama(model=model, temperature=0.4, base_url="http://localhost:11434")


def _build_session_data_text(answers: list[dict], scores_summary: dict) -> str:
    """Format all Q&A and evaluations into a readable text block."""
    lines = []

    lines.append("=== QUESTION-BY-QUESTION BREAKDOWN ===\n")
    for i, entry in enumerate(answers, 1):
        ev = entry.get("evaluation", {})
        lines.append(
            f"Q{i}: {entry['question']}\n"
            f"Answer: {entry['answer'][:300]}{'...' if len(entry['answer']) > 300 else ''}\n"
            f"Scores — Correctness: {ev.get('correctness', 'N/A')}/10 | "
            f"Depth: {ev.get('depth', 'N/A')}/10 | "
            f"Communication: {ev.get('communication', 'N/A')}/10 | "
            f"Overall: {ev.get('overall', 'N/A')}/10\n"
            f"Covered: {', '.join(ev.get('covered_points', []))}\n"
            f"Missed: {', '.join(ev.get('missing_points', []))}\n"
        )

    lines.append("=== AGGREGATE SCORES ===\n")
    lines.append(
        f"Average Correctness: {scores_summary.get('avg_correctness', 'N/A')}/10\n"
        f"Average Depth: {scores_summary.get('avg_depth', 'N/A')}/10\n"
        f"Average Communication: {scores_summary.get('avg_communication', 'N/A')}/10\n"
        f"Overall Average: {scores_summary.get('avg_overall', 'N/A')}/10\n"
        f"Top Strengths: {', '.join(scores_summary.get('top_strengths', []))}\n"
        f"Top Gaps: {', '.join(scores_summary.get('top_gaps', []))}\n"
    )

    return "\n".join(lines)


def compile_report(
    company: str,
    role: str,
    answers: list[dict],
    scores_summary: dict,
    coaching_notes: str,
    model: str = "llama3.2"
) -> str:
    """
    Compile a full session report using the Report Agent.

    Returns:
        Formatted markdown report string
    """
    if not answers:
        return "No session data available to compile a report."

    session_data_text = _build_session_data_text(answers, scores_summary)
    interview_date = datetime.now().strftime("%B %d, %Y at %I:%M %p")

    llm = get_report_llm(model=model)
    chain = REPORT_PROMPT | llm | StrOutputParser()

    report = chain.invoke({
        "company": company,
        "role": role,
        "date": interview_date,
        "session_data": session_data_text
    })

    # Prepend structured header
    header = (
        f"# 📋 MockMentor AI — Interview Session Report\n\n"
        f"**Company:** {company}  \n"
        f"**Role:** {role}  \n"
        f"**Date:** {interview_date}  \n"
        f"**Questions Answered:** {len(answers)}  \n"
        f"**Overall Score:** {scores_summary.get('avg_overall', 'N/A')}/10\n\n"
        f"---\n\n"
    )

    # Append coaching notes
    coaching_section = (
        f"\n\n---\n\n"
        f"## 🎯 Personalised Coaching (RAG-Grounded)\n\n"
        f"{coaching_notes}\n"
    )

    return header + report + coaching_section


def get_score_percentile(avg_score: float, company: str) -> str:
    """Estimate percentile based on historical data knowledge."""
    # Rough percentile estimation based on company difficulty
    hard_companies = {"Google", "Goldman Sachs", "Microsoft", "Amazon"}
    is_hard = company in hard_companies

    if is_hard:
        thresholds = [(8.5, "top 10%"), (7.0, "top 25%"), (5.5, "top 50%"), (4.0, "top 75%")]
    else:
        thresholds = [(8.0, "top 10%"), (6.5, "top 25%"), (5.0, "top 50%"), (3.5, "top 75%")]

    for threshold, label in thresholds:
        if avg_score >= threshold:
            return label
    return "bottom 25%"
