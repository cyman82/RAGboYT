export type IngestRequest = {
  video_id?: string
  video_url?: string
  video_title?: string
  chunk_size?: number
  chunk_overlap?: number
}

export type IngestResponse = {
  success: boolean
  video_id: string
  chunks_created: number
  suggested_questions?: string[]
}

export type SearchResult = {
  content: string
  start_time: number
  end_time: number
  score: number
}

export type ChatRequest = {
  question: string
  top_k?: number
  max_chunks?: number | null
  time_window_seconds?: number | null
  model?: string | null
  prompt_template?: string | null
}

export type ChatResponse = {
  answer: string
  context: string
  chunks: SearchResult[]
}

export type VideoContext = {
  url: string
  videoId: string | null
  title: string | null
}
