"""
Answer Relevance Evaluator - LangSmith Compatible

Evaluates whether the answer actually addresses the user's question.
"""
import os
import sys
from typing import Literal
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class RelevanceResult(BaseModel):
    """Structured result from relevance evaluation."""
    question_intent: str
    answer_addresses_intent: bool
    completeness: Literal["full", "partial", "none"]
    score: float
    reasoning: str


# Initialize evaluator LLM
evaluator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_evaluator = evaluator_llm.with_structured_output(RelevanceResult)


RELEVANCE_PROMPT = """Evaluate if the answer is relevant to the question.

<question>
{question}
</question>

<answer>
{answer}
</answer>

Instructions:
1. Identify the core intent/information need in the question
2. Check if the answer addresses that intent
3. Rate completeness: "full", "partial", or "none"
4. Score:
   - 1.0 = fully addresses the question
   - 0.7 = mostly addresses, minor gaps
   - 0.5 = partially addresses
   - 0.3 = tangentially related
   - 0.0 = does not address at all

Return question_intent, answer_addresses_intent, completeness, score, and reasoning."""


def evaluate_relevance(question: str, answer: str) -> RelevanceResult:
    """
    Check if answer addresses the question.
    
    Args:
        question: The user's question
        answer: The generated answer
    
    Returns:
        RelevanceResult with score and details
    """
    prompt = RELEVANCE_PROMPT.format(question=question, answer=answer)
    return structured_evaluator.invoke(prompt)


def evaluate_relevance_simple(question: str, answer: str) -> float:
    """Simple version that just returns the score."""
    result = evaluate_relevance(question, answer)
    return result.score


# LangSmith-compatible evaluator
def langsmith_relevance_evaluator(run, example) -> dict:
    """
    LangSmith-compatible evaluator function.
    
    Args:
        run: The LangSmith run object
        example: The dataset example
    
    Returns:
        Dict with 'score' and 'reasoning' keys
    """
    question = example.inputs.get("question", "")
    
    # Get answer from run outputs
    answer = ""
    if hasattr(run, 'outputs') and run.outputs:
        answer = run.outputs.get("answer", run.outputs.get("output", str(run.outputs)))
    
    result = evaluate_relevance(question, answer)
    
    return {
        "key": "answer_relevance",
        "score": result.score,
        "reasoning": result.reasoning,
        "metadata": {
            "question_intent": result.question_intent,
            "completeness": result.completeness,
            "addresses_intent": result.answer_addresses_intent
        }
    }


if __name__ == "__main__":
    print("=" * 50)
    print("Answer Relevance Evaluator Test")
    print("=" * 50)
    
    test_cases = [
        {
            "question": "What is the refund policy?",
            "answer": "Our refund policy allows returns within 30 days of purchase with a valid receipt."
        },
        {
            "question": "What is the refund policy?",
            "answer": "We have great customer service and many happy customers."
        },
        {
            "question": "What is the refund policy?",
            "answer": "Refunds are possible but it depends on the situation."
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Test {i} ---")
        print(f"Q: {case['question']}")
        print(f"A: {case['answer']}")
        result = evaluate_relevance(case['question'], case['answer'])
        print(f"Score: {result.score}")
        print(f"Completeness: {result.completeness}")
        print(f"Reasoning: {result.reasoning}")
