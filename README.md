# YouTube RAG Chatbot (Extension + Backend)

A Chrome side panel extension that ingests a YouTube transcript, runs Retrieval-Augmented Generation (RAG), and answers questions with timestamped evidence.

## What it does
- Ingests a YouTube transcript into a vector store (FAISS).
- Retrieves relevant chunks and asks an LLM to answer using only transcript context.
- Shows answers, evidence, and jump-to-timestamp controls in a side panel.

## Architecture
- Backend: FastAPI + YouTubeTranscriptApi + FAISS + OpenAI embeddings.
- Frontend: Plasmo MV3 extension + React + Tailwind side panel.

## Project structure
- backend/: FastAPI app, RAG pipeline, LLM calls.
- extension/: Chrome extension UI + content script.
- backend.md: backend deep dive.
- frontend.md: frontend deep dive.

## Requirements
- Python 3.10+ (backend)
- Node.js 18+ (extension)
- OpenAI API key

## Backend setup (local)
1. Install dependencies:

   ```bash
   pip install -r backend/requirements.txt
   ```

2. Set environment variables:

   ```bash
   OPENAI_API_KEY=your_key_here
   # Optional
   OPENAI_MODEL=gpt-4o-mini
   CORS_ALLOW_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

3. Start the API:

   ```bash
   python -m uvicorn app.api.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
   ```

## Extension setup (local)
1. Install dependencies:

   ```bash
   npm --prefix extension install
   ```

2. Set API base URL (optional):

   ```bash
   PLASMO_PUBLIC_API_BASE_URL=http://localhost:8000/api
   ```

3. Build the extension:

   ```bash
   npm --prefix extension run build
   ```

4. Load in Chrome:
- Open chrome://extensions
- Enable Developer mode
- Click Load unpacked
- Select extension/build/chrome-mv3-prod

## API endpoints
- POST /api/ingest
  - Inputs: video_url or video_id, chunk_size, chunk_overlap
- POST /api/chat
  - Inputs: question, top_k, max_chunks, time_window_seconds

## Usage flow
1. Open a YouTube video.
2. Open the extension side panel.
3. Click Ingest transcript.
4. Ask questions and jump to evidence timestamps.

## Notes
- The backend stores data in memory. Restarting the API clears the vector store.
- For production, deploy the backend and point the extension to that URL.

## Documentation
- backend.md: backend implementation details.
- frontend.md: frontend implementation details.
