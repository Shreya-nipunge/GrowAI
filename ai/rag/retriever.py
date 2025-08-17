# retriever.py
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

CHROMA_DB_PATH = r"D:\Codes\Krishimitra\GrowAI\ai\rag\chroma_db"

def get_retriever():
    """Load existing Chroma DB and return a retriever."""
    if not os.path.exists(CHROMA_DB_PATH):
        raise FileNotFoundError("❌ Chroma vector DB not found. Run chromadb_setup.py first.")
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    vectordb = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=embeddings   # pass the embeddings here!
    )

    retriever = vectordb.as_retriever()
    return retriever
