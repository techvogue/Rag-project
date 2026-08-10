# InsightFlow - AI-based Q&A RAG System

InsightFlow is an intelligent web application that transcribes, summarizes, and enables real-time conversational Q&A over audio, video, documents, and web links using advanced AI models. It leverages Retrieval-Augmented Generation (RAG), vector search, and LangChain to provide accurate, context-aware answers with full conversational memory.

## 🚀 Key Features
- **Conversational Memory**: The AI remembers previous context within a session, making follow-up questions feel natural.
- **Real-Time Streaming UX**: Answers are streamed token-by-token using Server-Sent Events (SSE), just like ChatGPT.
- **Modern Chat Interface**: A beautiful, responsive frontend with markdown support and message bubbles.
- **Semantic Chunking**: Intelligently splits documents using LangChain to preserve contextual meaning.
- **Transcribe & Summarize**: Extract text from audio and video files via AssemblyAI and summarize large meetings instantly.
- **Security & Privacy**: Document confidentiality via AES-256 encryption.

## 🛠 Tech Stack
- **Frontend**: React 19, Vite, TypeScript, Tailwind CSS v4, React-Markdown
- **Backend**: FastAPI (Python), LangChain
- **Database**: MongoDB (Motor & Beanie ODM)
- **Vector Search**: FAISS (with LangChain integration)
- **AI/LLM APIs**: AssemblyAI, Cohere (`embed-english-v3.0`), AI21
- **Deployment**: Render (backend), Vercel (frontend)

## ⚙️ Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB instance
- AssemblyAI and Cohere API keys

### Backend (FastAPI)
1. Clone the repository:
   ```bash
   git clone https://github.com/techvogue/Rag-project.git
   cd Rag-project/backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your `.env` file with the required API keys (Cohere, AssemblyAI, etc.) and MongoDB URI.
5. Run the backend server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend (React.js)
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set up your `.env` variables (e.g., `VITE_API_BASE_URL`).
4. Run the frontend:
   ```bash
   npm run dev
   ```

## 📖 Documentation
Detailed architectural explanations and phase plans are located in the `doc/` directory:
- [Architecture & Data Flow](doc/architecture.md)
- [Architecture Decisions](doc/decisions.md)
- [Tech Stack Overview](doc/techstack.md)
- [Future Improvements & Phase Plan](doc/improvements.md)

## 🔐 Security
- All sensitive data is encrypted using AES-256.
- JWT-based authentication for secure access.

## 🤝 Contribution
Contributions are welcome! Please open issues or submit pull requests for improvements or bug fixes.

## 📄 License
This project is licensed under the MIT License.

## 📬 Contact
For questions or support, contact [vishwagautam57@gmail.com](mailto:vishwagautam57@gmail.com).

---
**GitHub:** https://github.com/techvogue/Rag-project