"""
Tests for ingest.py - document loading, chunking, and embedding.
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from collections import defaultdict

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ingest import get_file_paths, create_langchain_documents, chunk_documents


class TestGetFilePaths:
    """Tests for get_file_paths function."""
    
    def test_returns_defaultdict(self, tmp_path):
        """Should return a defaultdict grouping files by extension."""
        # Create test directory structure
        tickets = tmp_path / "tickets"
        tickets.mkdir()
        (tickets / "ticket1.html").write_text("<html>test</html>")
        
        runbooks = tmp_path / "runbooks"
        runbooks.mkdir()
        (runbooks / "runbook1.pdf").write_bytes(b"%PDF-1.4 test")
        
        product_docs = tmp_path / "product-docs"
        product_docs.mkdir()
        (product_docs / "doc1.md").write_text("# Test")
        
        result = get_file_paths(str(tmp_path))
        
        assert isinstance(result, defaultdict)
        assert 'html' in result
        assert 'pdf' in result
        assert 'md' in result
    
    def test_skips_hidden_files(self, tmp_path):
        """Should skip files starting with '.' like .DS_Store."""
        tickets = tmp_path / "tickets"
        tickets.mkdir()
        (tickets / ".DS_Store").write_text("hidden")
        (tickets / "ticket1.html").write_text("<html>test</html>")
        
        # Create other required folders (empty)
        (tmp_path / "runbooks").mkdir()
        (tmp_path / "product-docs").mkdir()
        
        result = get_file_paths(str(tmp_path))
        
        all_paths = []
        for paths in result.values():
            all_paths.extend(paths)
        
        assert not any('.DS_Store' in p for p in all_paths)
        assert len(result['html']) == 1
    
    def test_handles_nested_folders(self, tmp_path):
        """Should recursively find files in nested folders."""
        runbooks = tmp_path / "runbooks"
        nested = runbooks / "incident-response"
        nested.mkdir(parents=True)
        (nested / "guide.pdf").write_bytes(b"%PDF-1.4 test")
        
        # Create other required folders
        (tmp_path / "tickets").mkdir()
        (tmp_path / "product-docs").mkdir()
        
        result = get_file_paths(str(tmp_path))
        
        assert len(result['pdf']) == 1
        assert 'incident-response' in result['pdf'][0]


class TestChunkDocuments:
    """Tests for chunk_documents function."""
    
    def test_chunks_have_ids(self):
        """Each chunk should have a unique ID in metadata."""
        from langchain_core.documents import Document
        
        docs = [
            Document(page_content="This is a test document with some content.", metadata={"source": "test.txt"}),
            Document(page_content="Another document with different content.", metadata={"source": "test2.txt"})
        ]
        
        chunks = chunk_documents(docs)
        
        for chunk in chunks:
            assert 'id' in chunk.metadata
            assert len(chunk.metadata['id']) == 32  # MD5 hex length
    
    def test_chunk_ids_are_unique(self):
        """Different content should produce different IDs."""
        from langchain_core.documents import Document
        
        docs = [
            Document(page_content="Content A " * 100, metadata={"source": "a.txt"}),
            Document(page_content="Content B " * 100, metadata={"source": "b.txt"})
        ]
        
        chunks = chunk_documents(docs)
        ids = [c.metadata['id'] for c in chunks]
        
        assert len(ids) == len(set(ids)), "Chunk IDs should be unique"
    
    def test_duplicate_content_same_id(self):
        """Identical content should produce the same ID (for deduplication)."""
        from langchain_core.documents import Document
        
        same_content = "This is identical content."
        docs = [
            Document(page_content=same_content, metadata={"source": "a.txt"}),
            Document(page_content=same_content, metadata={"source": "b.txt"})
        ]
        
        chunks = chunk_documents(docs)
        ids = [c.metadata['id'] for c in chunks]
        
        assert ids[0] == ids[1], "Same content should produce same ID"
    
    def test_respects_chunk_size(self):
        """Chunks should not exceed the configured chunk size significantly."""
        from langchain_core.documents import Document
        
        # Create a long document
        long_content = "Word " * 500  # ~2500 characters
        docs = [Document(page_content=long_content, metadata={"source": "long.txt"})]
        
        chunks = chunk_documents(docs)
        
        # Should be split into multiple chunks
        assert len(chunks) > 1
        
        # Each chunk should be roughly within chunk_size (1000) + some overlap
        for chunk in chunks:
            assert len(chunk.page_content) <= 1200  # Allow some buffer


class TestCreateLangchainDocuments:
    """Tests for create_langchain_documents function."""
    
    @patch('langchain_community.document_loaders.BSHTMLLoader')
    @patch('langchain_community.document_loaders.PyPDFLoader')
    @patch('langchain_community.document_loaders.UnstructuredMarkdownLoader')
    def test_adds_doc_type_metadata(self, mock_md, mock_pdf, mock_html):
        """Should add doc_type metadata based on file source."""
        from langchain_core.documents import Document
        
        # Mock loaders to return documents
        mock_html.return_value.load.return_value = [
            Document(page_content="HTML content", metadata={"source": "/path/tickets/t1.html"})
        ]
        mock_pdf.return_value.load.return_value = [
            Document(page_content="PDF content", metadata={"source": "/path/runbooks/r1.pdf"})
        ]
        mock_md.return_value.load.return_value = [
            Document(page_content="MD content", metadata={"source": "/path/product-docs/p1.md"})
        ]
        
        file_grouping = {
            'html': ['/path/tickets/t1.html'],
            'pdf': ['/path/runbooks/r1.pdf'],
            'md': ['/path/product-docs/p1.md']
        }
        
        docs = create_langchain_documents(file_grouping)
        
        html_doc = next(d for d in docs if 'HTML' in d.page_content)
        pdf_doc = next(d for d in docs if 'PDF' in d.page_content)
        md_doc = next(d for d in docs if 'MD' in d.page_content)
        
        assert html_doc.metadata['doc_type'] == 'ticket'
        assert pdf_doc.metadata['doc_type'] == 'runbook'
        assert md_doc.metadata['doc_type'] == 'product-doc'
    
    @patch('langchain_community.document_loaders.BSHTMLLoader')
    @patch('langchain_community.document_loaders.PyPDFLoader')
    @patch('langchain_community.document_loaders.UnstructuredMarkdownLoader')
    def test_extracts_category_from_path(self, mock_md, mock_pdf, mock_html):
        """Should extract category from nested folder structure."""
        from langchain_core.documents import Document
        
        mock_html.return_value.load.return_value = []
        mock_pdf.return_value.load.return_value = [
            Document(page_content="PDF", metadata={"source": "/corpus/runbooks/incident-response/guide.pdf"})
        ]
        mock_md.return_value.load.return_value = [
            Document(page_content="MD", metadata={"source": "/corpus/product-docs/api/reference.md"})
        ]
        
        file_grouping = {
            'html': [],
            'pdf': ['/corpus/runbooks/incident-response/guide.pdf'],
            'md': ['/corpus/product-docs/api/reference.md']
        }
        
        docs = create_langchain_documents(file_grouping)
        
        pdf_doc = next(d for d in docs if 'PDF' in d.page_content)
        md_doc = next(d for d in docs if 'MD' in d.page_content)
        
        assert pdf_doc.metadata.get('category') == 'incident-response'
        assert md_doc.metadata.get('category') == 'api'
