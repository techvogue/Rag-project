# Tech Stack

## Overview
InsightFlow leverages a modern, robust, and scalable technology stack to ensure seamless performance, security, and developer experience.

## Frontend
- **Framework**: React 19 (via Vite)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4
- **Visualization**: Recharts
- **State Management & Routing**: React Router
- **HTTP Client**: Axios
- **Deployment**: Vercel

## Backend
- **Framework**: FastAPI (Python)
- **Language**: Python 3.8+
- **Asynchronous Processing**: Native `async`/`await` support
- **Deployment**: Render

## Database & Storage
- **Primary Database**: MongoDB
- **ODM**: Beanie (Object-Document Mapper for Motor)
- **Vector Search Database**: FAISS (Facebook AI Similarity Search) - `IndexFlatL2`

## AI & Machine Learning
- **Transcription**: AssemblyAI (for highly accurate, asynchronous audio transcription)
- **LLM / Summarization**: Cohere, AI21
- **Embeddings**: Cohere (`embed-english-v3.0`)
- **Video Processing**: yt-dlp, moviepy

## Security
- **Authentication**: JWT (JSON Web Tokens)
- **Encryption**: AES-256 for sensitive data (handled via bcrypt & cryptography)
