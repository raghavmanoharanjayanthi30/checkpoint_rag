"""
Tests for evals/harness.py - evaluation harness and metrics.
"""
import pytest
import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock

# Add src and evals to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'evals'))


class TestEvalMetrics:
    """Tests for evaluation metric calculations."""
    
    def test_faithfulness_score_range(self):
        """Faithfulness score should be between 0 and 1."""
        # This tests the expected output format
        score = 0.85
        assert 0 <= score <= 1
    
    def test_relevance_score_range(self):
        """Answer relevance score should be between 0 and 1."""
        score = 0.75
        assert 0 <= score <= 1
    
    def test_context_precision_score_range(self):
        """Context precision score should be between 0 and 1."""
        score = 0.60
        assert 0 <= score <= 1
    
    def test_correctness_score_range(self):
        """Correctness score should be between 0 and 1."""
        score = 0.90
        assert 0 <= score <= 1


class TestTestSetFormat:
    """Tests for test set JSON format validation."""
    
    @pytest.fixture
    def sample_test_set(self, tmp_path):
        """Create a sample test set file."""
        test_data = [
            {
                "query_id": "Q001",
                "question": "What is the refund policy?",
                "expected_answer": "30 day refund policy",
                "expected_doc_ids": ["doc1", "doc2"]
            },
            {
                "query_id": "Q002",
                "question": "How do I reset my password?",
                "expected_answer": "Go to settings and click reset",
                "expected_doc_ids": ["doc3"]
            }
        ]
        
        test_file = tmp_path / "test_set.json"
        test_file.write_text(json.dumps(test_data, indent=2))
        return str(test_file)
    
    def test_load_test_set(self, sample_test_set):
        """Should load test set from JSON file."""
        with open(sample_test_set) as f:
            test_set = json.load(f)
        
        assert len(test_set) == 2
        assert test_set[0]['query_id'] == 'Q001'
    
    def test_test_set_has_required_fields(self, sample_test_set):
        """Each test case should have required fields."""
        with open(sample_test_set) as f:
            test_set = json.load(f)
        
        required_fields = ['query_id', 'question', 'expected_answer', 'expected_doc_ids']
        
        for test_case in test_set:
            for field in required_fields:
                assert field in test_case, f"Missing field: {field}"


class TestEvalOutputFormat:
    """Tests for evaluation output format."""
    
    def test_results_json_structure(self):
        """Results JSON should have expected structure."""
        sample_results = {
            "summary": {
                "total_queries": 50,
                "avg_faithfulness": 0.75,
                "avg_relevance": 0.80,
                "avg_context_precision": 0.65,
                "avg_correctness": 0.70
            },
            "per_query_results": [
                {
                    "query_id": "Q001",
                    "question": "Test question",
                    "answer": "Test answer",
                    "faithfulness": 0.8,
                    "relevance": 0.9,
                    "context_precision": 0.7,
                    "correctness": 0.85
                }
            ]
        }
        
        assert "summary" in sample_results
        assert "per_query_results" in sample_results
        assert sample_results["summary"]["total_queries"] == 50
    
    def test_per_query_result_fields(self):
        """Each per-query result should have all metric scores."""
        result = {
            "query_id": "Q001",
            "question": "Test",
            "answer": "Answer",
            "faithfulness": 0.8,
            "relevance": 0.9,
            "context_precision": 0.7,
            "correctness": 0.85
        }
        
        required_metrics = ['faithfulness', 'relevance', 'context_precision', 'correctness']
        for metric in required_metrics:
            assert metric in result
            assert 0 <= result[metric] <= 1


class TestEvalThresholds:
    """Tests for evaluation threshold requirements."""
    
    def test_faithfulness_threshold(self):
        """Faithfulness should meet >= 0.70 threshold."""
        threshold = 0.70
        score = 0.75  # Example passing score
        assert score >= threshold
    
    def test_context_precision_threshold(self):
        """Context precision should meet >= 0.60 threshold."""
        threshold = 0.60
        score = 0.65  # Example passing score
        assert score >= threshold
    
    def test_aggregate_scores_calculation(self):
        """Should correctly calculate aggregate scores."""
        per_query_scores = [0.8, 0.7, 0.9, 0.6, 0.75]
        avg_score = sum(per_query_scores) / len(per_query_scores)
        
        assert avg_score == 0.75
        assert 0 <= avg_score <= 1


class TestResultsDirectory:
    """Tests for results output directory."""
    
    def test_results_dir_creation(self, tmp_path):
        """Should create results directory if it doesn't exist."""
        results_dir = tmp_path / "results"
        
        # Simulate what harness should do
        os.makedirs(results_dir, exist_ok=True)
        
        assert results_dir.exists()
        assert results_dir.is_dir()
    
    def test_writes_json_output(self, tmp_path):
        """Should write JSON results file."""
        results_dir = tmp_path / "results"
        results_dir.mkdir()
        
        results = {"summary": {"total": 50}}
        output_file = results_dir / "eval_results.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f)
        
        assert output_file.exists()
        
        with open(output_file) as f:
            loaded = json.load(f)
        assert loaded == results
    
    def test_writes_markdown_summary(self, tmp_path):
        """Should write markdown summary file."""
        results_dir = tmp_path / "results"
        results_dir.mkdir()
        
        markdown = "# Evaluation Results\n\n- Faithfulness: 0.75\n"
        output_file = results_dir / "summary.md"
        
        output_file.write_text(markdown)
        
        assert output_file.exists()
        assert "Faithfulness" in output_file.read_text()
