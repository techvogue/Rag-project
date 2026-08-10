# InsightFlow - Project Documentation

## 1. Project Overview and Flow

**InsightFlow** is an intelligent document, audio, and video processing platform. The general flow of the application is as follows:

1. **Upload & Ingestion:** The user uploads a file (PDF, text, audio, video) or provides a URL (like a YouTube link). 
2. **Processing & Extraction:**
   - **Documents:** Text is extracted directly using tools like `textract`.
   - **Audio/Video:** Audio is extracted (if video) using `moviepy` or downloaded from YouTube using `yt-dlp`. The audio is then transcribed into text using **AssemblyAI**.
3. **Security (Optional):** If a user flags a document as confidential, the extracted transcription is encrypted using a user-provided password before being saved to the database.
4. **Chunking:** The large transcribed text is split into smaller, manageable chunks using a **Fixed-size Chunking Strategy**.
5. **Embedding:** Each chunk is converted into a dense vector representation using the **Cohere** embedding model.
6. **Vector Storage:** The embeddings are saved in a **FAISS** vector index to enable extremely fast similarity searches later.
7. **Summarization & Notification:** The document is automatically summarized, and the user is sent an email notification confirming the upload and processing.
8. **Querying (RAG):** When a user asks a question about their document, the question is embedded, compared against the FAISS index to retrieve the most relevant chunks, and sent to an LLM to generate an accurate, grounded answer.

---

## 2. Technologies Used and Why

### Backend
* **FastAPI (Python):** Used as the core web framework. **Why:** It is incredibly fast, natively supports asynchronous programming (`async`/`await`), and automatically generates Swagger documentation.
* **MongoDB (Motor & Beanie):** Used as the primary NoSQL database. **Why:** Motor provides async drivers for MongoDB, preventing database calls from blocking the FastAPI event loop. Beanie provides an elegant Object-Document Mapper (ODM) layer for Pydantic-based data models.
* **AssemblyAI:** Used for speech-to-text transcription. **Why:** It offers highly accurate, state-of-the-art asynchronous audio transcription APIs.
* **yt-dlp & moviepy:** Used for handling video and YouTube links. **Why:** They are the most reliable open-source tools for scraping and processing video/audio streams.
* **bcrypt & cryptography:** Used for password hashing and document encryption. **Why:** Ensures that confidential data remains secure at rest and user passwords are safely hashed.

### Frontend
* **React 19 (via Vite):** The user interface is built as a Single Page Application (SPA). **Why:** React provides a component-based architecture for rich interactivity, and Vite offers lightning-fast Hot Module Replacement (HMR) and build times.
* **TypeScript:** **Why:** Adds static typing to JavaScript, catching errors at compile time and improving developer experience and code maintainability.
* **Tailwind CSS v4:** Used for styling. **Why:** Utility-first CSS framework that allows for rapid UI development without writing custom CSS files.
* **Recharts:** Used for data visualization. **Why:** A highly customizable and declarative charting library built for React.

---

## 3. Core Strategies Used and Why

### A. Fixed-size Character Chunking with Overlap
* **What it is:** The system splits raw transcriptions into chunks of **500 characters** with an **overlap of 50 characters**.
* **Why:** 
  1. **LLM Context Limits:** Large language models have a maximum token limit. Chunking ensures we only pass the most relevant snippets to the LLM, saving costs and preventing context window overflow.
  2. **Retrieval Precision:** Embedding a 1-hour transcript as a single vector dilutes the specific facts. Smaller chunks mean the embedding vector highly accurately represents the specific information in that paragraph.
  3. **Overlap:** The 50-character overlap prevents a critical sentence or thought from being abruptly cut in half across two chunks, preserving semantic context.

### B. Cohere Embeddings (`embed-english-v3.0`)
* **What it is:** The model used to convert text chunks into high-dimensional mathematical vectors.
* **Why:** Cohere's v3 models are state-of-the-art for semantic search. They specifically differentiate between `search_document` (for the chunks) and `search_query` (for the user's question), optimizing the vector space for retrieval tasks better than older symmetric models.

### C. FAISS Vector Store (`IndexFlatL2`)
* **What it is:** Facebook AI Similarity Search (FAISS) is used to store the Cohere embeddings.
* **Why:** 
  1. **Speed:** FAISS is a highly optimized C++ library that performs blazing-fast nearest-neighbor searches.
  2. **L2 Distance:** `IndexFlatL2` uses Euclidean distance to accurately find the closest matching vectors to a user query.
  3. **Simplicity:** It provides a lightweight, in-memory vector index without the overhead of spinning up a separate, heavy database service like Pinecone or Qdrant for this specific use case.
