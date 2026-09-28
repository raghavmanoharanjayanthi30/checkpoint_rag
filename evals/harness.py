"""
Evaluation Harness for RAG Pipeline

Runs evaluation on test queries and outputs:
- JSON results with per-query scores
- Markdown summary
- CSV and Parquet DataFrames

Metrics:
- Faithfulness: Is the answer grounded in retrieved context?
- Answer Relevance: Does the answer address the question?
- Context Precision: Are the right documents retrieved?
- Correctness: Does the answer match the ground truth?
"""
import os
import sys
import json
import argparse
from datetime import datetime
from typing import Literal

import pandas as pd
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Add src to path for imports (works for both direct and module execution)
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from retrieve import get_documents, format_docs, create_bm25_retriever
from generate import create_rag_chain
from ingest import get_file_paths, create_langchain_documents, chunk_documents, embed_chunks

load_dotenv()


# ============================================
# PYDANTIC MODELS FOR STRUCTURED EVALUATION
# ============================================

class FaithfulnessResult(BaseModel):
    claims: list[str]
    supported_claims: list[str]
    unsupported_claims: list[str]
    score: float
    reasoning: str


class RelevanceResult(BaseModel):
    question_intent: str
    answer_addresses_intent: bool
    completeness: Literal["full", "partial", "none"]
    score: float
    reasoning: str


class CorrectnessResult(BaseModel):
    key_facts_required: list[str]
    key_facts_found: list[str]
    key_facts_missing: list[str]
    score: float
    reasoning: str


# ============================================
# EVALUATOR SETUP
# ============================================

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
faithfulness_llm = llm.with_structured_output(FaithfulnessResult)
relevance_llm = llm.with_structured_output(RelevanceResult)
correctness_llm = llm.with_structured_output(CorrectnessResult)


# ============================================
# EVALUATOR FUNCTIONS
# ============================================

def evaluate_faithfulness(answer: str, context: str) -> FaithfulnessResult:
    """Check if answer is grounded in the retrieved context."""
    prompt = f"""Evaluate if the answer is faithful to the provided context.
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
    
    return faithfulness_llm.invoke(prompt)


def evaluate_relevance(question: str, answer: str) -> RelevanceResult:
    """Check if answer addresses the question."""
    prompt = f"""Evaluate if the answer is relevant to the question.

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
    
    return relevance_llm.invoke(prompt)


def evaluate_correctness(answer: str, ground_truth: str, notes: str) -> CorrectnessResult:
    """Check if answer contains the key facts from ground truth."""
    prompt = f"""Evaluate if the answer contains the key facts from the ground truth.

<ground_truth_answer>
{ground_truth}
</ground_truth_answer>

<scoring_notes>
{notes}
</scoring_notes>

<generated_answer>
{answer}
</generated_answer>

Instructions:
1. Extract the key facts required from ground_truth and scoring_notes
2. Check which key facts are present in the generated answer
3. Score = len(key_facts_found) / len(key_facts_required)
4. Be lenient on phrasing — if the meaning is correct, count it as found
5. If no key facts required, score = 1.0

Return key_facts_required, key_facts_found, key_facts_missing, score, and reasoning."""
    
    return correctness_llm.invoke(prompt)


def evaluate_context_precision(expected_sources: list[str], retrieved_docs: list) -> dict:
    """
    Context Precision with ranking (RAGAS-style).
    Rewards relevant docs appearing at top positions.
    """
    def normalize(path: str) -> str:
        path = path.lower()
        for prefix in ['product-docs/', 'runbooks/', 'tickets/']:
            if prefix in path:
                idx = path.find(prefix)
                return path[idx:]
        return path
    
    expected_norm = set(normalize(s) for s in expected_sources)
    retrieved_sources = [doc.metadata.get('source', '') for doc in retrieved_docs]
    retrieved_norm = [normalize(s) for s in retrieved_sources]
    
    # Calculate precision with ranking
    relevant_at_k = []
    running_relevant = 0
    precisions = []
    seen_expected = set()  # Track which expected sources we've already counted
    
    for k, source in enumerate(retrieved_norm, start=1):
        if source in expected_norm and source not in seen_expected:
            seen_expected.add(source)
            running_relevant += 1
            precision_at_k = running_relevant / k
            precisions.append(precision_at_k)
            relevant_at_k.append(k)
    
    # Average precision normalized by expected count
    if len(expected_norm) == 0:
        score = 1.0
    elif len(precisions) == 0:
        score = 0.0
    else:
        score = sum(precisions) / len(expected_norm)
    
    # Clamp to [0, 1] just in case
    score = min(max(score, 0.0), 1.0)
    
    matched = set(retrieved_norm) & expected_norm
    
    return {
        "score": round(score, 3),
        "expected": list(expected_norm),
        "retrieved": retrieved_norm,
        "matched": list(matched),
        "relevant_positions": relevant_at_k,
        "reasoning": f"Found {len(matched)}/{len(expected_norm)} expected sources at positions {relevant_at_k}"
    }


# ============================================
# MARKDOWN SUMMARY GENERATOR
# ============================================

def generate_markdown_summary(output: dict) -> str:
    """Generate human-readable markdown summary."""
    agg = output["aggregate_scores"]
    results = output["per_query_results"]
    meta = output["metadata"]
    
    md = f"""# RAG Evaluation Summary

**Generated:** {meta["timestamp"]}  
**Queries Evaluated:** {meta["num_queries"]}  
**Sample Size:** {meta.get("sample_size") or "All"}  
**Generation Model:** {meta["model"]}  
**Embedding Model:** {meta["embedding_model"]}

---

## Aggregate Scores

| Metric | Score | Target | Status |
|--------|-------|--------|--------|
| Faithfulness | {agg['faithfulness']:.3f} | ≥ 0.70 | {"✅ PASS" if agg['faithfulness'] >= 0.70 else "❌ FAIL"} |
| Answer Relevance | {agg['answer_relevance']:.3f} | — | — |
| Context Precision | {agg['context_precision']:.3f} | ≥ 0.60 | {"✅ PASS" if agg['context_precision'] >= 0.60 else "❌ FAIL"} |
| Correctness | {agg['correctness']:.3f} | — | — |

---

## Score Distribution

### By Category
"""
    
    # Group by category
    categories = {}
    for r in results:
        cat = r.get("category", "unknown")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(r)
    
    md += "\n| Category | Count | Avg Faith. | Avg Relev. | Avg Prec. | Avg Correct. |\n"
    md += "|----------|-------|------------|------------|-----------|-------------|\n"
    
    for cat, items in sorted(categories.items()):
        avg_f = sum(r["faithfulness"]["score"] for r in items) / len(items)
        avg_r = sum(r["answer_relevance"]["score"] for r in items) / len(items)
        avg_p = sum(r["context_precision"]["score"] for r in items) / len(items)
        avg_c = sum(r["correctness"]["score"] for r in items) / len(items)
        md += f"| {cat} | {len(items)} | {avg_f:.2f} | {avg_r:.2f} | {avg_p:.2f} | {avg_c:.2f} |\n"

    # By Difficulty
    md += "\n### By Difficulty\n"
    difficulties = {}
    for r in results:
        diff = r.get("difficulty", "unknown")
        if diff not in difficulties:
            difficulties[diff] = []
        difficulties[diff].append(r)
    
    md += "\n| Difficulty | Count | Avg Faith. | Avg Relev. | Avg Prec. | Avg Correct. |\n"
    md += "|------------|-------|------------|------------|-----------|-------------|\n"
    
    for diff, items in sorted(difficulties.items()):
        avg_f = sum(r["faithfulness"]["score"] for r in items) / len(items)
        avg_r = sum(r["answer_relevance"]["score"] for r in items) / len(items)
        avg_p = sum(r["context_precision"]["score"] for r in items) / len(items)
        avg_c = sum(r["correctness"]["score"] for r in items) / len(items)
        md += f"| {diff} | {len(items)} | {avg_f:.2f} | {avg_r:.2f} | {avg_p:.2f} | {avg_c:.2f} |\n"
    
    md += "\n---\n\n## Per-Query Results\n\n"
    md += "| ID | Query | Faith. | Relev. | Prec. | Correct. |\n"
    md += "|----|-------|--------|--------|-------|----------|\n"
    
    for r in results:
        query_short = r["query"][:35] + "..." if len(r["query"]) > 35 else r["query"]
        md += f"| {r['id']} | {query_short} | {r['faithfulness']['score']:.2f} | {r['answer_relevance']['score']:.2f} | {r['context_precision']['score']:.2f} | {r['correctness']['score']:.2f} |\n"
    
    # Low-scoring queries
    md += "\n---\n\n## ⚠️ Low-Scoring Queries (any metric < 0.5)\n\n"
    
    low_scores = [r for r in results if 
                  r["faithfulness"]["score"] < 0.5 or 
                  r["context_precision"]["score"] < 0.5 or
                  r["correctness"]["score"] < 0.5]
    
    if low_scores:
        for r in low_scores:
            md += f"### {r['id']}: {r['query']}\n\n"
            md += f"**Generated Answer:** {r.get('generated_answer', 'N/A')[:300]}...\n\n"
            md += f"**Ground Truth:** {r.get('ground_truth', 'N/A')[:300]}...\n\n"
            md += f"| Metric | Score | Details |\n"
            md += f"|--------|-------|--------|\n"
            md += f"| Faithfulness | {r['faithfulness']['score']:.2f} | {r['faithfulness'].get('reasoning', '')[:100]} |\n"
            md += f"| Context Precision | {r['context_precision']['score']:.2f} | Matched: {r['context_precision'].get('matched', [])} |\n"
            md += f"| Correctness | {r['correctness']['score']:.2f} | Missing: {r['correctness'].get('key_facts_missing', [])} |\n"
            md += "\n---\n\n"
    else:
        md += "None! All queries scored ≥ 0.5 on all metrics. 🎉\n"
    
    # Future improvements
    md += """
---

## Future Improvements

**Answer Relevance:** Current implementation uses direct LLM judgment. Could be improved with RAGAS-style approach:
1. Generate hypothetical questions the answer would address
2. Compute semantic similarity between generated and original questions
3. Average similarity scores

This would make the metric more robust and less dependent on LLM judgment variability.
"""
    
    return md


# ============================================
# MAIN EVALUATION HARNESS
# ============================================

def run_eval_harness(
    test_set_path: str,
    output_dir: str = "results",
    sample_size: int = None,
    corpus_path: str = None,
    vectorstore=None,
    bm25_retriever=None,
    rag_chain=None
):
    """
    Run evaluation on queries and output JSON + Markdown + DataFrame.
    
    Args:
        test_set_path: Path to test_set.json
        output_dir: Directory to save output files
        sample_size: Number of queries to evaluate (None = all)
        corpus_path: Path to corpus for building pipeline (if not providing vectorstore)
        vectorstore: Pre-built vectorstore (optional)
        bm25_retriever: Pre-built BM25 retriever (optional)
        rag_chain: Pre-built RAG chain (optional)
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Build pipeline if not provided
    if rag_chain is None:
        if corpus_path is None:
            # Default to ./corpus when running from checkpoint_rag root
            corpus_path = "./corpus"
        
        print(f"Building pipeline from corpus: {corpus_path}")
        file_grouping = get_file_paths(corpus_path)
        docs = create_langchain_documents(file_grouping)
        chunks = chunk_documents(docs)
        vectorstore = embed_chunks(chunks)
        bm25_retriever = create_bm25_retriever(chunks)
        rag_chain = create_rag_chain(vectorstore, bm25_retriever)
    
    # Load test set
    with open(test_set_path) as f:
        data = json.load(f)
    
    results = []  # For JSON output
    df_rows = []  # For DataFrame output
    
    queries = data["queries"]
    if sample_size is not None:
        test_queries = queries[:sample_size]
    else:
        test_queries = queries
    
    total = len(test_queries)
    print(f"Running evaluation on {total} queries" + (f" (sample of {sample_size})" if sample_size else "") + "...")
    
    for i, item in enumerate(test_queries):
        print(f"[{i+1}/{total}] Evaluating: {item['id']} - {item['query'][:50]}...")
        
        try:
            # Run RAG pipeline
            docs = get_documents(item["query"], vectorstore, bm25_retriever)
            context = format_docs(docs)
            response = rag_chain.invoke(item["query"])
            
            # Get retrieved sources in normalized format
            retrieved_sources = [doc.metadata.get('source', '') for doc in docs]
            retrieved_sources_norm = []
            for s in retrieved_sources:
                for prefix in ['product-docs/', 'runbooks/', 'tickets/']:
                    if prefix in s.lower():
                        idx = s.lower().find(prefix)
                        retrieved_sources_norm.append(s[idx:])
                        break
            
            # Evaluate all 4 metrics
            faith = evaluate_faithfulness(response.answer, context)
            relevance = evaluate_relevance(item["query"], response.answer)
            precision = evaluate_context_precision(item["expected_sources"], docs)
            correctness = evaluate_correctness(
                response.answer, 
                item["ground_truth_answer"], 
                item.get("notes", "")
            )
            
            # Build result dict (for JSON)
            result = {
                "id": item["id"],
                "query": item["query"],
                "category": item.get("category", ""),
                "difficulty": item.get("difficulty", ""),
                "generated_answer": response.answer,
                "ground_truth": item["ground_truth_answer"],
                "sources_used": response.sources,
                "faithfulness": {
                    "score": faith.score,
                    "claims": faith.claims,
                    "supported": faith.supported_claims,
                    "unsupported": faith.unsupported_claims,
                    "reasoning": faith.reasoning
                },
                "answer_relevance": {
                    "score": relevance.score,
                    "completeness": relevance.completeness,
                    "reasoning": relevance.reasoning
                },
                "context_precision": precision,
                "correctness": {
                    "score": correctness.score,
                    "key_facts_required": correctness.key_facts_required,
                    "key_facts_found": correctness.key_facts_found,
                    "key_facts_missing": correctness.key_facts_missing,
                    "reasoning": correctness.reasoning
                }
            }
            results.append(result)
            
            # Build DataFrame row (flat structure)
            df_row = {
                # Query Info
                "query_id": item["id"],
                "query": item["query"],
                "category": item.get("category", ""),
                "difficulty": item.get("difficulty", ""),
                "notes": item.get("notes", ""),
                "ground_truth_answer": item["ground_truth_answer"],
                "expected_sources": " | ".join(item["expected_sources"]),
                
                # RAG Output
                "generated_answer": response.answer,
                "retrieved_sources": " | ".join(retrieved_sources_norm),
                "sources_used_by_llm": " | ".join(response.sources) if response.sources else "",
                "confidence": response.confidence,
                
                # Metric Scores
                "faithfulness_score": faith.score,
                "relevance_score": relevance.score,
                "precision_score": precision["score"],
                "correctness_score": correctness.score,
                
                # Faithfulness Details
                "faithfulness_claims": " | ".join(faith.claims),
                "faithfulness_supported": " | ".join(faith.supported_claims),
                "faithfulness_unsupported": " | ".join(faith.unsupported_claims),
                "faithfulness_reasoning": faith.reasoning,
                
                # Relevance Details
                "relevance_intent": relevance.question_intent,
                "relevance_addresses_intent": relevance.answer_addresses_intent,
                "relevance_completeness": relevance.completeness,
                "relevance_reasoning": relevance.reasoning,
                
                # Precision Details
                "precision_matched_sources": " | ".join(precision["matched"]),
                "precision_missing_sources": " | ".join(set(precision["expected"]) - set(precision["matched"])),
                "precision_relevant_positions": str(precision["relevant_positions"]),
                
                # Correctness Details
                "correctness_key_facts_required": " | ".join(correctness.key_facts_required),
                "correctness_key_facts_found": " | ".join(correctness.key_facts_found),
                "correctness_key_facts_missing": " | ".join(correctness.key_facts_missing),
                "correctness_reasoning": correctness.reasoning,
                
                # Computed Flags
                "sources_match": precision["score"] == 1.0,
                "is_faithful": faith.score >= 0.7,
                "is_correct": correctness.score >= 0.7,
                "all_metrics_pass": (faith.score >= 0.7 and precision["score"] >= 0.6)
            }
            df_rows.append(df_row)
            
            print(f"    ✓ Faith: {faith.score:.2f} | Relev: {relevance.score:.2f} | Prec: {precision['score']:.2f} | Correct: {correctness.score:.2f}")
            
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            results.append({
                "id": item["id"],
                "query": item["query"],
                "error": str(e),
                "faithfulness": {"score": 0},
                "answer_relevance": {"score": 0},
                "context_precision": {"score": 0},
                "correctness": {"score": 0}
            })
            df_rows.append({
                "query_id": item["id"],
                "query": item["query"],
                "error": str(e),
                "faithfulness_score": 0,
                "relevance_score": 0,
                "precision_score": 0,
                "correctness_score": 0
            })
    
    # Calculate aggregates
    avg_faithfulness = sum(r["faithfulness"]["score"] for r in results) / len(results)
    avg_relevance = sum(r["answer_relevance"]["score"] for r in results) / len(results)
    avg_precision = sum(r["context_precision"]["score"] for r in results) / len(results)
    avg_correctness = sum(r["correctness"]["score"] for r in results) / len(results)
    
    # Build JSON output
    output = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "num_queries": len(results),
            "sample_size": sample_size,
            "model": "gpt-4o-mini",
            "embedding_model": "text-embedding-3-small"
        },
        "aggregate_scores": {
            "faithfulness": round(avg_faithfulness, 3),
            "answer_relevance": round(avg_relevance, 3),
            "context_precision": round(avg_precision, 3),
            "correctness": round(avg_correctness, 3)
        },
        "thresholds": {
            "faithfulness": {"target": 0.70, "passed": avg_faithfulness >= 0.70},
            "context_precision": {"target": 0.60, "passed": avg_precision >= 0.60}
        },
        "per_query_results": results
    }
    
    # Create DataFrame
    df = pd.DataFrame(df_rows)
    
    # Save JSON
    json_path = f"{output_dir}/eval_results.json"
    with open(json_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n✅ JSON saved to: {json_path}")
    
    # Save Markdown
    md_path = f"{output_dir}/eval_summary.md"
    markdown = generate_markdown_summary(output)
    with open(md_path, "w") as f:
        f.write(markdown)
    print(f"✅ Markdown saved to: {md_path}")
    
    # Save DataFrame as CSV
    csv_path = f"{output_dir}/eval_details.csv"
    df.to_csv(csv_path, index=False)
    print(f"✅ CSV saved to: {csv_path}")
    
    # Save DataFrame as Parquet
    parquet_path = f"{output_dir}/eval_details.parquet"
    df.to_parquet(parquet_path, index=False)
    print(f"✅ Parquet saved to: {parquet_path}")
    
    # Print summary
    print("\n" + "="*50)
    print("EVALUATION COMPLETE")
    print("="*50)
    print(f"Faithfulness:      {avg_faithfulness:.3f} (target: ≥0.70) {'✅' if avg_faithfulness >= 0.70 else '❌'}")
    print(f"Answer Relevance:  {avg_relevance:.3f}")
    print(f"Context Precision: {avg_precision:.3f} (target: ≥0.60) {'✅' if avg_precision >= 0.60 else '❌'}")
    print(f"Correctness:       {avg_correctness:.3f}")
    
    return output, df


def main():
    parser = argparse.ArgumentParser(description="RAG Evaluation Harness")
    parser.add_argument("--test-set", default="evals/test_set.json", help="Path to test_set.json")
    parser.add_argument("--output-dir", default="evals/results", help="Output directory")
    parser.add_argument("--sample-size", type=int, default=None, help="Number of queries to evaluate")
    parser.add_argument("--corpus", default="./corpus", help="Path to corpus folder")
    args = parser.parse_args()
    
    run_eval_harness(
        test_set_path=args.test_set,
        output_dir=args.output_dir,
        sample_size=args.sample_size,
        corpus_path=args.corpus
    )


if __name__ == "__main__":
    main()
