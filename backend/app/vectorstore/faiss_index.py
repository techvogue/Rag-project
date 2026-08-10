import os
from typing import List
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_cohere import CohereEmbeddings

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
EMBED_MODEL = "embed-english-v3.0"

INDEX_DIR = "app/vectorstore/indexes"
os.makedirs(INDEX_DIR, exist_ok=True)

# Initialize LangChain Cohere Embeddings
embeddings = CohereEmbeddings(
    model=EMBED_MODEL,
    cohere_api_key=COHERE_API_KEY,
)

# 🔹 Generate & Save FAISS index for chunks using LangChain
async def add_document_embeddings(doc_id: str, chunks: List[str]):
    # FAISS.from_texts will automatically embed all chunks and build the index
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embeddings)
    
    # Save the index locally. LangChain saves both the .faiss index and a .pkl file containing the actual text.
    index_path = os.path.join(INDEX_DIR, doc_id)
    vectorstore.save_local(index_path)

# 🔹 Search FAISS index by question using LangChain
async def search_faiss_by_document(document_id: str, query: str, top_k: int = 5) -> List[dict]:
    index_path = os.path.join(INDEX_DIR, document_id)
    
    if not os.path.exists(index_path):
        return []

    # Load the vectorstore. allow_dangerous_deserialization is required for local pickle files.
    vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    
    # Perform similarity search
    results = vectorstore.similarity_search_with_score(query, k=top_k)
    
    formatted_results = []
    for doc, score in results:
        formatted_results.append({
            "text": doc.page_content,
            "distance": float(score)
        })
        
    return formatted_results
