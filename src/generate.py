from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Literal

from retrieve import get_documents, format_docs


class RAGResponse(BaseModel):
    """Structured response from the RAG pipeline."""
    answer: str
    sources: list[str]
    confidence: Literal["low", "medium", "high"]


def create_rag_chain(vectorstore, bm25_retriever):
    """
    Create an LCEL RAG chain with hybrid retrieval.
    
    Args:
        vectorstore: Pinecone vector store for similarity search
        bm25_retriever: BM25 retriever for keyword search
    
    Returns:
        A runnable chain that takes a question and returns RAGResponse
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant who is good at analyzing source information and answering questions.
Use the following source documents to answer the user's questions.
If you don't know the answer, just say that you don't know.
Use three sentences maximum and keep the answer concise.
Return the DOC_IDs of the sources you used in your answer.

<context>
{context}
</context>"""),
        ("user", "{question}")
    ])

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(RAGResponse)

    # Create retriever function with vectorstore and bm25 bound
    def retrieve_and_format(question):
        docs = get_documents(question, vectorstore, bm25_retriever)
        return format_docs(docs)

    # LCEL Chain
    rag_chain = (
        {
            "context": RunnableLambda(retrieve_and_format),
            "question": RunnablePassthrough()
        }
        | prompt
        | structured_llm
    )

    return rag_chain


def generate_answer(question, rag_chain):
    """
    Generate an answer using the RAG chain.
    
    Args:
        question: The user's question
        rag_chain: The LCEL chain created by create_rag_chain()
    
    Returns:
        RAGResponse with answer, sources, and confidence
    """
    return rag_chain.invoke(question)
