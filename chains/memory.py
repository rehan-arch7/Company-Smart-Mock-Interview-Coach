"""
Conversation memory management for the interview session.
"""

from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, AIMessage


class InterviewMemory:
    """
    Manages conversation memory for a single interview session.
    Stores:
      - chat history (last N turns)
      - session context (company, role, questions, answers, scores)
    """

    def __init__(self, window_size: int = 20):
        self.memory = ConversationBufferWindowMemory(
            k=window_size,
            return_messages=True,
            memory_key="history"
        )
        self.session = {
            "company": None,
            "role": None,
            "questions": [],        # list of question dicts from vector store
            "current_q_index": 0,
            "answers": [],          # list of {question, answer, evaluation}
            "total_questions": 5,
            "is_active": False,
            "is_complete": False,
        }

    def save_exchange(self, human_msg: str, ai_msg: str):
        """Save a human-AI exchange to memory."""
        self.memory.chat_memory.add_user_message(human_msg)
        self.memory.chat_memory.add_ai_message(ai_msg)

    def get_history(self) -> list:
        """Return message history for prompt injection."""
        return self.memory.chat_memory.messages

    def reset(self):
        """Clear memory and reset session."""
        self.memory.clear()
        self.session = {
            "company": None,
            "role": None,
            "questions": [],
            "current_q_index": 0,
            "answers": [],
            "total_questions": 5,
            "is_active": False,
            "is_complete": False,
        }

    def start_session(self, company: str, role: str, questions: list):
        """Initialise a new interview session."""
        self.reset()
        self.session.update({
            "company": company,
            "role": role,
            "questions": questions,
            "total_questions": len(questions),
            "is_active": True,
        })

    def record_answer(self, question: str, answer: str, evaluation: dict):
        """Record a question-answer-evaluation triplet."""
        self.session["answers"].append({
            "question": question,
            "answer": answer,
            "evaluation": evaluation
        })
        self.session["current_q_index"] += 1
        if self.session["current_q_index"] >= self.session["total_questions"]:
            self.session["is_complete"] = True
            self.session["is_active"] = False

    @property
    def current_question(self) -> dict | None:
        """Return the current question dict or None if done."""
        idx = self.session["current_q_index"]
        questions = self.session["questions"]
        if idx < len(questions):
            return questions[idx]
        return None

    @property
    def progress(self) -> tuple[int, int]:
        """Return (current_index, total) for progress display."""
        return self.session["current_q_index"], self.session["total_questions"]

    def get_scores_summary(self) -> dict:
        """Aggregate scores across all answers."""
        if not self.session["answers"]:
            return {}

        all_correctness = []
        all_depth = []
        all_comm = []
        gaps = []
        strengths = []

        for entry in self.session["answers"]:
            ev = entry.get("evaluation", {})
            all_correctness.append(ev.get("correctness", 0))
            all_depth.append(ev.get("depth", 0))
            all_comm.append(ev.get("communication", 0))
            gaps.extend(ev.get("missing_points", []))
            strengths.extend(ev.get("covered_points", []))

        return {
            "avg_correctness": round(sum(all_correctness) / len(all_correctness), 1),
            "avg_depth": round(sum(all_depth) / len(all_depth), 1),
            "avg_communication": round(sum(all_comm) / len(all_comm), 1),
            "avg_overall": round(
                (sum(all_correctness) + sum(all_depth) + sum(all_comm)) /
                (3 * len(self.session["answers"])), 1
            ),
            "top_gaps": list(dict.fromkeys(gaps))[:5],
            "top_strengths": list(dict.fromkeys(strengths))[:5],
        }
