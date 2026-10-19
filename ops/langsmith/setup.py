"""
LangSmith Setup - Initialize tracing and evaluation infrastructure

This module sets up LangSmith for:
1. Tracing all LangChain calls (retrieval, generation)
2. Creating/managing evaluation datasets
3. Running evaluations with results logged to LangSmith
"""
import os
from dotenv import load_dotenv
from langsmith import Client

load_dotenv()


def get_langsmith_client() -> Client:
    """Initialize and return LangSmith client."""
    api_key = os.getenv("LANGSMITH_API_KEY")
    if not api_key:
        raise ValueError("LANGSMITH_API_KEY not set in environment")
    return Client(api_key=api_key)


def setup_tracing(project_name: str = None):
    """
    Enable LangSmith tracing for all LangChain calls.
    
    Args:
        project_name: Optional project name. Defaults to LANGSMITH_PROJECT env var.
    """
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    
    project = project_name or os.getenv("LANGSMITH_PROJECT", "checkpoint-rag-ops")
    os.environ["LANGCHAIN_PROJECT"] = project
    
    print(f"✅ LangSmith tracing enabled for project: {project}")
    return project


def create_or_get_dataset(client: Client, dataset_name: str, description: str = None):
    """
    Create a new dataset or get existing one.
    
    Args:
        client: LangSmith client
        dataset_name: Name of the dataset
        description: Optional description
    
    Returns:
        Dataset object
    """
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"📂 Using existing dataset: {dataset_name}")
    except Exception:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description=description or f"Evaluation dataset for {dataset_name}"
        )
        print(f"📂 Created new dataset: {dataset_name}")
    return dataset


def upload_examples_to_dataset(client: Client, dataset_name: str, examples: list):
    """
    Upload examples to a LangSmith dataset.
    
    Args:
        client: LangSmith client
        dataset_name: Name of the dataset
        examples: List of dicts with 'inputs' and 'outputs' keys
            Example: [
                {
                    "inputs": {"question": "What is the refund policy?"},
                    "outputs": {"answer": "Refunds within 30 days...", "sources": [...]}
                }
            ]
    """
    dataset = create_or_get_dataset(client, dataset_name)
    
    inputs = [ex["inputs"] for ex in examples]
    outputs = [ex.get("outputs") for ex in examples]
    
    client.create_examples(
        dataset_id=dataset.id,
        inputs=inputs,
        outputs=outputs
    )
    print(f"✅ Uploaded {len(examples)} examples to {dataset_name}")


def load_test_set_to_langsmith(client: Client, test_set_path: str, dataset_name: str = "csm-support-eval"):
    """
    Load existing test_set.json into LangSmith dataset.
    
    Args:
        client: LangSmith client
        test_set_path: Path to test_set.json
        dataset_name: Name for the LangSmith dataset
    """
    import json
    
    with open(test_set_path) as f:
        data = json.load(f)
    
    examples = []
    for query in data.get("queries", []):
        examples.append({
            "inputs": {
                "question": query["query"],
                "category": query.get("category", ""),
                "difficulty": query.get("difficulty", "")
            },
            "outputs": {
                "ground_truth_answer": query["ground_truth_answer"],
                "expected_sources": query.get("expected_sources", []),
                "notes": query.get("notes", "")
            }
        })
    
    upload_examples_to_dataset(client, dataset_name, examples)
    return len(examples)


if __name__ == "__main__":
    # Test setup
    print("=" * 50)
    print("LangSmith Setup Test")
    print("=" * 50)
    
    # Enable tracing
    project = setup_tracing()
    
    # Initialize client
    client = get_langsmith_client()
    print(f"✅ LangSmith client initialized")
    
    # Show project URL
    print(f"\n📊 View traces at: https://smith.langchain.com/o/default/projects/p/{project}")
