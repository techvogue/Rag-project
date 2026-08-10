# Architectural Decisions & Technology Choices

This document outlines the core technical and strategic decisions made for InsightFlow. For each major architectural component, we document the chosen technology, the alternative options evaluated during the decision-making process, and the reasoning behind the final choice.

---

## 1. Backend Web Framework
**Decision**: **FastAPI** (Python)
**Options Evaluated**: 
- *Flask*: Simple, but synchronous by default. Retrofitting async is clunky.
- *Django*: Highly opinionated, heavy, and includes many built-in tools (like its ORM) that we don't need for a NoSQL-driven, API-only backend.
- *FastAPI*: Built from the ground up for speed and native asynchronous (`async`/`await`) capabilities.
**Reasoning**:
Handling audio transcription (AssemblyAI), video downloads, and LLM API calls is heavily I/O bound. FastAPI's native asynchronous support ensures that these slow API calls do not block the main event loop. Furthermore, its automatic OpenAPI (Swagger) documentation generation significantly speeds up frontend integration.

---

## 2. Primary Database
**Decision**: **MongoDB** (using Motor/Beanie ODM)
**Options Evaluated**:
- *PostgreSQL / MySQL*: Relational databases are excellent for structured, tabular data.
- *MongoDB*: A NoSQL document database.
**Reasoning**:
InsightFlow deals with unstructured and highly variable data (transcripts, dynamic document metadata, nested Q&A arrays, unknown chat lengths). A NoSQL document structure maps perfectly to this. Additionally, using `Motor` ensures that database interactions remain fully asynchronous, preventing event loop blocking. `Beanie` was chosen as the ODM because it integrates seamlessly with FastAPI's Pydantic models.

---

## 3. Vector Store Database
**Decision**: **FAISS** (Facebook AI Similarity Search) - `IndexFlatL2`
**Options Evaluated**:
- *Pinecone / Milvus / Qdrant*: Dedicated, distributed cloud vector databases.
- *FAISS*: A local, in-memory C++ library for vector similarity search.
**Reasoning**:
For the initial phases of the project, a heavy distributed cloud vector database introduces unnecessary network latency, cost, and DevOps complexity. FAISS runs directly in the backend's memory, offering blazing-fast retrieval speeds at zero infrastructure cost. 
*Note on Future Scaling*: As the application scales to handle massive amounts of documents, FAISS's memory constraints will become a bottleneck. We have structured the code using LangChain to allow a 1-line swap to Pinecone or Qdrant when this time comes.

---

## 4. Chunking Strategy
**Decision**: **Semantic Chunking** (LangChain's `RecursiveCharacterTextSplitter`)
**Options Evaluated**:
- *Fixed-size Character Chunking*: Splitting text strictly every 500 characters. (Initially used).
- *Semantic Chunking*: Splitting text based on natural language boundaries (paragraphs, sentences).
**Reasoning**:
Fixed-size chunking is easy to implement but often severs sentences or thoughts directly in the middle, destroying the semantic context of that chunk. By moving to `RecursiveCharacterTextSplitter`, the text is split on double-newlines (`\n\n`) first, then single newlines, then periods. This ensures that the vectors stored in FAISS represent complete, coherent thoughts, drastically improving the accuracy of the Retrieval-Augmented Generation (RAG) system.

---

## 5. Embedding Model
**Decision**: **Cohere** (`embed-english-v3.0`)
**Options Evaluated**:
- *OpenAI (`text-embedding-3-small`)*: Excellent general-purpose embeddings.
- *Open-source (e.g., SentenceTransformers / HuggingFace)*: Free, but requires hosting and compute power (GPU) on the backend server.
- *Cohere v3*: Specifically designed for retrieval tasks.
**Reasoning**:
Cohere's v3 embedding model was chosen because it explicitly differentiates between document embeddings (`search_document`) and query embeddings (`search_query`). This asymmetric embedding approach optimizes the mathematical vector space specifically for RAG, resulting in superior retrieval accuracy compared to older symmetric models.

---

## 6. Frontend Framework & Tooling
**Decision**: **React 19 with Vite & TypeScript**
**Options Evaluated**:
- *Next.js*: Great for SEO and Server-Side Rendering (SSR).
- *Create React App (CRA)*: The old standard, now deprecated and slow.
- *React + Vite*: Blazing fast build times and Hot Module Replacement (HMR).
**Reasoning**:
InsightFlow is a heavily interactive, authenticated dashboard application where SEO is not a primary concern (users must log in to view their private documents). Therefore, the complexity of Next.js SSR is unwarranted. Vite provides the best developer experience for a Single Page Application (SPA). TypeScript was chosen over plain JavaScript to catch runtime errors at compile-time, especially when dealing with complex data structures from the FastAPI backend.

---

## 7. Real-Time Chat UX (Streaming)
**Decision**: **Server-Sent Events (SSE) / StreamingResponse**
**Options Evaluated**:
- *Standard REST (Wait & Render)*: The frontend sends a request and waits 5-10 seconds for the entire LLM response to generate before rendering it.
- *WebSockets*: Bi-directional communication protocol.
- *Server-Sent Events (SSE)*: Uni-directional stream from server to client.
**Reasoning**:
Modern users expect AI chatbots to type out responses token-by-token (like ChatGPT) to reduce perceived latency. WebSockets were evaluated but deemed overkill since chat generation only requires server-to-client streaming. SSE via FastAPI's `StreamingResponse` and the native JS `fetch` API (`ReadableStream`) provides the exact typing-effect functionality with significantly less overhead than WebSockets.
