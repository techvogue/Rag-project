# Project Improvements & Future Scope

This document outlines ways to improve the project, enhance its performance, modernize the frontend UI, and integrate advanced AI orchestration tools. It tracks both completed upgrades and future recommendations.

---

## ✅ Completed Improvements

### 1. Semantic Chunking Strategy
- **Previous**: Fixed-size character chunking (500 characters, 50 overlap).
- **Completed Upgrade**: Implemented LangChain's `RecursiveCharacterTextSplitter`. This splits by paragraphs and sentences first, ensuring the chunks remain contextually coherent.

### 2. Conversational Memory
- **Previous**: The backend treated each question as isolated, without remembering past context.
- **Completed Upgrade**: Integrated native conversational memory. The backend now retrieves the last 3 QA interactions from the MongoDB `QADocument` and automatically injects them into the LLM's prompt as chat history.

### 3. Real-Time Chat UX (Streaming)
- **Previous**: Standard REST calls where the frontend waited 5-10 seconds for the entire LLM response.
- **Completed Upgrade**: Migrated the `/ask` endpoint to use **Server-Sent Events (SSE)** via FastAPI's `StreamingResponse`. The React frontend uses the Fetch API (`ReadableStream`) to stream the answer character-by-character for a ChatGPT-style typing effect.

### 4. Modern ChatGPT-Style UI
- **Previous**: Static Q&A blocks, no markdown formatting.
- **Completed Upgrade**: Redesigned `Chats.tsx` with a full-height flex layout, distinct message bubbles, avatars, auto-scrolling (`useRef`), and full Markdown/Code-block rendering using `react-markdown` and `@tailwindcss/typography`.

### 5. Hybrid Search (FAISS + BM25)
- **Previous**: Only semantic vector search (FAISS) was used, which struggled with exact acronyms or part numbers.
- **Completed Upgrade**: Implemented LangChain's `EnsembleRetriever`. The backend now runs FAISS (for concepts) and BM25 (for exact keywords) simultaneously, weighing them equally using Reciprocal Rank Fusion to guarantee the best retrieval.

### 6. Inline Source Citations
- **Previous**: The LLM answered based on context but didn't prove where it got the information.
- **Completed Upgrade**: The LLM prompt now strictly enforces `[Source X]` citations. After the stream finishes, the backend dynamically appends a formatted list of the exact document snippets used for complete transparency.

---

## 🚀 Future Scope & Recommendations (Phase 4+)

### 1. Vector Database Strategy (Scaling)
- **Current**: In-memory FAISS.
- **Recommendation**: FAISS is perfect for small-scale apps and MVPs. However, as user uploads scale, memory will become a bottleneck. Plan a future migration to a managed, distributed vector database like **Pinecone, Qdrant, or Milvus**. LangChain makes swapping vector databases a 1-line code change.

### 2. Microservices & Background Task Queues
- **Current**: Video parsing and transcription happen synchronously or block resources.
- **Recommendation**: Use a message broker like **RabbitMQ, Redis, or Celery** for handling heavy asynchronous tasks (e.g., video downloads and transcriptions) outside the main web thread. This allows returning a `task_id` to the frontend instantly and rendering a progress bar.

### 3. Advanced PDF & Table Parsing (LlamaParse)
- **Current**: Standard text splitters strip out table structures.
- **Recommendation**: Integrate **LlamaParse** or **Unstructured.io** to intelligently parse complex PDFs with charts, graphs, and multi-column layouts into pristine Markdown before chunking.

### 4. LangGraph Agentic Workflows
- **Current**: Linear RAG (Retrieve -> Answer).
- **Recommendation**: Implement **LangGraph** to build cyclic, stateful multi-agent workflows. For example, an agent that decides whether to search the document, search the web, or run a python script based on the user's intent.

### 5. Global / Multi-Document Chat
- **Current**: The user must open a specific document to chat with it.
- **Recommendation**: Add a global chat dashboard where a user can ask a question, and the RAG system searches across their entire personal repository of uploaded documents to synthesize cross-document insights.
