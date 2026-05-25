import type {
  ChatRequest,
  ChatResponse,
  IngestRequest,
  IngestResponse
} from "./types"

const DEFAULT_BASE_URL = "https://ragboyt-production.up.railway.app/api"

const API_BASE_URL =
  process.env.PLASMO_PUBLIC_API_BASE_URL || DEFAULT_BASE_URL

async function requestJson<T>(
  path: string,
  payload: object
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed: ${response.status}`)
  }

  return (await response.json()) as T
}

export async function ingestTranscript(
  payload: IngestRequest
): Promise<IngestResponse> {
  return requestJson<IngestResponse>("/ingest", payload)
}

export async function submitChat(
  payload: ChatRequest
): Promise<ChatResponse> {
  return requestJson<ChatResponse>("/chat", payload)
}
