# rag_pipeline.py
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA

def build_rag_chain(retriever, model_name="llama3-70b-8192"):
    """Create RetrievalQA chain with Groq LLM and retriever."""
    llm = ChatGroq(model=model_name, temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain

def query_rag(qa_chain, question):
    """Query the RAG chain."""
    # Use .run() if you only need answer, or .invoke() if want source docs
    result = qa_chain.invoke(question)  # returns dict with keys: result, source_documents
    answer = result.get("result", "")
    context_used = result.get("source_documents", [])
    return answer, context_used
