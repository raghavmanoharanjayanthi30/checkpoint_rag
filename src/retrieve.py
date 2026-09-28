from langchain_community.retrievers import BM25Retriever


def create_bm25_retriever(chunks):
    """Create a BM25 retriever from document chunks."""
    return BM25Retriever.from_documents(chunks)


def get_documents(query, vectorstore, bm25_retriever, k=3):
    """
    Hybrid retrieval: combine vector similarity search and BM25 results.
    Deduplicates by document ID.
    """
    vector_results = vectorstore.similarity_search(query, k=k)
    bm25_results = bm25_retriever.invoke(query)

    seen_ids = set()
    combined = []
    for doc in vector_results + bm25_results:
        doc_id = doc.metadata.get('id')
        if doc_id and doc_id not in seen_ids:
            seen_ids.add(doc_id)
            combined.append(doc)

    return combined


def format_docs(docs):
    """Format documents for inclusion in LLM prompt."""
    return "\n\n".join(
        f"[DOC_ID: {doc.metadata.get('id')}]\n{doc.page_content}"
        for doc in docs
    )
