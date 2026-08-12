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

from langchain_community.retrievers import BM25Retriever

# 🔹 Search FAISS index by question using Hybrid Search (Manual RRF)
async def search_faiss_by_document(document_id: str, query: str, top_k: int = 5) -> List[dict]:
    index_path = os.path.join(INDEX_DIR, document_id)
    
    if not os.path.exists(index_path):
        return []

    # Load the vectorstore
    vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    
    # Get FAISS results
    faiss_results = vectorstore.similarity_search(query, k=top_k)
    
    # Reconstruct documents for BM25 retriever
    all_docs = list(vectorstore.docstore._dict.values())
    if not all_docs:
        return []
        
    bm25_retriever = BM25Retriever.from_documents(all_docs)
    bm25_retriever.k = top_k
    bm25_results = bm25_retriever.invoke(query)
    
    # Reciprocal Rank Fusion (RRF)
    doc_scores = {}
    
    for rank, doc in enumerate(faiss_results):
        doc_scores[doc.page_content] = doc_scores.get(doc.page_content, 0.0) + (1.0 / (rank + 60))
        
    for rank, doc in enumerate(bm25_results):
        doc_scores[doc.page_content] = doc_scores.get(doc.page_content, 0.0) + (1.0 / (rank + 60))
        
    # Sort by RRF score descending
    sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
    
    # Limit to top_k and format
    formatted_results = []
    for text, score in sorted_docs[:top_k]:
        formatted_results.append({
            "text": text,
            "distance": score 
        })
        
    return formatted_results
