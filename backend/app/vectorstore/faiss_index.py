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

from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever

# 🔹 Search FAISS index by question using Hybrid Search (EnsembleRetriever)
async def search_faiss_by_document(document_id: str, query: str, top_k: int = 5) -> List[dict]:
    index_path = os.path.join(INDEX_DIR, document_id)
    
    if not os.path.exists(index_path):
        return []

    # Load the vectorstore
    vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    
    # Create FAISS retriever
    faiss_retriever = vectorstore.as_retriever(search_kwargs={"k": top_k})
    
    # Reconstruct documents for BM25 retriever
    all_docs = list(vectorstore.docstore._dict.values())
    if not all_docs:
        return []
        
    bm25_retriever = BM25Retriever.from_documents(all_docs)
    bm25_retriever.k = top_k
    
    # Combine both retrievers with equal weighting
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, faiss_retriever], weights=[0.5, 0.5]
    )
    
    # Perform hybrid search
    results = ensemble_retriever.invoke(query)
    
    # Limit to top_k and format
    formatted_results = []
    for doc in results[:top_k]:
        formatted_results.append({
            "text": doc.page_content,
            "distance": 0.0 # Distance isn't easily extracted from EnsembleRetriever
        })
        
    return formatted_results
