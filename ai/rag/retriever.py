# retriever.py

import os
import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Ensure your API key is available. The setup script will have checked this already.
# It's good practice to handle potential missing keys gracefully.
try:
    openai_api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    print("Error: OPENAI_API_KEY environment variable not set.")
    sys.exit(1) # Exit the script if the key is not found

# Define the paths and collection name used in chromadb_setup.py
# Make sure these match exactly!
# The path is where the vector store data is persisted.
CHROMA_PATH = "D:/Codes/Krishimitra/GrowAI/ai/rag/chroma_db"
# The collection is like a table in a traditional database.
COLLECTION_NAME = "krishimitra_farming"
# The embedding model must be the same one used for generating the embeddings
# to ensure the search works correctly.
EMBEDDING_MODEL = "text-embedding-3-large"

print("--- Initializing Retriever ---")

# Instantiate the embedding function using the same model
# The model is required to convert the user's query into an embedding vector.
try:
    embeddings = OpenAIEmbeddings(
        openai_api_key=openai_api_key,
        model=EMBEDDING_MODEL
    )
    print(f"Successfully initialized embeddings model: {EMBEDDING_MODEL}")
except Exception as e:
    print(f"Error initializing OpenAIEmbeddings: {e}")
    sys.exit(1)

# Load the persisted ChromaDB vector store
# This points to the directory where the collection was saved.
try:
    print(f"Attempting to load ChromaDB from: {CHROMA_PATH}")
    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    print("Successfully loaded ChromaDB vector store.")
except Exception as e:
    print(f"Error loading ChromaDB: {e}")
    sys.exit(1)

# Create a retriever from the vector store
# A retriever is an object that can retrieve documents given a query.
# We'll set k=5 to retrieve the top 5 most relevant documents.
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

def retrieve_documents(query: str):
    """
    Performs a semantic search on the vector store to find relevant documents.

    Args:
        query (str): The user's search query.

    Returns:
        list: A list of Document objects from the vector store.
    """
    print(f"\n--- Retrieving documents for query: '{query}' ---")
    
    try:
        # Use the retriever to find and return the most relevant documents
        # The retriever handles the embedding of the query and the search for us.
        retrieved_docs = retriever.get_relevant_documents(query)

        
        if not retrieved_docs:
            print("No documents found for this query.")
            return []
        
        print(f"Found {len(retrieved_docs)} relevant documents.")
        return retrieved_docs
        
    except Exception as e:
        print(f"An error occurred during retrieval: {e}")
        return []

if __name__ == "__main__":
    # Example usage: Test the retriever with a sample query
    
    # A sample query related to farming
    sample_query = "What are the best soil preparation techniques for farming?"
    
    # Retrieve documents for the sample query
    results = retrieve_documents(sample_query)
    
    # Print the retrieved documents and their metadata
    if results:
        for i, doc in enumerate(results):
            print(f"\n--- Document {i+1} ---")
            print(f"Source: {doc.metadata.get('source', 'N/A')}")
            print(f"Content:\n{doc.page_content[:500]}...") # Print first 500 characters
            
