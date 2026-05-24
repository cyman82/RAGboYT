# 🎬 YouTube RAG Chatbot (RAGboYT)

A powerful Chrome extension that lets you ask questions about any YouTube video using RAG (Retrieval-Augmented Generation) and LLMs. Get instant answers with video evidence, all without leaving YouTube.

## ✨ Features

- **🤖 AI-Powered Q&A**: Ask questions about YouTube video content and get intelligent answers
- **📹 Transcript Analysis**: Automatically processes YouTube transcripts using RAG
- **🔍 Evidence-Based Answers**: Each response includes specific timestamps and evidence from the video
- **💾 Persistent Storage**: Query history and metadata stored locally
- **🎯 Side Panel Integration**: Seamless Chrome extension side panel experience
- **⚡ Real-time Processing**: Get answers instantly with streaming responses
- **🔗 Grounded Responses**: All answers are grounded in actual video content

## 🛠 Tech Stack

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Plasmo** - Extension framework
- **Framer Motion** - Animations
- **Lucide React** - Icons

### Backend
- **Python 3.10+** - Core language
- **FastAPI** - API framework
- **LangChain** - LLM orchestration
- **FAISS** - Vector similarity search
- **youtube-transcript-api** - YouTube transcript extraction
- **Pydantic** - Data validation

### Key Libraries
- **ollama** or **OpenAI API** - LLM models
- **HuggingFace Embeddings** - Text embeddings
- **dotenv** - Environment configuration

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- Chrome/Chromium browser
- YouTube API access (or use transcript-api)
- LLM access (local Ollama or OpenAI API key)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/cyman82/RAGboYT.git
cd RAGboYT
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file with your configuration
cp .env.example .env
# Edit .env with your API keys and settings
```

#### `.env` Configuration Example

```env
# LLM Configuration
LLM_PROVIDER=ollama  # or 'openai'
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_API_KEY=sk-your-key-here

# Embedding Configuration
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
DEVICE=cpu  # or 'cuda' for GPU

# API Configuration
BACKEND_URL=http://localhost:8000
CORS_ORIGINS=["*"]

# Vector Store
VECTOR_STORE_PATH=./data/vectors
```

### 3. Frontend Setup

```bash
# Navigate to extension directory
cd extension

# Install dependencies
npm install

# Create .env file if needed
cp .env.example .env
# Update API_URL to match your backend
```

## 💻 Development

### Start Backend Development Server

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app/api/main.py
```

The backend will be available at `http://localhost:8000`

API docs: `http://localhost:8000/docs`

### Start Extension Development Build

```bash
cd extension
npm run dev
```

This starts the development build with hot reload.

### Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable **Developer Mode** (toggle in top-right)
3. Click **Load unpacked**
4. Select the `extension/build/chrome-mv3-dev` directory
5. The extension is now loaded for development

## 📦 Build & Deployment

### Build Extension for Production

```bash
cd extension
npm run build
npm run package
```

This creates `chrome-mv3-prod.zip` in the build directory.

### Deploy Backend

**Option 1: Hugging Face Spaces (Recommended for Quick Sharing)**
```bash
# Convert to Streamlit app and deploy to Hugging Face
# See DEPLOYMENT.md for detailed instructions
```

**Option 2: Railway or Render (Free Tier)**
- Connect GitHub repo
- Set environment variables
- Deploy automatically

**Option 3: Docker**
```bash
cd backend
docker build -t ragboyt-backend .
docker run -p 8000:8000 --env-file .env ragboyt-backend
```

## 📚 Project Structure

```
RAGboYT/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── main.py          # FastAPI app entry
│   │   │   └── routes/
│   │   │       ├── chat.py       # Chat endpoint
│   │   │       └── ingest.py     # Ingestion endpoint
│   │   ├── core/
│   │   │   └── config.py         # Configuration
│   │   ├── llm/
│   │   │   └── generator.py      # LLM response generation
│   │   └── rag/
│   │       ├── embeddings/       # Embedding models
│   │       ├── ingestion/        # Data processing
│   │       ├── pipelines/        # RAG pipelines
│   │       ├── prompting/        # Prompt templates
│   │       └── retrieval/        # Document retrieval
│   ├── scripts/                  # Testing & utilities
│   └── requirements.txt
│
├── extension/
│   ├── src/
│   │   ├── contents/             # Content scripts
│   │   ├── sidepanel/            # React side panel UI
│   │   ├── lib/                  # Utilities & API client
│   │   └── styles/               # Tailwind CSS
│   ├── build/                    # Compiled extension
│   ├── package.json
│   └── tsconfig.json
│
└── README.md
```

## 🔌 API Endpoints

### Chat Endpoint
```bash
POST /api/chat
Content-Type: application/json

{
  "video_id": "dQw4w9WgXcQ",
  "query": "What is the main topic?"
}
```

Response:
```json
{
  "answer": "The video discusses...",
  "evidence": [
    {
      "text": "Key quote from transcript",
      "timestamp": "2:34",
      "confidence": 0.95
    }
  ]
}
```

### Ingest Endpoint
```bash
POST /api/ingest
Content-Type: application/json

{
  "video_id": "dQw4w9WgXcQ",
  "transcript": "transcript text..."
}
```

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest scripts/test_*.py -v
```

## 🌐 Deployment Options

### For Sharing with Friends (Recommended)
1. **GitHub Releases** - [See instructions](docs/DEPLOYMENT.md#github-releases)
2. **Hugging Face Spaces** - [See instructions](docs/DEPLOYMENT.md#hugging-face-spaces)

### For Production
1. **Chrome Web Store** - Official deployment
2. **Vercel + Railway** - Scalable stack
3. **Docker + Cloud Platform** - Full control

## 🐛 Troubleshooting

### Extension not loading?
- Check console logs: `Right-click → Inspect → Console`
- Verify backend API is running
- Check CORS settings in `.env`

### No transcripts found?
- Verify YouTube video has captions enabled
- Check YouTube API quota
- Review backend logs

### Slow responses?
- Check LLM model size (use smaller model for faster responses)
- Verify GPU acceleration if using CUDA
- Monitor backend resource usage

## 📝 Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `ollama` | LLM service (ollama/openai) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `OPENAI_API_KEY` | - | OpenAI API key |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | HuggingFace embedding model |
| `DEVICE` | `cpu` | Compute device (cpu/cuda) |
| `BACKEND_URL` | `http://localhost:8000` | Backend API URL |
| `VECTOR_STORE_PATH` | `./data/vectors` | Vector store location |

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋 Support

- 📖 Check existing issues and discussions
- 🐛 Report bugs with detailed reproduction steps
- 💡 Suggest features in discussions

## 🚀 Roadmap

- [ ] Multi-language support
- [ ] Video chapters support
- [ ] Advanced filtering options
- [ ] Conversation memory
- [ ] Custom model selection UI
- [ ] Offline mode
- [ ] Video summarization
- [ ] Export transcripts

## 📞 Contact

For questions or suggestions, open an issue on GitHub.

---

**Built with ❤️ for YouTube lovers and curious minds**
