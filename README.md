# 🔬 Research Paper Analyzer (AI-Powered)

A premium, modern web application that allows you to upload and chat with multiple Research Papers (PDF & DOCX). Powered by **Google Gemini 2.5/3.1** and **LangChain**, this tool uses RAG (Retrieval-Augmented Generation) to provide accurate, context-aware answers from your documents.

## ✨ Features
- **Modern UI/UX**: Premium dark theme with glassmorphism, Lottie animations, and a sleek chat interface.
- **Multi-Format Support**: Analyze both `.pdf` and `.docx` files simultaneously.
- **Interactive Chat**: Natural conversation flow with AI that remembers context.
- **Document Insights**: Real-time statistics and analysis status.
- **Robust Processing**: Smart batched embeddings with rate-limit protection.
- **FAISS Vector Store**: High-performance local vector database for fast similarity search.

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- A Google Gemini API Key (get one at [Google AI Studio](https://aistudio.google.com/))

### 2. Installation
```bash
# Clone the repository
git clone <repository-url>
cd Research-Paper-Analyzer

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
You can enter your keys in the app's **Configure AI provider keys** panel. Keys entered there are held in the current Streamlit session and are not written to project files. For a local environment-based setup, create a `.env.local` file in the root directory:
```text
GOOGLE_API_KEY=your_actual_key_here
GROQ_API_KEY=your_optional_fallback_key_here
```

Google Gemini is required because it creates document and query embeddings and provides the primary answers. Groq is optional and can provide the answer when Gemini's response generation reaches a quota limit; Gemini is still needed for search and embeddings. Papers and retrieved passages are sent to the provider handling that operation. The FAISS index is kept in a local per-session temporary folder and removed when you start a new session. When hosted remotely, serve the app over HTTPS and use a host you trust.

### 4. Run the App
```bash
streamlit run app.py
```

## 🛠️ Technology Stack
- **Frontend**: Streamlit (with Custom CSS)
- **LLM**: Google Gemini 2.5-Flash
- **Embeddings**: Google Gemini-Embedding-2
- **Orchestration**: LangChain
- **Vector Database**: FAISS
- **Document Parsing**: pypdf, python-docx

## 🛡️ Security
- API keys are managed via environment variables (`.env.local`).
- FAISS index is stored locally on your machine.

## 📄 License
This project is licensed under the MIT License.
