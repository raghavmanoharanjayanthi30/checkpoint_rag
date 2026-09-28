from retrieve import get_documents, format_docs

def generate_answer(question):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda
    
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

    from langchain_openai import ChatOpenAI
    from langsmith import traceable
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    from pydantic import BaseModel
    from typing import Literal
    
    class RAGResponse(BaseModel):
        answer: str
        sources: list[str]
        confidence: Literal["low", "medium", "high"]
    
    structured_llm = llm.with_structured_output(RAGResponse)
    
    # Helper to format docs
    def format_docs(docs):
        return "\n\n".join(
            f"[DOC_ID: {doc.metadata.get('id')}]\n{doc.page_content}"
            for doc in docs
        )
    
    # LCEL Chain
    rag_chain = (
        {
            "context": RunnableLambda(get_documents) | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        }
        | prompt
        | structured_llm
    )
    
    # Use it
    response = rag_chain.invoke(question)
    return response