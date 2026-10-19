"""
Great Expectations Data Quality Suite

Defines expectations for the RAG corpus and ingestion pipeline:
1. Chunk length distribution
2. Metadata completeness
3. Embedding dimension consistency
4. No detected PII patterns
"""
import re
from typing import List, Dict, Any


# PII Patterns
PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone": r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b',
    "ssn": r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',
    "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
}


class ChunkExpectations:
    """Expectations for document chunks."""
    
    def __init__(
        self,
        min_chunk_length: int = 100,
        max_chunk_length: int = 1500,
        required_metadata_fields: List[str] = None,
        embedding_dimension: int = 1536
    ):
        self.min_chunk_length = min_chunk_length
        self.max_chunk_length = max_chunk_length
        self.required_metadata_fields = required_metadata_fields or ["id", "source", "doc_type"]
        self.embedding_dimension = embedding_dimension
    
    def expect_chunk_length_in_range(self, chunks: List) -> Dict[str, Any]:
        """Check that chunk lengths are within expected range."""
        results = {
            "expectation": "chunk_length_in_range",
            "success": True,
            "details": {
                "min_expected": self.min_chunk_length,
                "max_expected": self.max_chunk_length,
                "violations": []
            }
        }
        
        for i, chunk in enumerate(chunks):
            content = chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
            length = len(content)
            
            if length < self.min_chunk_length:
                results["details"]["violations"].append({
                    "index": i,
                    "length": length,
                    "issue": "too_short"
                })
                results["success"] = False
            elif length > self.max_chunk_length:
                results["details"]["violations"].append({
                    "index": i,
                    "length": length,
                    "issue": "too_long"
                })
                results["success"] = False
        
        results["details"]["total_chunks"] = len(chunks)
        results["details"]["violation_count"] = len(results["details"]["violations"])
        
        return results
    
    def expect_metadata_completeness(self, chunks: List) -> Dict[str, Any]:
        """Check that all required metadata fields are present."""
        results = {
            "expectation": "metadata_completeness",
            "success": True,
            "details": {
                "required_fields": self.required_metadata_fields,
                "violations": []
            }
        }
        
        for i, chunk in enumerate(chunks):
            metadata = chunk.metadata if hasattr(chunk, 'metadata') else {}
            missing_fields = []
            
            for field in self.required_metadata_fields:
                if field not in metadata or metadata[field] is None:
                    missing_fields.append(field)
            
            if missing_fields:
                results["details"]["violations"].append({
                    "index": i,
                    "missing_fields": missing_fields
                })
                results["success"] = False
        
        results["details"]["total_chunks"] = len(chunks)
        results["details"]["violation_count"] = len(results["details"]["violations"])
        
        return results
    
    def expect_no_empty_chunks(self, chunks: List) -> Dict[str, Any]:
        """Check that no chunks are empty."""
        results = {
            "expectation": "no_empty_chunks",
            "success": True,
            "details": {"empty_indices": []}
        }
        
        for i, chunk in enumerate(chunks):
            content = chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
            if not content or not content.strip():
                results["details"]["empty_indices"].append(i)
                results["success"] = False
        
        results["details"]["total_chunks"] = len(chunks)
        results["details"]["empty_count"] = len(results["details"]["empty_indices"])
        
        return results
    
    def expect_no_pii(self, chunks: List) -> Dict[str, Any]:
        """Check that chunks don't contain PII patterns."""
        results = {
            "expectation": "no_pii_detected",
            "success": True,
            "details": {
                "patterns_checked": list(PII_PATTERNS.keys()),
                "violations": []
            }
        }
        
        for i, chunk in enumerate(chunks):
            content = chunk.page_content if hasattr(chunk, 'page_content') else str(chunk)
            
            for pii_type, pattern in PII_PATTERNS.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    results["details"]["violations"].append({
                        "index": i,
                        "pii_type": pii_type,
                        "match_count": len(matches),
                        # Don't include actual matches for privacy
                        "sample": f"[REDACTED - {len(matches)} matches]"
                    })
                    results["success"] = False
        
        results["details"]["total_chunks"] = len(chunks)
        results["details"]["violation_count"] = len(results["details"]["violations"])
        
        return results
    
    def expect_valid_doc_types(self, chunks: List, valid_types: List[str] = None) -> Dict[str, Any]:
        """Check that doc_type metadata is valid."""
        valid_types = valid_types or ["ticket", "runbook", "product-doc"]
        
        results = {
            "expectation": "valid_doc_types",
            "success": True,
            "details": {
                "valid_types": valid_types,
                "violations": []
            }
        }
        
        for i, chunk in enumerate(chunks):
            metadata = chunk.metadata if hasattr(chunk, 'metadata') else {}
            doc_type = metadata.get("doc_type")
            
            if doc_type not in valid_types:
                results["details"]["violations"].append({
                    "index": i,
                    "doc_type": doc_type
                })
                results["success"] = False
        
        results["details"]["total_chunks"] = len(chunks)
        results["details"]["violation_count"] = len(results["details"]["violations"])
        
        return results


class EmbeddingExpectations:
    """Expectations for embeddings."""
    
    def __init__(self, expected_dimension: int = 1536):
        self.expected_dimension = expected_dimension
    
    def expect_embedding_dimension(self, embeddings: List[List[float]]) -> Dict[str, Any]:
        """Check that all embeddings have the expected dimension."""
        results = {
            "expectation": "embedding_dimension_consistency",
            "success": True,
            "details": {
                "expected_dimension": self.expected_dimension,
                "violations": []
            }
        }
        
        for i, embedding in enumerate(embeddings):
            dim = len(embedding)
            if dim != self.expected_dimension:
                results["details"]["violations"].append({
                    "index": i,
                    "actual_dimension": dim
                })
                results["success"] = False
        
        results["details"]["total_embeddings"] = len(embeddings)
        results["details"]["violation_count"] = len(results["details"]["violations"])
        
        return results


def run_all_expectations(chunks: List, embeddings: List[List[float]] = None) -> Dict[str, Any]:
    """
    Run all expectations and return a summary.
    
    Args:
        chunks: List of document chunks
        embeddings: Optional list of embeddings
    
    Returns:
        Dict with all expectation results
    """
    chunk_expectations = ChunkExpectations()
    
    results = {
        "chunk_length": chunk_expectations.expect_chunk_length_in_range(chunks),
        "metadata_completeness": chunk_expectations.expect_metadata_completeness(chunks),
        "no_empty_chunks": chunk_expectations.expect_no_empty_chunks(chunks),
        "no_pii": chunk_expectations.expect_no_pii(chunks),
        "valid_doc_types": chunk_expectations.expect_valid_doc_types(chunks)
    }
    
    if embeddings:
        embedding_expectations = EmbeddingExpectations()
        results["embedding_dimension"] = embedding_expectations.expect_embedding_dimension(embeddings)
    
    # Summary
    all_passed = all(r["success"] for r in results.values())
    passed_count = sum(1 for r in results.values() if r["success"])
    
    results["summary"] = {
        "all_passed": all_passed,
        "passed": passed_count,
        "failed": len(results) - passed_count - 1,  # -1 for summary itself
        "total": len(results) - 1
    }
    
    return results


if __name__ == "__main__":
    # Test with sample data
    from langchain_core.documents import Document
    
    sample_chunks = [
        Document(
            page_content="This is a valid chunk with enough content to pass the minimum length requirement.",
            metadata={"id": "123", "source": "test.md", "doc_type": "product-doc"}
        ),
        Document(
            page_content="Short",  # Too short
            metadata={"id": "456", "source": "test2.md", "doc_type": "ticket"}
        ),
        Document(
            page_content="Contact us at test@example.com for help.",  # Has PII
            metadata={"id": "789", "source": "test3.md", "doc_type": "runbook"}
        ),
    ]
    
    results = run_all_expectations(sample_chunks)
    
    print("=" * 50)
    print("Data Quality Expectations Test")
    print("=" * 50)
    
    for name, result in results.items():
        if name == "summary":
            continue
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {result['expectation']}")
        if not result["success"]:
            print(f"    Violations: {result['details'].get('violation_count', 'N/A')}")
    
    print(f"\nSummary: {results['summary']['passed']}/{results['summary']['total']} passed")
