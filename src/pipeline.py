"""
RAG Pipeline - Orchestrates ingestion, retrieval, and generation.
"""
from dotenv import load_dotenv
load_dotenv()

from ingest import get_file_paths, create_langchain_documents, chunk_documents, embed_chunks
from retrieve import create_bm25_retriever, get_documents, format_docs
from generate import create_rag_chain, generate_answer, RAGResponse


class RAGPipeline:
    
    def __init__(self, corpus_path: str = None, vectorstore=None, chunks=None):
        """
        Initialize the pipeline.
        
        Args:
            corpus_path: Path to corpus folder (for fresh ingestion)
            vectorstore: Pre-existing vectorstore (skip ingestion)
            chunks: Pre-existing chunks for BM25 (skip ingestion)
        """
        if vectorstore and chunks:
            # Use existing vectorstore and chunks
            self.vectorstore = vectorstore
            self.chunks = chunks
        elif corpus_path:
            # Run full ingestion
            self.chunks = self._ingest(corpus_path)
            self.vectorstore = embed_chunks(self.chunks)
        else:
            raise ValueError("Must provide either corpus_path or (vectorstore, chunks)")
        
        # Create BM25 retriever from chunks
        self.bm25_retriever = create_bm25_retriever(self.chunks)
        
        # Create the RAG chain
        self.chain = create_rag_chain(self.vectorstore, self.bm25_retriever)
    
    def _ingest(self, corpus_path: str):
        """Load, parse, and chunk documents."""
        file_grouping = get_file_paths(corpus_path)
        docs = create_langchain_documents(file_grouping)
        chunks = chunk_documents(docs)
        return chunks
    
    def query(self, question: str) -> RAGResponse:
        """
        Run a query through the pipeline.
        
        Args:
            question: User's question
            
        Returns:
            RAGResponse with answer, sources, and confidence
        """
        return generate_answer(question, self.chain)
    
    def retrieve(self, question: str, k: int = 3):
        """
        Retrieve relevant documents without generating an answer.
        
        Args:
            question: User's question
            k: Number of results per retriever
            
        Returns:
            List of relevant documents
        """
        return get_documents(question, self.vectorstore, self.bm25_retriever, k=k)


def main():
    """Example usage of the RAG pipeline."""
    import argparse
    
    parser = argparse.ArgumentParser(description="RAG Pipeline")
    parser.add_argument("--corpus", default="./corpus", help="Path to corpus folder")
    parser.add_argument("--query", type=str, help="Question to ask")
    args = parser.parse_args()
    
    # Build pipeline
    print(f"Building pipeline from corpus: {args.corpus}")
    pipeline = RAGPipeline(corpus_path=args.corpus)
    
    if args.query:
        # Run single query
        response = pipeline.query(args.query)
        print(f"\nQuestion: {args.query}")
        print(f"Answer: {response.answer}")
        print(f"Sources: {response.sources}")
        print(f"Confidence: {response.confidence}")
    else:
        # Interactive mode
        print("\nPipeline ready. Enter questions (Ctrl+C to exit):")
        while True:
            try:
                question = input("\n> ")
                if question.strip():
                    response = pipeline.query(question)
                    print(f"Answer: {response.answer}")
                    print(f"Sources: {response.sources}")
                    print(f"Confidence: {response.confidence}")
            except KeyboardInterrupt:
                print("\nExiting.")
                break


if __name__ == "__main__":
    main()
