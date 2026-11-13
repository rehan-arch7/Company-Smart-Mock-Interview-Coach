"""
Evaluator Agent
- Scores candidate answers on correctness, depth, and communication
- Returns structured JSON evaluation
"""

import json
import re
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from chains.prompts import EVALUATOR_PROMPT


def get_evaluator_llm(model: str = "llama3.2") -> ChatOllama:
    return ChatOllama(model=model, temperature=0.1, base_url="http://localhost:11434")


def _extract_json(text: str) -> dict:
    """
    Robustly extract JSON from LLM response, even if surrounded by markdown/text.
    """
    # Try direct parse
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Try to find JSON block
    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Return a default evaluation if parsing fails
    return {
        "correctness": 5,
        "depth": 5,
        "communication": 5,
        "overall": 5.0,
        "covered_points": ["Unable to parse evaluation"],
        "missing_points": ["Evaluation parsing error"],
        "quick_feedback": "Your answer was received. Manual review recommended."
    }


def evaluate_answer(
    company: str,
    role: str,
    question: str,
    key_points: list[str],
    answer: str,
    model: str = "llama3.2"
) -> dict:
    """
    Evaluate a candidate's answer against expected key points.

    Returns:
        dict with keys: correctness, depth, communication, overall,
                        covered_points, missing_points, quick_feedback
    """
    if not answer or len(answer.strip()) < 10:
        return {
            "correctness": 0,
            "depth": 0,
            "communication": 0,
            "overall": 0.0,
            "covered_points": [],
            "missing_points": key_points[:3],
            "quick_feedback": "No substantial answer was provided."
        }

    llm = get_evaluator_llm(model=model)
    chain = EVALUATOR_PROMPT | llm | StrOutputParser()

    raw_response = chain.invoke({
        "company": company,
        "role": role,
        "question": question,
        "key_points": json.dumps(key_points, indent=2),
        "answer": answer
    })

    evaluation = _extract_json(raw_response)

    # Clamp scores to 0-10 range
    for key in ["correctness", "depth", "communication"]:
        if key in evaluation:
            evaluation[key] = max(0, min(10, int(evaluation[key])))

    # Recalculate overall if present
    if all(k in evaluation for k in ["correctness", "depth", "communication"]):
        evaluation["overall"] = round(
            (evaluation["correctness"] + evaluation["depth"] + evaluation["communication"]) / 3, 1
        )

    return evaluation


def get_score_label(score: float) -> tuple[str, str]:
    """Return a label and color for a score."""
    if score >= 8:
        return "Excellent", "#00C851"
    elif score >= 6:
        return "Good", "#33b5e5"
    elif score >= 4:
        return "Fair", "#FF8800"
    else:
        return "Needs Work", "#FF4444"
