"""
Run Data Quality Validations

Executes the Great Expectations suite on the corpus and writes a report.
"""
import os
import sys
import json
from datetime import datetime

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
load_dotenv()

from ops.data_quality.expectations import run_all_expectations, ChunkExpectations
from src.ingest import get_file_paths, create_langchain_documents, chunk_documents


def run_validations(corpus_path: str = "./corpus", output_dir: str = "ops/data_quality/results"):
    """
    Run all data quality validations on the corpus.
    
    Args:
        corpus_path: Path to corpus folder
        output_dir: Directory for output reports
    """
    print("=" * 50)
    print("Data Quality Validation")
    print("=" * 50)
    
    # Load and process corpus
    print("\n📂 Loading corpus...")
    file_grouping = get_file_paths(corpus_path)
    
    total_files = sum(len(files) for files in file_grouping.values())
    print(f"   Found {total_files} files")
    for file_type, files in file_grouping.items():
        print(f"   - {file_type}: {len(files)} files")
    
    # Create documents
    print("\n📄 Creating documents...")
    docs = create_langchain_documents(file_grouping)
    print(f"   Created {len(docs)} documents")
    
    # Chunk documents
    print("\n✂️  Chunking documents...")
    chunks = chunk_documents(docs)
    print(f"   Created {len(chunks)} chunks")
    
    # Run expectations
    print("\n🔍 Running expectations...")
    results = run_all_expectations(chunks)
    
    # Print results
    print("\n" + "=" * 50)
    print("RESULTS")
    print("=" * 50)
    
    for name, result in results.items():
        if name == "summary":
            continue
        
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        expectation_name = result.get("expectation", name)
        print(f"\n{status} {expectation_name}")
        
        details = result.get("details", {})
        if "violation_count" in details:
            print(f"   Violations: {details['violation_count']}/{details.get('total_chunks', 'N/A')}")
        
        if not result["success"] and "violations" in details:
            # Show first few violations
            for v in details["violations"][:3]:
                print(f"   - {v}")
            if len(details["violations"]) > 3:
                print(f"   ... and {len(details['violations']) - 3} more")
    
    # Summary
    summary = results["summary"]
    print("\n" + "=" * 50)
    print(f"SUMMARY: {summary['passed']}/{summary['total']} expectations passed")
    print("=" * 50)
    
    # Generate report
    os.makedirs(output_dir, exist_ok=True)
    
    report = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "corpus_path": corpus_path,
            "total_files": total_files,
            "total_documents": len(docs),
            "total_chunks": len(chunks)
        },
        "results": results,
        "summary": {
            "all_passed": summary["all_passed"],
            "passed": summary["passed"],
            "failed": summary["failed"],
            "total": summary["total"]
        }
    }
    
    # Save JSON report
    json_path = f"{output_dir}/validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\n📄 JSON report saved to: {json_path}")
    
    # Save Markdown report
    md_path = f"{output_dir}/validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    md_content = generate_markdown_report(report)
    with open(md_path, "w") as f:
        f.write(md_content)
    print(f"📄 Markdown report saved to: {md_path}")
    
    return report


def generate_markdown_report(report: dict) -> str:
    """Generate a markdown report from validation results."""
    meta = report["metadata"]
    results = report["results"]
    summary = report["summary"]
    
    md = f"""# Data Quality Validation Report

**Generated:** {meta['timestamp']}  
**Corpus:** {meta['corpus_path']}

## Corpus Statistics

| Metric | Value |
|--------|-------|
| Total Files | {meta['total_files']} |
| Total Documents | {meta['total_documents']} |
| Total Chunks | {meta['total_chunks']} |

## Validation Results

| Expectation | Status | Violations |
|-------------|--------|------------|
"""
    
    for name, result in results.items():
        if name == "summary":
            continue
        
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        violations = result.get("details", {}).get("violation_count", 0)
        total = result.get("details", {}).get("total_chunks", "-")
        
        md += f"| {result.get('expectation', name)} | {status} | {violations}/{total} |\n"
    
    md += f"""
## Summary

- **Passed:** {summary['passed']}/{summary['total']}
- **Failed:** {summary['failed']}/{summary['total']}
- **Overall:** {'✅ ALL PASSED' if summary['all_passed'] else '❌ SOME FAILED'}

## Expectation Details

"""
    
    for name, result in results.items():
        if name == "summary":
            continue
        
        if not result["success"]:
            md += f"### ❌ {result.get('expectation', name)}\n\n"
            details = result.get("details", {})
            
            if "violations" in details:
                md += "**Violations:**\n\n"
                for v in details["violations"][:5]:
                    md += f"- {v}\n"
                if len(details["violations"]) > 5:
                    md += f"- ... and {len(details['violations']) - 5} more\n"
            md += "\n"
    
    md += """
## Recommendations

1. **For chunk length violations:** Adjust chunking parameters or review source documents
2. **For metadata issues:** Ensure all loaders add required metadata
3. **For PII detections:** Review and redact sensitive information before indexing
4. **For empty chunks:** Filter out empty chunks during ingestion

---

*Report generated by checkpoint_rag data quality suite*
"""
    
    return md


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Data Quality Validations")
    parser.add_argument("--corpus", default="./corpus", help="Path to corpus folder")
    parser.add_argument("--output-dir", default="ops/data_quality/results", help="Output directory")
    args = parser.parse_args()
    
    run_validations(corpus_path=args.corpus, output_dir=args.output_dir)
