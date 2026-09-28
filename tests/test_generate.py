"""
Tests for generate.py - RAG chain and structured generation.
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generate import RAGResponse, create_rag_chain, generate_answer


class TestRAGResponse:
    """Tests for the RAGResponse Pydantic model."""
    
    def test_valid_response(self):
        """Should accept valid response data."""
        response = RAGResponse(
            answer="This is the answer.",
            sources=["doc1", "doc2"],
            confidence="high"
        )
        
        assert response.answer == "This is the answer."
        assert response.sources == ["doc1", "doc2"]
        assert response.confidence == "high"
    
    def test_confidence_literal_values(self):
        """Should only accept low, medium, high for confidence."""
        # Valid values
        for conf in ["low", "medium", "high"]:
            response = RAGResponse(answer="test", sources=[], confidence=conf)
            assert response.confidence == conf
    
    def test_invalid_confidence_rejected(self):
        """Should reject invalid confidence values."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            RAGResponse(answer="test", sources=[], confidence="very high")
    
    def test_empty_sources_allowed(self):
        """Should allow empty sources list."""
        response = RAGResponse(answer="I don't know.", sources=[], confidence="low")
        assert response.sources == []
    
    def test_required_fields(self):
        """Should require all fields."""
        from pydantic import ValidationError
        
        with pytest.raises(ValidationError):
            RAGResponse(answer="test")  # Missing sources and confidence


class TestCreateRagChain:
    """Tests for RAG chain creation."""
    
    @patch('generate.ChatOpenAI')
    @patch('generate.get_documents')
    @patch('generate.format_docs')
    def test_chain_is_callable(self, mock_format, mock_get_docs, mock_llm):
        """Should return a callable chain."""
        from langchain_core.documents import Document
        
        # Setup mocks
        mock_vectorstore = Mock()
        mock_bm25 = Mock()
        mock_get_docs.return_value = [Document(page_content="test", metadata={"id": "1"})]
        mock_format.return_value = "[DOC_ID: 1]\ntest"
        
        # Mock LLM to return structured output
        mock_structured = Mock()
        mock_structured.invoke.return_value = RAGResponse(
            answer="Test answer",
            sources=["1"],
            confidence="high"
        )
        mock_llm.return_value.with_structured_output.return_value = mock_structured
        
        chain = create_rag_chain(mock_vectorstore, mock_bm25)
        
        # Chain should be invokable
        assert hasattr(chain, 'invoke')
    
    @patch('generate.ChatOpenAI')
    def test_uses_gpt4o_mini(self, mock_llm):
        """Should use gpt-4o-mini model."""
        mock_vectorstore = Mock()
        mock_bm25 = Mock()
        
        mock_llm.return_value.with_structured_output.return_value = Mock()
        
        create_rag_chain(mock_vectorstore, mock_bm25)
        
        mock_llm.assert_called_once_with(model="gpt-4o-mini", temperature=0)
    
    @patch('generate.ChatOpenAI')
    def test_uses_structured_output(self, mock_llm):
        """Should configure LLM for structured output."""
        mock_vectorstore = Mock()
        mock_bm25 = Mock()
        
        mock_llm_instance = Mock()
        mock_llm.return_value = mock_llm_instance
        
        create_rag_chain(mock_vectorstore, mock_bm25)
        
        mock_llm_instance.with_structured_output.assert_called_once_with(RAGResponse)


class TestGenerateAnswer:
    """Tests for the generate_answer function."""
    
    def test_invokes_chain_with_question(self):
        """Should invoke the chain with the question."""
        mock_chain = Mock()
        mock_chain.invoke.return_value = RAGResponse(
            answer="The answer is 42.",
            sources=["doc1"],
            confidence="high"
        )
        
        result = generate_answer("What is the answer?", mock_chain)
        
        mock_chain.invoke.assert_called_once_with("What is the answer?")
        assert result.answer == "The answer is 42."
    
    def test_returns_rag_response(self):
        """Should return a RAGResponse object."""
        mock_chain = Mock()
        expected_response = RAGResponse(
            answer="Test",
            sources=["s1", "s2"],
            confidence="medium"
        )
        mock_chain.invoke.return_value = expected_response
        
        result = generate_answer("question", mock_chain)
        
        assert isinstance(result, RAGResponse)
        assert result == expected_response


class TestIntegration:
    """Integration tests for the generation pipeline."""
    
    @pytest.mark.skipif(
        not os.environ.get('OPENAI_API_KEY'),
        reason="OPENAI_API_KEY not set"
    )
    def test_end_to_end_generation(self):
        """End-to-end test with real LLM (requires API key)."""
        from langchain_core.documents import Document
        
        # Create mock retrievers that return real documents
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = [
            Document(
                page_content="The refund policy allows returns within 30 days.",
                metadata={"id": "policy1"}
            )
        ]
        
        mock_bm25 = Mock()
        mock_bm25.invoke.return_value = []
        
        chain = create_rag_chain(mock_vectorstore, mock_bm25)
        response = generate_answer("What is the refund policy?", chain)
        
        assert isinstance(response, RAGResponse)
        assert len(response.answer) > 0
        assert response.confidence in ["low", "medium", "high"]
