# Frontend Guide (Extension)

This document explains the browser extension frontend, how the side panel UI works, and how it talks to the backend.

## 1) Overview
The frontend is a Chrome MV3 extension built with Plasmo, React, and Tailwind. It does three things:
1. Reads the active YouTube tab context (URL, video ID, title).
2. Calls the backend to ingest the transcript and ask questions.
3. Shows answers, evidence, and timestamp jump controls in a side panel.

Key folders:
- extension/src/sidepanel: main UI and components.
- extension/src/contents: content script running on YouTube pages.
- extension/src/lib: API helpers, types, and message contracts.
- extension/src/styles: Tailwind + UI utilities.

## 2) Extension packaging and manifest
Files:
- extension/package.json
- extension/plasmo.config.ts

Highlights:
- Plasmo handles MV3 build and packaging.
- Manifest permissions:
  - activeTab, tabs, sidePanel
- Host permissions:
  - https://www.youtube.com/*
  - https://youtu.be/*
- Side panel entry is sidepanel.html (Plasmo generates it).

Scripts:
- npm run dev: watch/dev build
- npm run build: production build
- npm run package: zip build

## 3) Content script (YouTube page)
File: extension/src/contents/youtube.ts

What it does:
- Runs on YouTube pages (document_idle).
- Listens for extension messages and responds with page context.

Message handlers:
- GET_VIDEO_CONTEXT
  - Returns the current URL, video ID, and title.
- SEEK_TO
  - Seeks the YouTube video element to a given timestamp and plays.

The video ID and title are extracted using helpers in extension/src/lib/youtube.ts.

## 4) API layer and types
Files:
- extension/src/lib/api.ts
- extension/src/lib/types.ts
- extension/src/lib/messages.ts

### API helper (api.ts)
- Base URL is set by PLASMO_PUBLIC_API_BASE_URL.
- Default fallback is the Railway backend.
- Two POST requests:
  - /ingest
  - /chat

### Types (types.ts)
- Defines IngestRequest, IngestResponse, ChatRequest, ChatResponse.
- SearchResult matches backend chunk shape (content, start_time, end_time, score).
- VideoContext stores the active tab data.

### Messages (messages.ts)
- Defines message contracts between side panel and content script:
  - GET_VIDEO_CONTEXT / VIDEO_CONTEXT
  - SEEK_TO

## 5) Side panel entry
File: extension/src/sidepanel/index.tsx

This is the main React app for the side panel.

State managed here:
- video context (url, id, title)
- contextReady (ingest completed)
- loading flags for ingest and chat
- error message and backend offline status
- current results and recent history
- suggested questions

Key actions:
- refreshVideoContext(): asks content script for video info.
- handleIngest(): calls /ingest and sets contextReady.
- handleQuery(): calls /chat and updates results/history.
- handleSeek(): sends SEEK_TO to the content script.

UI flow:
1. Header and video preview.
2. Ingest button.
3. Query form.
4. Suggested questions.
5. Answer + evidence list.
6. History panel.

## 6) Side panel components
Folder: extension/src/sidepanel/components

### Header.tsx
Shows the branded image at the top of the panel.

### VideoPreview.tsx
Shows thumbnail, title, and video ID state.

### EmptyState.tsx
Displays helpful guidance when no video or no ingest yet.

### QueryForm.tsx
Text area and submit button for asking questions.

### SuggestedQuestions.tsx
Renders suggested prompts as clickable chips.

### StatusNotice.tsx
Displays warning or error banners (offline backend, errors).

### ResultsList.tsx
Main results renderer. It:
- Shows a loading skeleton while waiting.
- Parses the LLM answer into body, confidence, follow-up.
- Highlights timestamps in answers and makes them clickable.
- Dedupe chunks and build jump buttons.
- Renders evidence with expand/collapse.

### AnswerCard.tsx
Styled panel for the LLM answer, copy button, and follow-up action.

### EvidenceCard.tsx
Shows one chunk with time range and toggle for expanded view.

### LoadingSkeleton.tsx
Animated placeholder for answer + evidence loading state.

### HistoryPanel.tsx
Shows recent questions to re-open earlier answers.

## 7) Styling system
Files:
- extension/src/styles/tailwind.css
- extension/tailwind.config.js
- extension/postcss.config.js

Tailwind is used for layout and styles.
Custom tokens:
- Colors: haze, panel, teal, amber, youtube, etc.
- Shadows: soft, circuit, glow
- Font sizes: micro, compact, body

Component utilities:
- .ui-button / .ui-chip / .glass-card
- animated shimmer and soft-in transitions

## 8) Data flow summary
1. Side panel asks content script for the current YouTube context.
2. User clicks Ingest -> /api/ingest runs on backend.
3. Suggested questions are returned and displayed.
4. User asks a question -> /api/chat runs on backend.
5. Answer + evidence are rendered with timestamp jump controls.

## 9) Environment variables
- PLASMO_PUBLIC_API_BASE_URL
  - Example: http://localhost:8000/api
  - Used to point the extension to your backend.

## 10) Build and share
- npm run build creates the folder:
  extension/build/chrome-mv3-prod
- Load unpacked from Chrome extensions page.

## 11) What to improve later (optional)
- Cache last ingested video ID in storage.
- Add settings UI for API base URL.
- Add per-video history persistence.
- Show backend health status on load.
