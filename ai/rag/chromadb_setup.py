import os
from dotenv import load_dotenv
from langchain.vectorstores import Chroma
from groq import Groq

# Load environment
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Paths
CHROMA_DB_PATH = r"D:\Codes\Krishimitra\GrowAI\ai\rag\chroma_db"

# Create a function to embed query with Groq
def embed_query(query: str):
    response = client.embeddings.create(
        input=[query],
        model="text-embedding-3-large"
    )
    return response["data"][0]  # returns embedding vector (list of floats)

# Retrieve top-k documents
def retrieve(query: str, k: int = 5):
    # Load Chroma
    vectordb = Chroma(
        persist_directory=CHROMA_DB_PATH,
        embedding_function=None  # no auto-embedding, we use Groq manually
    )

    # Embed query
    query_embedding = embed_query(query)

    # Do similarity search
    results = vectordb._collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    retrieved = []
    for doc, meta, distance in zip(results["documents"][0],
                                   results["metadatas"],
                                   results["distances"]):
        retrieved.append({
            "content": doc,
            "metadata": meta,
            "score": distance
        })
    return retrieved

# Example usage
if __name__ == "__main__":
    query = "What is sustainable agriculture?"
    results = retrieve(query, k=3)
    print("🔍 Query:", query)
    for i, res in enumerate(results, 1):
        print(f"\nResult {i} (score: {res['score']:.4f}):")
        print(res["content"])
