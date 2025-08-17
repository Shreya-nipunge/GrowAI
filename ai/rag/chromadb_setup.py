import os
import sys
import shutil
import logging
from typing import List, Iterable

from dotenv import load_dotenv

# LangChain core
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.chains import RetrievalQA
from langchain_core.embeddings import Embeddings

# Groq LLM
from langchain_groq import ChatGroq

# Torch/Transformers for custom HF embeddings (no sentence-transformers)
try:
    import torch
    from transformers import AutoTokenizer, AutoModel
except Exception as e:
    AutoTokenizer = None
    AutoModel = None
    torch = None

# =============================
# 0. Logging
# =============================
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# =============================
# 1. Env & Keys
# =============================
load_dotenv()
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "TinyLlama/TinyLlama-1.1B-Chat-v1.0")
# Examples you can use:
#   "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  (lightweight, LLaMA-family)
#   "meta-llama/Llama-3.2-1B"             (requires gated access)
#   "meta-llama/Meta-Llama-3-8B"          (heavy; needs strong GPU)

if HUGGINGFACEHUB_API_TOKEN:
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN
if GROQ_API_KEY:
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# =============================
# 2. Paths (edit as needed)
# =============================
DATA_PATH = r"D:\\Codes\\Krishimitra\\GrowAI\\ai\\rag\\data"
CHROMA_DB_PATH = r"D:\\Codes\\Krishimitra\\GrowAI\\ai\\rag\\chroma_db"

# =============================
# 3. Robust file loading & splitting
# =============================

def load_and_split_documents(data_path: str = DATA_PATH,
                             chunk_size: int = 1700,
                             chunk_overlap: int = 50):
    """Walk all subfolders, load .pdf and .txt with per-file error handling, then split."""
    documents = []
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"DATA_PATH does not exist: {data_path}")

    for root, _, files in os.walk(data_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                if file.lower().endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                elif file.lower().endswith(".txt"):
                    loader = TextLoader(file_path, encoding="utf-8")
                else:
                    continue
                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Loaded: {file_path} ({len(docs)} docs)")
            except Exception as e:
                logger.warning(f"Skipping {file_path} due to error: {e}")

    if not documents:
        logger.warning("No documents found. Check DATA_PATH and file types (.pdf/.txt).")

    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(documents)
    logger.info(f"Split into {len(chunks)} chunks (size={chunk_size}, overlap={chunk_overlap})")
    return chunks

# =============================
# 4. Custom HF LLaMA-style Embeddings (no sentence-transformers)
# =============================

class HFLLamaEmbeddings(Embeddings):
    """
    Minimal embeddings wrapper using any Hugging Face causal LM (e.g., LLaMA/TinyLlama).
    It mean-pools last hidden states to produce fixed-size vectors.

    Notes:
    - Quality won't match dedicated embedding models, but avoids sentence-transformers entirely.
    - Heavy models require a capable GPU; we auto-fallback to CPU if CUDA isn't available.
    """

    def __init__(self,
                 model_name: str = EMBEDDING_MODEL,
                 device: str | None = None,
                 max_length: int = 1024,
                 batch_size: int = 8):
        if AutoTokenizer is None or AutoModel is None:
            raise ImportError("transformers and torch are required for HFLLamaEmbeddings. Install them first.")

        self.model_name = model_name
        self.max_length = max_length
        self.batch_size = batch_size

        # Device
        if device:
            self.device = device
        else:
            if torch and torch.cuda.is_available():
                self.device = "cuda"
            elif torch and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"

        # Load
        auth_token = os.getenv("HUGGINGFACEHUB_API_TOKEN", None)
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=auth_token)
        except TypeError:
            # transformers>=4.39 deprecates use_auth_token
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, token=auth_token)

        try:
            self.model = AutoModel.from_pretrained(model_name, torch_dtype=torch.float16 if self.device == "cuda" else None)
        except Exception:
            # Some models don't support float16; fallback to default dtype
            self.model = AutoModel.from_pretrained(model_name)

        self.model.to(self.device)
        self.model.eval()

    def _encode(self, texts: List[str]) -> List[List[float]]:
        out_vectors: List[List[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            enc = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt",
            )
            enc = {k: v.to(self.device) for k, v in enc.items()}
            with torch.no_grad():
                outputs = self.model(**enc, output_hidden_states=False)
                # outputs.last_hidden_state: [B, T, H]
                hidden = outputs.last_hidden_state
                # Mean pool using attention mask
                mask = enc["attention_mask"].unsqueeze(-1).expand(hidden.size()).float()
                masked_hidden = hidden * mask
                summed = masked_hidden.sum(dim=1)
                counts = mask.sum(dim=1).clamp(min=1e-9)
                mean_pooled = summed / counts
                vecs = mean_pooled.detach().cpu().float().tolist()
                out_vectors.extend(vecs)
        return out_vectors

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # Chroma expects List[List[float]]
        return self._encode(texts)

    def embed_query(self, text: str) -> List[float]:
        return self._encode([text])[0]

# =============================
# 5. Create / Load Vector Store
# =============================

def create_vectorstore(chunks, persist_directory: str = CHROMA_DB_PATH, embedding_model: str = EMBEDDING_MODEL):
    if os.path.exists(persist_directory) and not os.listdir(persist_directory):
        # Exists but empty -> clean it to avoid Chroma errors
        shutil.rmtree(persist_directory, ignore_errors=True)

    os.makedirs(persist_directory, exist_ok=True)

    try:
        embeddings = HFLLamaEmbeddings(model_name=embedding_model)
        logger.info(f"Embeddings model ready: {embedding_model}")
    except Exception as e:
        logger.error(f"Failed to initialize embeddings model '{embedding_model}': {e}")
        raise

    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
    )
    vectordb.persist()
    logger.info(f"Vector store created at: {persist_directory}")
    return vectordb


def load_vectorstore(persist_directory: str = CHROMA_DB_PATH):
    if not os.path.exists(persist_directory):
        raise FileNotFoundError(f"Chroma directory not found: {persist_directory}")

    try:
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=HFLLamaEmbeddings())
        # embedding_function is required at load time for similarity queries
        return vectordb
    except Exception as e:
        logger.error(f"Error loading Chroma DB: {e}")
        raise

# =============================
# 6. QA Chain
# =============================

def setup_qa_chain(vectordb: Chroma, model_name: str = "llama3-70b-8192", k: int = 4):
    retriever = vectordb.as_retriever(search_kwargs={"k": k})
    try:
        llm = ChatGroq(model=model_name, temperature=0)
    except Exception as e:
        logger.error(f"Failed to initialize Groq model '{model_name}': {e}")
        raise

    try:
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
        )
    except Exception as e:
        logger.error(f"Failed to create RetrievalQA chain: {e}")
        raise
    return qa_chain

# =============================
# 7. CLI / Main
# =============================

def build_or_load_db(rebuild: bool = False):
    if rebuild and os.path.exists(CHROMA_DB_PATH):
        logger.info("Rebuilding requested: clearing existing Chroma DB...")
        shutil.rmtree(CHROMA_DB_PATH, ignore_errors=True)

    if not os.path.exists(CHROMA_DB_PATH):
        logger.info("📂 Creating vector store…")
        chunks = load_and_split_documents()
        vectordb = create_vectorstore(chunks)
    else:
        logger.info("📂 Loading existing vector store…")
        vectordb = load_vectorstore()
    return vectordb


def main():
    # Basic sanity checks
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY is empty. Set it in your .env for ChatGroq to work.")
    if AutoTokenizer is None or AutoModel is None:
        logger.error("transformers/torch not available. Install: pip install transformers torch --upgrade")
        sys.exit(1)

    # Optional flags
    rebuild = "--rebuild" in sys.argv

    try:
        vectordb = build_or_load_db(rebuild=rebuild)
        qa_chain = setup_qa_chain(vectordb)
        logger.info("✅ Chroma DB + QA Chain ready for Agentic RAG queries!")
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

