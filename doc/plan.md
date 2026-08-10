# Phase-wise Implementation Plan

This document outlines a structured, step-by-step plan for upgrading **InsightFlow** into a highly scalable, conversational AI application with a modern UI.

---

## Phase 1: Foundation & LangChain Integration
*Focus: Refactoring the backend AI logic to use LangChain, establishing the base for memory and advanced chunking without touching the UI yet.*

1. **Install LangChain Ecosystem**
   - Install `langchain`, `langchain-community`, `langchain-mongodb`, and related provider packages (e.g., `langchain-cohere`, `langchain-openai`).
2. **Migrate Chunking Strategy**
   - Replace the current fixed-size chunker with LangChain's `RecursiveCharacterTextSplitter`.
   - Test text extraction to ensure chunk boundaries are semantic (paragraph/sentence level).
3. **Wrap FAISS in LangChain**
   - Convert the current custom FAISS logic to use LangChain's `FAISS` vector store abstraction.
4. **Implement Memory (MongoDB)**
   - Create a MongoDB collection for chat histories.
   - Implement `MongoDBChatMessageHistory` to store and retrieve past Q&A turns based on a `session_id`.
5. **Refactor `/ask` Endpoint**
   - Combine the LangChain FAISS retriever and Memory into a `ConversationalRetrievalChain`.
   - Ensure the `/ask` endpoint now requires a `session_id` to maintain conversation state.

---

## Phase 2: Modernizing the Frontend Chat UI
*Focus: Redesigning the `Chats.tsx` page to look and feel like ChatGPT or Gemini.*

1. **Layout & Styling Overhaul**
   - Update `Chats.tsx` to a full-screen height layout (`h-screen`).
   - Create a dedicated, scrollable message container and a fixed bottom input bar.
   - Design distinct chat bubbles for 'User' and 'AI'.
2. **Markdown Support**
   - Install `react-markdown` and `rehype-highlight`.
   - Wrap the AI response text inside the Markdown component so lists, bold text, and code blocks render beautifully.
3. **Session Management**
   - Update the frontend to generate or fetch a unique `session_id` for a document chat.
   - Pass this `session_id` to the `/ask` API so the backend LangChain memory can recognize the user's context.
4. **Auto-Scrolling**
   - Add a `useRef` at the bottom of the message list and trigger `scrollIntoView()` every time the message array updates.

---

## Phase 3: Streaming & Real-Time UX
*Focus: Reducing perceived latency by streaming the LLM response token-by-token.*

1. **Backend: Implement Server-Sent Events (SSE)**
   - Update the FastAPI `/ask` endpoint to use `StreamingResponse`.
   - Configure the LangChain LLM to use a streaming callback handler so it yields words as they are generated.
2. **Frontend: Fetch API & Stream Reading**
   - Replace the Axios `POST /ask` call with the native `fetch` API to support reading streams.
   - Implement a stream reader loop that updates the final message bubble incrementally as chunks arrive from the server.
3. **Loading States**
   - Add a typing indicator (e.g., three bouncing dots) that shows up the moment the user sends a message, and disappears the moment the first streamed token arrives.

---

## Phase 4: Scaling & Advanced Orchestration (Future)
*Focus: Preparing the application for heavy production traffic and multi-agent workflows.*

1. **Migrate Vector DB**
   - Swap FAISS for a distributed vector database like Pinecone, Qdrant, or Milvus to handle massive document scaling.
2. **Asynchronous Task Queues**
   - Implement Celery and Redis.
   - Move document transcription and video downloading out of the FastAPI request cycle into background Celery workers.
3. **LangGraph Workflows**
   - Integrate LangGraph to handle advanced scenarios (e.g., routing questions: if a user asks a general question, skip the vector DB; if they ask about the document, query the vector DB).
