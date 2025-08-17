# rag_pipeline.py
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from GrowAI.ai.rag.retriever import get_retriever

def build_rag_chain(model_name="llama3-70b-8192"):
    """
    Create a RetrievalQA chain using Groq LLM and Chroma retriever.
    """
    # Load retriever from retriever.py
    retriever = get_retriever()

    # Initialize Groq LLM
    llm = ChatGroq(model=model_name, temperature=0)

    # Create RetrievalQA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain

def query_rag(qa_chain, question):
    """
    Query the RAG chain with a question.
    Returns answer and source documents.
    """
    result = qa_chain.invoke({"query": question})  # use dict for consistency
    answer = result.get("result", "")
    context_used = result.get("source_documents", [])
    return answer, context_used


if __name__ == "__main__":
    # Example run
    qa_chain = build_rag_chain()
    question = "What crops are suitable for clay soil?"
    answer, sources = query_rag(qa_chain, question)

    print("\n✅ Answer:", answer)
    print("\n📂 Sources used:")
    for doc in sources:
        print("-", getattr(doc, "metadata", {}).get("source", "Unknown"))
