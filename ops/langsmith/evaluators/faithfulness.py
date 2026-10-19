"""
Faithfulness Evaluator - LangSmith Compatible

Wraps the existing faithfulness evaluation logic for use with LangSmith.
"""
import os
import sys
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'evals'))


class FaithfulnessResult(BaseModel):
    """Structured result from faithfulness evaluation."""
    claims: list[str]
    supported_claims: list[str]
    unsupported_claims: list[str]
    score: float
    reasoning: str


# Initialize evaluator LLM
evaluator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_evaluator = evaluator_llm.with_structured_output(FaithfulnessResult)


FAITHFULNESS_PROMPT = """Evaluate if the answer is faithful to the provided context.
Faithful means: every factual claim in the answer can be traced back to the context.

<context>
{context}
</context>

<answer>
{answer}
</answer>

Instructions:
1. Extract all factual claims/statements from the answer
2. For each claim, check if the context supports it
3. Calculate score = len(supported_claims) / len(all_claims)
4. If answer says "I don't know" with no factual claims, score = 1.0
5. If answer has 0 claims, score = 1.0

Return claims, supported_claims, unsupported_claims, score, and reasoning."""


def evaluate_faithfulness(answer: str, context: str) -> FaithfulnessResult:
    """
    Check if answer is grounded in the retrieved context.
    
    Args:
        answer: The generated answer
        context: The retrieved context used to generate the answer
    
    Returns:
        FaithfulnessResult with score and details
    """
    prompt = FAITHFULNESS_PROMPT.format(context=context, answer=answer)
    return structured_evaluator.invoke(prompt)


def evaluate_faithfulness_simple(answer: str, context: str) -> float:
    """Simple version that just returns the score."""
    result = evaluate_faithfulness(answer, context)
    return result.score


# LangSmith-compatible evaluator
def langsmith_faithfulness_evaluator(run, example) -> dict:
    """
    LangSmith-compatible evaluator function.
    
    Args:
        run: The LangSmith run object
        example: The dataset example
    
    Returns:
        Dict with 'score' and 'reasoning' keys
    """
    # Get answer from run outputs
    answer = ""
    context = ""
    
    if hasattr(run, 'outputs') and run.outputs:
        answer = run.outputs.get("answer", run.outputs.get("output", str(run.outputs)))
    
    # Try to get context from run inputs or intermediate steps
    if hasattr(run, 'inputs') and run.inputs:
        context = run.inputs.get("context", "")
    
    # If no context available, we can't evaluate faithfulness properly
    if not context:
        return {
            "key": "faithfulness",
            "score": None,
            "reasoning": "No context available to evaluate faithfulness"
        }
    
    result = evaluate_faithfulness(answer, context)
    
    return {
        "key": "faithfulness",
        "score": result.score,
        "reasoning": result.reasoning,
        "metadata": {
            "claims": result.claims,
            "supported": result.supported_claims,
            "unsupported": result.unsupported_claims
        }
    }


if __name__ == "__main__":
    print("=" * 50)
    print("Faithfulness Evaluator Test")
    print("=" * 50)
    
    context = """
    The refund policy allows returns within 30 days of purchase.
    Customers must have their receipt to process a refund.
    Digital products are non-refundable.
    """
    
    test_answers = [
        "Refunds are available within 30 days if you have your receipt. Digital products cannot be refunded.",
        "Refunds are available within 60 days for all products including digital ones.",
        "I don't have enough information to answer that question."
    ]
    
    for i, answer in enumerate(test_answers, 1):
        print(f"\n--- Test {i} ---")
        print(f"Answer: {answer}")
        result = evaluate_faithfulness(answer, context)
        print(f"Score: {result.score}")
        print(f"Reasoning: {result.reasoning}")
