def get_documents(query, k = 3):
    vector_results = vectorstore.similarity_search(query, k = 3)
    bm25_results = retriever.invoke(query)

    seen_ids = set()
    combined = []
    for doc in vector_results + bm25_results:
        doc_id = doc.metadata.get('id')
        if doc_id not in seen_ids:
            seen_ids.add(doc_id)
            combined.append(doc)

    return combined

def format_docs(docs):
    return "\n\n".join(
        f"[DOC_ID: {doc.metadata.get('id')}]\n{doc.page_content}"
        for doc in docs
    )


