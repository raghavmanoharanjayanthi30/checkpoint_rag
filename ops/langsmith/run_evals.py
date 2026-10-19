"""
Run Evaluations with LangSmith

This script:
1. Enables LangSmith tracing
2. Loads the eval dataset (or creates from test_set.json)
3. Runs the RAG pipeline on each example
4. Evaluates with faithfulness, relevance, and actionability
5. Logs all results to LangSmith
"""
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

load_dotenv()

from langsmith import Client
from langsmith.evaluation import evaluate

from ops.langsmith.setup import setup_tracing, get_langsmith_client, create_or_get_dataset
from ops.langsmith.evaluators.faithfulness import evaluate_faithfulness_simple
from ops.langsmith.evaluators.answer_relevance import evaluate_relevance_simple
from ops.langsmith.evaluators.custom_judge import evaluate_actionability_simple

# Import RAG components
from src.retrieve import get_documents, format_docs, create_bm25_retriever
from src.generate import create_rag_chain
from src.ingest import get_file_paths, create_langchain_documents, chunk_documents, embed_chunks


def build_rag_pipeline(corpus_path: str = "./corpus"):
    """Build the RAG pipeline components."""
    print("Building RAG pipeline...")
    file_grouping = get_file_paths(corpus_path)
    docs = create_langchain_documents(file_grouping)
    chunks = chunk_documents(docs)
    vectorstore = embed_chunks(chunks)
    bm25_retriever = create_bm25_retriever(chunks)
    rag_chain = create_rag_chain(vectorstore, bm25_retriever)
    print("✅ RAG pipeline ready")
    return rag_chain, vectorstore, bm25_retriever


def run_rag_and_evaluate(question: str, rag_chain, vectorstore, bm25_retriever) -> dict:
    """
    Run RAG pipeline and return results with context for evaluation.
    """
    # Get documents for context
    docs = get_documents(question, vectorstore, bm25_retriever)
    context = format_docs(docs)
    
    # Run RAG chain
    response = rag_chain.invoke(question)
    
    return {
        "question": question,
        "answer": response.answer,
        "sources": response.sources,
        "confidence": response.confidence,
        "context": context,
        "retrieved_docs": [doc.metadata.get('source', '') for doc in docs]
    }


def evaluate_single(result: dict) -> dict:
    """Run all evaluators on a single result."""
    question = result["question"]
    answer = result["answer"]
    context = result["context"]
    
    # Run evaluators
    faithfulness_score = evaluate_faithfulness_simple(answer, context)
    relevance_score = evaluate_relevance_simple(question, answer)
    actionability_score = evaluate_actionability_simple(question, answer)
    
    return {
        "faithfulness": faithfulness_score,
        "answer_relevance": relevance_score,
        "actionability": actionability_score
    }


def run_eval_suite(
    test_set_path: str = "evals/test_set.json",
    corpus_path: str = "./corpus",
    sample_size: int = None,
    output_dir: str = "ops/langsmith/results"
):
    """
    Run full evaluation suite with LangSmith logging.
    
    Args:
        test_set_path: Path to test_set.json
        corpus_path: Path to corpus folder
        sample_size: Number of queries to evaluate (None = all)
        output_dir: Directory for local output files
    """
    # Setup
    setup_tracing()
    client = get_langsmith_client()
    
    # Build pipeline
    rag_chain, vectorstore, bm25_retriever = build_rag_pipeline(corpus_path)
    
    # Load test set
    with open(test_set_path) as f:
        data = json.load(f)
    
    queries = data.get("queries", [])
    if sample_size:
        queries = queries[:sample_size]
    
    print(f"\n📊 Running evaluation on {len(queries)} queries...")
    
    results = []
    scores = {
        "faithfulness": [],
        "answer_relevance": [],
        "actionability": []
    }
    
    for i, item in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] {item['query'][:50]}...")
        
        try:
            # Run RAG
            result = run_rag_and_evaluate(
                item["query"], 
                rag_chain, 
                vectorstore, 
                bm25_retriever
            )
            
            # Evaluate
            eval_scores = evaluate_single(result)
            
            # Store results
            result_entry = {
                "id": item.get("id", f"Q{i:03d}"),
                "query": item["query"],
                "category": item.get("category", ""),
                "difficulty": item.get("difficulty", ""),
                "generated_answer": result["answer"],
                "ground_truth": item.get("ground_truth_answer", ""),
                "sources_used": result["sources"],
                "confidence": result["confidence"],
                "scores": eval_scores
            }
            results.append(result_entry)
            
            # Track scores
            for metric, score in eval_scores.items():
                scores[metric].append(score)
            
            print(f"    Faith: {eval_scores['faithfulness']:.2f} | "
                  f"Relev: {eval_scores['answer_relevance']:.2f} | "
                  f"Action: {eval_scores['actionability']:.2f}")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            results.append({
                "id": item.get("id", f"Q{i:03d}"),
                "query": item["query"],
                "error": str(e)
            })
    
    # Calculate aggregates
    aggregates = {}
    for metric, metric_scores in scores.items():
        if metric_scores:
            aggregates[metric] = sum(metric_scores) / len(metric_scores)
        else:
            aggregates[metric] = 0.0
    
    # Build output
    output = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "num_queries": len(results),
            "sample_size": sample_size,
            "langsmith_project": os.getenv("LANGSMITH_PROJECT", "checkpoint-rag-ops")
        },
        "aggregate_scores": aggregates,
        "per_query_results": results
    }
    
    # Save locally
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/eval_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n✅ Results saved to: {output_path}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("EVALUATION SUMMARY")
    print("=" * 50)
    print(f"Faithfulness:      {aggregates['faithfulness']:.3f}")
    print(f"Answer Relevance:  {aggregates['answer_relevance']:.3f}")
    print(f"Actionability:     {aggregates['actionability']:.3f}")
    print(f"\n📊 View traces at: https://smith.langchain.com")
    
    return output


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run LangSmith Evaluations")
    parser.add_argument("--test-set", default="evals/test_set.json", help="Path to test_set.json")
    parser.add_argument("--corpus", default="./corpus", help="Path to corpus folder")
    parser.add_argument("--sample-size", type=int, default=None, help="Number of queries to evaluate")
    parser.add_argument("--output-dir", default="ops/langsmith/results", help="Output directory")
    args = parser.parse_args()
    
    run_eval_suite(
        test_set_path=args.test_set,
        corpus_path=args.corpus,
        sample_size=args.sample_size,
        output_dir=args.output_dir
    )
