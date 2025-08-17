import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA

# -----------------------------
# 1. API Keys
# -----------------------------
load_dotenv()
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# -----------------------------
# 2. Paths
# -----------------------------
DATA_PATH = r"D:\Codes\Krishimitra\GrowAI\ai\rag\data"          # Folder with PDFs/TXTs
CHROMA_DB_PATH = r"D:\Codes\Krishimitra\GrowAI\ai\rag\chroma_db" # Folder to persist vector DB




# -----------------------------
# 4. Load & Split Documents
# -----------------------------
def load_and_split_documents():
    documents = []

    # Walk through all subfolders
    for root, dirs, files in os.walk(DATA_PATH):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file.endswith(".txt"):
                loader = TextLoader(file_path)
            else:
                continue
            documents.extend(loader.load())

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1700, chunk_overlap=50)
    return splitter.split_documents(documents)

# -----------------------------
# 5. Create Chroma Vector Store
# -----------------------------
def create_vectorstore(chunks):
    # Use HuggingFace transformers model directly, no sentence-transformers needed
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    vectordb.persist()
    return vectordb
# -----------------------------
# 6. Setup QA Chain
# -----------------------------
def setup_qa_chain(vectordb, model_name="llama3-70b-8192"):
    retriever = vectordb.as_retriever()
    llm = ChatGroq(model=model_name, temperature=0)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )
    return qa_chain

# -----------------------------
# 7. Main: build or load DB
# -----------------------------
if __name__ == "__main__":
    if not os.path.exists(CHROMA_DB_PATH):
        print("📂 Creating vector store...")
        chunks = load_and_split_documents()
        vectordb = create_vectorstore(chunks)
    else:
        print("📂 Loading existing vector store...")
        # Pass the embeddings here as well
        vectordb = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding=EMBEDDINGS
        )

    qa_chain = setup_qa_chain(vectordb)
    print("✅ Chroma DB + QA Chain ready for Agentic RAG queries!")
