"""
Intent Router — detects user intent and routes to the right agent.
"""

from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from chains.prompts import INTENT_PROMPT

VALID_INTENTS = {
    "start_interview",
    "submit_answer",
    "get_coaching",
    "get_report",
    "select_company",
    "general"
}


def get_llm(model: str = "llama3.2", temperature: float = 0.0) -> ChatOllama:
    """Create a ChatOllama instance."""
    return ChatOllama(
        model=model,
        temperature=temperature,
        base_url="http://localhost:11434"
    )


def route_intent(user_message: str, model: str = "llama3.2") -> str:
    """
    Detect the intent of a user message.
    Returns one of the VALID_INTENTS strings.
    """
    llm = get_llm(model=model, temperature=0.0)
    chain = INTENT_PROMPT | llm | StrOutputParser()

    result = chain.invoke({"user_message": user_message}).strip().lower()

    # Fuzzy match to valid intents
    for intent in VALID_INTENTS:
        if intent in result:
            return intent

    return "general"
