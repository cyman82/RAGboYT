# Backend Guide

This document explains how the backend is built and how the RAG, LLM, and API layers work together.

## 1) Overview
The backend is a FastAPI app that does two jobs:
1. Ingest a YouTube video transcript, chunk it, embed it, and store it in FAISS.
2. Answer questions by retrieving relevant chunks and asking an LLM to respond using only those chunks.

Main folders:
- backend/app/api: HTTP routes and FastAPI setup.
- backend/app/rag: RAG pipeline pieces (ingestion, retrieval, prompting, embeddings).
- backend/app/llm: LLM calls for answers and suggested questions.
- backend/main.py: Uvicorn entrypoint that exposes the app.

## 2) App entrypoint and lifecycle
Files:
- backend/main.py
- backend/app/api/main.py

### backend/main.py
This is the minimal entrypoint for Uvicorn. It simply exports the FastAPI `app` from `app.api.main`. Uvicorn uses this when deployed.

### backend/app/api/main.py
This builds the FastAPI application and configures middleware and routes.

Key details:
- CORS is enabled for local dev origins plus optional extra origins via `CORS_ALLOW_ORIGINS`.
- `allow_origin_regex` allows Chrome extension requests: `chrome-extension://.*`.
- Two routers are added: `/api/ingest` and `/api/chat`.
- A shared in-memory vector store and an asyncio lock are created and stored in `app.state`:
  - `app.state.vector_store`: FAISSVectorStore or None
  - `app.state.store_lock`: prevents concurrent ingestion mutations

Why the lock matters:
- FAISS is in-memory and not thread-safe when being mutated. The lock ensures ingestion is serialized.

## 3) API layer
Folder: backend/app/api/routes

### Ingest route
File: backend/app/api/routes/ingest.py

Endpoint: `POST /api/ingest`

Request model (IngestRequest):
- `video_id` (optional)
- `video_url` (optional)
- `video_title` (optional, currently unused)
- `chunk_size` (default 1000)
- `chunk_overlap` (default 200)

Behavior:
1. Resolve YouTube URL:
   - If `video_url` is present, use it.
   - Else if `video_id` is present, build the full URL.
   - Else raise a 400 error.
2. Acquire the store lock and run the ingest pipeline in a threadpool.
3. Store the updated FAISS vector store in `app.state`.
4. Return `success`, `video_id`, `chunks_created`, and `suggested_questions`.

Errors:
- 400 for invalid input.
- 502 for runtime failures (e.g., transcript API failure or OpenAI issues).

### Chat route
File: backend/app/api/routes/chat.py

Endpoint: `POST /api/chat`

Request model (ChatRequest):
- `question` (required)
- `top_k` (default 5)
- `max_chunks` (optional)
- `time_window_seconds` (optional)
- `model` (optional, override)
- `prompt_template` (optional, override)

Behavior:
1. If the vector store is missing, return 400.
2. Normalize optional values (trim strings, drop empty or "string").
3. Run the query pipeline (threadpool).
4. Return answer, context, and chunk list.

## 4) RAG ingestion pipeline
Folder: backend/app/rag/pipelines

### Ingest pipeline
File: backend/app/rag/pipelines/ingest_pipeline.py

Flow:
1. Extract a video ID from the URL.
2. Fetch transcript via YouTubeTranscriptApi.
3. Chunk the transcript.
4. Generate embeddings for each chunk.
5. Add embeddings and metadata to FAISS.
6. Generate suggested questions from sample chunk content.

Key functions:
- `run_ingest_pipeline(youtube_url, store, chunk_size, chunk_overlap)`
- `_build_store_from_transcript(video_id, transcript, store, chunk_size, chunk_overlap)`

Return fields:
- `store`: FAISSVectorStore
- `video_id`: YouTube ID
- `segments`: number of transcript segments
- `chunks`: number of chunks stored
- `suggested_questions`: up to 3 questions

## 5) Transcript ingestion details
Folder: backend/app/rag/ingestion

### YouTube transcript loader
File: backend/app/rag/ingestion/youtube_loader.py

Key steps:
- `extract_video_id`: supports standard, shorts, embed, and youtu.be URLs, plus a fallback regex.
- `fetch_transcript`: uses YouTubeTranscriptApi and normalizes errors.
- `_normalize_transcript`: converts API output into a uniform list of {text, start, duration}.

### Chunker
File: backend/app/rag/ingestion/chunker.py

Chunking design:
- Character-based chunking for predictability.
- Chunk boundaries always align to segment boundaries.
- Overlap is applied by copying the last segments of the previous chunk.

Output format (TranscriptChunk):
- `content`: text block
- `start_time`, `end_time`: seconds

## 6) Embeddings and vector store
Folder: backend/app/rag/embeddings

### Embedder
File: backend/app/rag/embeddings/embedder.py

- Uses OpenAI embeddings model `text-embedding-3-small`.
- Batches inputs to avoid large requests.
- Requires `OPENAI_API_KEY`.

### Vector store
File: backend/app/rag/embeddings/vector_store.py

- FAISS IndexFlatL2 for cosine-like distance on embeddings.
- Stores metadata for each chunk (content, start_time, end_time).
- `search()` runs vector similarity search.
- `search_by_time()` retrieves chunks based on timestamp proximity.

## 7) Retrieval and ranking
Folder: backend/app/rag/retrieval

### Retriever
File: backend/app/rag/retrieval/retriever.py

Features:
- Timestamp queries like "2:13" are detected and reranked by time distance.
- Otherwise semantic search runs with oversampling and keyword reranking.

Scoring:
- Semantic similarity is combined with keyword overlap.
- Stopword filtering reduces noisy keyword scoring.

### Formatter
File: backend/app/rag/retrieval/formatter.py

- Formats retrieved chunks into readable context for the LLM.
- Adds chunk number, timestamps, and score.
- Controls the number of chunks sent to the LLM.

## 8) Prompting
Folder: backend/app/rag/prompting

File: backend/app/rag/prompting/prompt_builder.py

- Builds a grounded prompt with strict rules.
- Includes context, evidence snippets, and confidence hint.
- Allows a custom template for advanced users.

## 9) LLM layer
Folder: backend/app/llm

File: backend/app/llm/generator.py

Two main functions:
- `generate_answer(prompt, model=None)`
- `generate_suggested_questions(context, model=None)`

Details:
- Uses OpenAI chat completions via the OpenAI SDK.
- Default model is `gpt-4o-mini` unless overridden by `OPENAI_MODEL`.
- Suggested questions are returned as JSON array text, then parsed safely.

## 10) Test scripts
Folder: backend/scripts

- test_loader.py: prompts for a URL and prints the first 10 transcript segments.
- test_chunker.py: prompts for a URL and prints the first 3 chunks and timings.

## 11) Data flow summary
1. Client sends `/api/ingest` with video URL or ID.
2. Transcript is fetched and chunked.
3. Embeddings are generated and stored in FAISS.
4. Client sends `/api/chat` with a question.
5. RAG retrieves best chunks and builds a grounded prompt.
6. LLM answers using only transcript context.

## 12) Environment variables
Required:
- `OPENAI_API_KEY`

Optional:
- `OPENAI_MODEL` (default: gpt-4o-mini)
- `CORS_ALLOW_ORIGINS` (comma-separated)

## 13) What to improve later (optional)
- Persist vector store to disk or database.
- Add per-video stores instead of a single in-memory store.
- Add rate limiting and auth.
- Cache transcripts and embeddings.
- Add health check and metrics.
