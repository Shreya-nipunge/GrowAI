import os
from dotenv import load_dotenv
from groq import Groq
from retriever import retrieve

# --- Load environment ---
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# --- Core retrieval-augmented generation pipeline ---

def rag_pipeline(query, k=3, model="llama-3.1-70b-versatile"):
    """
    1. Retrieves relevant context from vector DB.
    2. Calls LLM with both context and the original query.
    3. Returns the LLM answer and context chunks used.
    """
    # Step 1: Retrieve top-k context
    results = retrieve(query, k=k)
    context = "\n\n".join([r["content"] for r in results])

    # Step 2: Create prompt
    prompt = f"""
You are an agricultural assistant.
Answer the user query using only the context below.
If context is not sufficient, say you do not know instead of making things up.

Context:
{context}

Query:
{query}

Answer:
"""

    # Step 3: Call LLM
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant for agriculture Q&A."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
    )
    answer = completion.choices[0].message["content"]

    return {
        "query": query,
        "context_used": results,
        "answer": answer
    }


# --- CLI Demo ---

if __name__ == "__main__":
    user_query = input("Ask your agricultural question: ").strip()
    response = rag_pipeline(user_query)
    print("\n---\nAnswer:")
    print(response["answer"])
    print("\nContext chunks (used for answer):")
    for i, res in enumerate(response["context_used"], 1):
        print(f"\n{i}. {res['content'][:300]}...")
