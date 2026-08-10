# Project Improvements & Future Scope

This document outlines ways to improve the project, enhance its performance, modernize the frontend UI, and integrate advanced AI orchestration tools. It also covers strategic technical tweaks recommended for scaling.

## 1. General Project Improvements & Strategy Tweaks

### Vector Database Strategy
- **Current**: In-memory FAISS.
- **Tweak**: FAISS is perfect for small-scale apps and MVPs. However, as user uploads scale, memory will become a bottleneck. **Recommendation**: Plan a future migration to a managed, distributed vector database like **Pinecone, Qdrant, or Milvus**. LangChain makes swapping vector databases a 1-line code change.

### Chunking Strategy
- **Current**: Fixed-size character chunking (500 characters, 50 overlap).
- **Tweak**: Fixed chunking can sometimes sever a sentence mid-thought, breaking context. **Recommendation**: Implement **Semantic Chunking** or use LangChain's `RecursiveCharacterTextSplitter`. This splits by paragraphs and sentences first, ensuring the chunks remain contextually coherent.

### LLM & Model Strategy
- **Current**: Cohere for embeddings, AI21/Cohere for summarization and Q&A.
- **Tweak**: Keep Cohere's `embed-english-v3.0` as it is state-of-the-art for embeddings. However, for a conversational chatbot feel, consider wiring the Q&A generation up to **OpenAI (GPT-4o), Anthropic (Claude 3.5 Sonnet), or Gemini 1.5 Pro**. They generally offer superior conversational context handling compared to standard completion models.

### Architecture & Performance
- **Streaming Responses**: Instead of standard REST calls where the frontend waits for the entire LLM response, migrate the `/ask` endpoint to use **Server-Sent Events (SSE)** via FastAPI's `StreamingResponse`. This enables real-time token-by-token text generation.
- **Microservices & Task Queues**: Use a message broker like RabbitMQ or Celery for handling heavy asynchronous tasks (e.g., video downloads and transcriptions) outside the main web thread to prevent blocking.
- **Caching**: Implement Redis for caching frequent database queries, repetitive LLM questions, or static document metadata.

---

## 2. Frontend Assessment & UI Upgrades

### What is currently implemented?
Based on `Chats.tsx`, the frontend currently has:
- Document detail viewing (alias, summary, transcription).
- A basic Q&A section where questions and answers are appended in static blocks.
- A basic text input field.
- A button to load all previous QAs (`/qnaAll`).

### How to achieve a ChatGPT/Gemini-style UI
To transform the UI into a modern AI chatbot interface:
1. **Layout**: Adopt a full-height flex layout where the chat area takes up the majority of the screen, and the input box is fixed at the bottom.
2. **Message Bubbles**: Clearly differentiate User messages and AI messages using distinct avatars, background colors, and alignments.
3. **Markdown Rendering**: Use `react-markdown` and `rehype-highlight` so the AI can return formatted text, code blocks, lists, and tables.
4. **Auto-Scrolling**: Use a `useRef` hook attached to the bottom of the chat list to automatically scroll down whenever a new message is added or streamed.
5. **Streaming Integration**: Update Axios calls to use the Fetch API with streaming support (`ReadableStream`), updating the last message character-by-character.
6. **Typing Indicators**: Show a loading animation (e.g., bouncing dots) while waiting for the AI to start responding.

---

## 3. Integrating LangChain / LangGraph

LangChain and LangGraph can significantly simplify and power up the backend AI logic.

### Why LangChain?
LangChain provides pre-built abstractions for RAG pipelines. Instead of manually writing logic to fetch from FAISS, format the prompt, and call LLMs, you can:
- Use `ConversationalRetrievalChain` to automatically handle vector store retrieval and conversational memory.
- Use Prompt Templates for robust, versionable prompts.

### Why LangGraph?
If you want the application to handle multi-step workflows (e.g., "If the user asks for a summary, summarize. If they ask to search the web, search the web"), LangGraph allows you to build cyclic, stateful multi-agent workflows.

---

## 4. Implementing Conversational Memory

Currently, the backend treats each question as isolated, without remembering past context in the same session.

### How to add Memory:
1. **Frontend Changes**:
   - Send a `session_id` or `chat_id` alongside the `document_id` when calling `/ask`.
2. **Backend Changes (with LangChain)**:
   - Use `ConversationBufferMemory`.
   - Store the raw chat history in MongoDB using LangChain's `MongoDBChatMessageHistory`.
   - When a user asks a question, LangChain automatically fetches the past history from MongoDB, prepends it to the prompt, and maintains contextual flow.
