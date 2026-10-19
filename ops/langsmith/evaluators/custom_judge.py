"""
Custom LLM-as-Judge Evaluator: Actionability

Measures whether the RAG response gives a CSM a clear, actionable next step.

This is CSM-specific because:
- CSMs need to quickly resolve customer issues
- Vague answers waste time even if technically correct
- Good answers include specific steps, links, or actions
"""
import os
import sys
from typing import Literal
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


class ActionabilityResult(BaseModel):
    """Structured result from actionability evaluation."""
    score: float
    action_identified: bool
    action_type: Literal["specific_steps", "general_guidance", "information_only", "unclear"]
    reasoning: str


# Initialize evaluator LLM
evaluator_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_evaluator = evaluator_llm.with_structured_output(ActionabilityResult)


ACTIONABILITY_PROMPT = """You are evaluating a support assistant's response for ACTIONABILITY.

A Customer Success Manager (CSM) asked a question and received this response.
Your job is to determine: Can the CSM immediately act on this answer?

<question>
{question}
</question>

<answer>
{answer}
</answer>

Evaluate ACTIONABILITY using this rubric:

SCORE 1.0 - Specific Steps:
- Contains exact steps ("Go to Settings → Billing → Cancel")
- Includes specific links, buttons, or menu paths
- CSM can follow instructions immediately

SCORE 0.75 - General Guidance:
- Provides direction but not exact steps
- CSM knows what to do but needs to figure out details
- Example: "Check the billing settings for the cancellation option"

SCORE 0.5 - Information Only:
- Answers the question with facts
- But doesn't tell CSM what to DO with that information
- Example: "The refund policy is 30 days" (but no next step)

SCORE 0.25 - Unclear:
- Vague or ambiguous response
- CSM would need to ask follow-up questions
- Example: "It depends on the situation"

SCORE 0.0 - Not Actionable:
- Doesn't help the CSM at all
- Off-topic or "I don't know" without guidance

Return your evaluation with:
- score: float between 0 and 1
- action_identified: whether a clear action was found
- action_type: one of "specific_steps", "general_guidance", "information_only", "unclear"
- reasoning: brief explanation of your score
"""


def evaluate_actionability(question: str, answer: str) -> ActionabilityResult:
    """
    Evaluate if the answer provides actionable guidance for a CSM.
    
    Args:
        question: The CSM's question
        answer: The RAG system's response
    
    Returns:
        ActionabilityResult with score, action_type, and reasoning
    """
    prompt = ACTIONABILITY_PROMPT.format(question=question, answer=answer)
    result = structured_evaluator.invoke(prompt)
    return result


def evaluate_actionability_simple(question: str, answer: str) -> float:
    """
    Simple version that just returns the score.
    
    Args:
        question: The CSM's question
        answer: The RAG system's response
    
    Returns:
        Float score between 0 and 1
    """
    result = evaluate_actionability(question, answer)
    return result.score


# LangSmith-compatible evaluator function
def langsmith_actionability_evaluator(run, example) -> dict:
    """
    LangSmith-compatible evaluator function.
    
    Args:
        run: The LangSmith run object (contains model outputs)
        example: The dataset example (contains inputs)
    
    Returns:
        Dict with 'score' and 'reasoning' keys
    """
    question = example.inputs.get("question", "")
    
    # Get answer from run outputs
    answer = ""
    if hasattr(run, 'outputs') and run.outputs:
        answer = run.outputs.get("answer", run.outputs.get("output", str(run.outputs)))
    
    result = evaluate_actionability(question, answer)
    
    return {
        "key": "actionability",
        "score": result.score,
        "reasoning": result.reasoning,
        "metadata": {
            "action_type": result.action_type,
            "action_identified": result.action_identified
        }
    }


if __name__ == "__main__":
    # Test the evaluator
    print("=" * 50)
    print("Actionability Evaluator Test")
    print("=" * 50)
    
    test_cases = [
        {
            "question": "How do I cancel a customer's subscription?",
            "answer": "To cancel a subscription, go to Settings → Billing → Subscriptions, find the customer by email, click the three-dot menu, and select 'Cancel Subscription'. You'll be prompted to select an end date (immediate or end of billing period)."
        },
        {
            "question": "How do I cancel a customer's subscription?",
            "answer": "Subscriptions can be cancelled through the billing settings."
        },
        {
            "question": "How do I cancel a customer's subscription?",
            "answer": "The subscription system supports various billing configurations."
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Q: {case['question']}")
        print(f"A: {case['answer'][:100]}...")
        
        result = evaluate_actionability(case['question'], case['answer'])
        print(f"\nScore: {result.score}")
        print(f"Action Type: {result.action_type}")
        print(f"Reasoning: {result.reasoning}")
