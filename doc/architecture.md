# Architecture & Data Flow

## System Architecture

InsightFlow follows a modern decoupled architecture:
1. **Client Layer**: A React-based SPA interacting with the backend via RESTful API calls using Axios.
2. **API Layer**: FastAPI serves as the entry point, handling routing, authentication (JWT), and request validation.
3. **Data Processing Layer**: Responsible for extracting text, fetching videos, and interacting with third-party APIs (AssemblyAI, Cohere, AI21).
4. **Data Persistence Layer**: 
    - **MongoDB**: Stores user information, document metadata, chat histories, and encrypted transcripts.
    - **FAISS**: Stores mathematical vector embeddings for fast semantic similarity search.

## Detailed Data Flow

1. **Upload & Ingestion**
   - User uploads a file (PDF, text, audio, video) or provides a URL (YouTube).
   - FastAPI receives the payload and authenticates the request.

2. **Processing & Extraction**
   - **Documents**: Direct text extraction.
   - **Audio/Video**: Extracted via `moviepy` or downloaded via `yt-dlp`. Sent asynchronously to **AssemblyAI** for transcription.

3. **Security Check**
   - If marked confidential, the transcript is encrypted (AES-256 via `cryptography` and `bcrypt`) before saving to MongoDB.

4. **Chunking**
   - Transcribed text is split into 500-character chunks with a 50-character overlap.

5. **Embedding Generation**
   - Chunks are sent to **Cohere** (`embed-english-v3.0`) to generate vector representations.

6. **Vector Storage**
   - Embeddings are indexed in **FAISS** for fast similarity-based retrieval.

7. **Summarization & Notification**
   - An LLM generates a summary.
   - An email is sent to notify the user of successful processing.

8. **Querying (RAG)**
   - User submits a question.
   - Question is embedded using Cohere.
   - FAISS retrieves the most relevant chunks.
   - Relevant chunks are passed to the LLM to generate a grounded, context-aware answer.
