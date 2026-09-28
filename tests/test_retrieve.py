"""
Tests for retrieve.py - hybrid retrieval and document formatting.
"""
import pytest
import os
import sys
from unittest.mock import Mock, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from retrieve import get_documents, format_docs, create_bm25_retriever


class TestGetDocuments:
    """Tests for hybrid retrieval function."""
    
    def test_combines_vector_and_bm25_results(self):
        """Should return results from both retrievers."""
        from langchain_core.documents import Document
        
        # Mock vectorstore
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = [
            Document(page_content="Vector result 1", metadata={"id": "v1"}),
            Document(page_content="Vector result 2", metadata={"id": "v2"})
        ]
        
        # Mock BM25 retriever
        mock_bm25 = Mock()
        mock_bm25.invoke.return_value = [
            Document(page_content="BM25 result 1", metadata={"id": "b1"}),
            Document(page_content="BM25 result 2", metadata={"id": "b2"})
        ]
        
        results = get_documents("test query", mock_vectorstore, mock_bm25)
        
        assert len(results) == 4
        ids = [d.metadata['id'] for d in results]
        assert set(ids) == {'v1', 'v2', 'b1', 'b2'}
    
    def test_deduplicates_by_id(self):
        """Should remove duplicate documents based on ID."""
        from langchain_core.documents import Document
        
        # Same document appears in both results
        shared_doc = Document(page_content="Shared content", metadata={"id": "shared"})
        
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = [
            shared_doc,
            Document(page_content="Vector only", metadata={"id": "v1"})
        ]
        
        mock_bm25 = Mock()
        mock_bm25.invoke.return_value = [
            Document(page_content="Shared content", metadata={"id": "shared"}),  # Duplicate
            Document(page_content="BM25 only", metadata={"id": "b1"})
        ]
        
        results = get_documents("test query", mock_vectorstore, mock_bm25)
        
        ids = [d.metadata['id'] for d in results]
        assert len(ids) == 3
        assert ids.count('shared') == 1  # Only one copy of shared doc
    
    def test_preserves_order_vector_first(self):
        """Vector results should come before BM25 results (after dedup)."""
        from langchain_core.documents import Document
        
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = [
            Document(page_content="V1", metadata={"id": "v1"}),
            Document(page_content="V2", metadata={"id": "v2"})
        ]
        
        mock_bm25 = Mock()
        mock_bm25.invoke.return_value = [
            Document(page_content="B1", metadata={"id": "b1"})
        ]
        
        results = get_documents("test", mock_vectorstore, mock_bm25)
        
        ids = [d.metadata['id'] for d in results]
        assert ids == ['v1', 'v2', 'b1']
    
    def test_handles_missing_ids(self):
        """Should skip documents without IDs."""
        from langchain_core.documents import Document
        
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = [
            Document(page_content="Has ID", metadata={"id": "v1"}),
            Document(page_content="No ID", metadata={})  # Missing ID
        ]
        
        mock_bm25 = Mock()
        mock_bm25.invoke.return_value = []
        
        results = get_documents("test", mock_vectorstore, mock_bm25)
        
        # Only the doc with ID should be included
        assert len(results) == 1
        assert results[0].metadata['id'] == 'v1'
    
    def test_respects_k_parameter(self):
        """Should pass k to similarity_search."""
        mock_vectorstore = Mock()
        mock_vectorstore.similarity_search.return_value = []
        
        mock_bm25 = Mock()
        mock_bm25.invoke.return_value = []
        
        get_documents("test", mock_vectorstore, mock_bm25, k=5)
        
        mock_vectorstore.similarity_search.assert_called_once_with("test", k=5)


class TestFormatDocs:
    """Tests for document formatting function."""
    
    def test_formats_single_doc(self):
        """Should format a single document correctly."""
        from langchain_core.documents import Document
        
        docs = [Document(page_content="Test content", metadata={"id": "abc123"})]
        
        result = format_docs(docs)
        
        assert "[DOC_ID: abc123]" in result
        assert "Test content" in result
    
    def test_formats_multiple_docs(self):
        """Should separate multiple documents with double newlines."""
        from langchain_core.documents import Document
        
        docs = [
            Document(page_content="Content 1", metadata={"id": "id1"}),
            Document(page_content="Content 2", metadata={"id": "id2"})
        ]
        
        result = format_docs(docs)
        
        assert "[DOC_ID: id1]" in result
        assert "[DOC_ID: id2]" in result
        assert "\n\n" in result  # Documents separated
    
    def test_handles_empty_list(self):
        """Should return empty string for empty list."""
        result = format_docs([])
        assert result == ""
    
    def test_handles_missing_id(self):
        """Should handle documents without ID gracefully."""
        from langchain_core.documents import Document
        
        docs = [Document(page_content="No ID doc", metadata={})]
        
        result = format_docs(docs)
        
        assert "[DOC_ID: None]" in result
        assert "No ID doc" in result


class TestCreateBM25Retriever:
    """Tests for BM25 retriever creation."""
    
    def test_creates_retriever_from_chunks(self):
        """Should create a working BM25 retriever."""
        from langchain_core.documents import Document
        
        chunks = [
            Document(page_content="Python programming language", metadata={"id": "1"}),
            Document(page_content="JavaScript web development", metadata={"id": "2"}),
            Document(page_content="Python data science", metadata={"id": "3"})
        ]
        
        retriever = create_bm25_retriever(chunks)
        
        # Should be able to invoke
        results = retriever.invoke("Python")
        
        assert len(results) > 0
        # Python docs should rank higher
        assert any("Python" in doc.page_content for doc in results[:2])
