import "../styles/tailwind.css"

import { AnimatePresence, motion } from "framer-motion"
import { Captions, Loader2 } from "lucide-react"
import { useEffect, useMemo, useState } from "react"

import type { ChatResponse, VideoContext } from "../lib/types"
import { ingestTranscript, submitChat } from "../lib/api"
import type {
  ContentRequestMessage,
  ContentResponseMessage,
  ExtensionMessage,
  SeekMessage
} from "../lib/messages"
import QueryForm from "./components/QueryForm"
import ResultsList from "./components/ResultsList"
import Header from "./components/Header"
import HistoryPanel from "./components/HistoryPanel"
import SuggestedQuestions from "./components/SuggestedQuestions"
import EmptyState from "./components/EmptyState"
import StatusNotice from "./components/StatusNotice"
import VideoPreview from "./components/VideoPreview"

const DEFAULT_CHUNK_SIZE = 1000
const DEFAULT_CHUNK_OVERLAP = 200
const DEFAULT_SUGGESTED_QUESTIONS = [
  "Summarize this video",
  "Key insights",
  "Explain the main idea",
  "What did he say about burnout?"
]

const SidePanel = () => {
  const [video, setVideo] = useState<VideoContext>({
    url: "",
    videoId: null,
    title: null
  })
  const [contextReady, setContextReady] = useState(false)
  const [isIngesting, setIsIngesting] = useState(false)
  const [isQuerying, setIsQuerying] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<ChatResponse | null>(null)
  const [history, setHistory] = useState<
    Array<{ question: string; response: ChatResponse }>
  >([])
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([])
  const [isBackendOffline, setIsBackendOffline] = useState(false)

  useEffect(() => {
    refreshVideoContext().catch((err) => setError(err.message))
  }, [])

  const canChat = useMemo(() => {
    return Boolean(video.url)
  }, [video.url])

  const promptSuggestions = useMemo(() => {
    const merged = [...suggestedQuestions, ...DEFAULT_SUGGESTED_QUESTIONS]
    return Array.from(new Set(merged)).slice(0, 6)
  }, [suggestedQuestions])

  async function refreshVideoContext() {
    setError(null)
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true
    })

    if (!tab?.id) {
      setError("No active YouTube tab detected.")
      return
    }

    const message: ContentRequestMessage = {
      type: "GET_VIDEO_CONTEXT"
    }

    const response = (await chrome.tabs.sendMessage(
      tab.id,
      message
    )) as ContentResponseMessage

    setVideo(response.payload)
  }

  async function handleIngest() {
    if (!video.url) {
      setError("Open a YouTube video to ingest transcript.")
      return
    }

    setIsIngesting(true)
    setError(null)
    setIsBackendOffline(false)

    try {
      const response = await ingestTranscript({
        youtube_url: video.url,
        chunk_size: DEFAULT_CHUNK_SIZE,
        chunk_overlap: DEFAULT_CHUNK_OVERLAP
      })
      setContextReady(true)
      setSuggestedQuestions(response.suggested_questions || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ingest failed")
      setIsBackendOffline(true)
    } finally {
      setIsIngesting(false)
    }
  }

  async function handleQuery(question: string) {
    if (!contextReady) {
      setError("Ingest the transcript before asking questions.")
      return
    }

    setIsQuerying(true)
    setError(null)
    setIsBackendOffline(false)

    try {
      const response = await submitChat({
        question,
        top_k: 5,
        max_chunks: 6
      })
      setResults(response)
      setHistory((prev) =>
        [{ question, response }, ...prev].slice(0, 5)
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : "Chat failed")
      setIsBackendOffline(true)
    } finally {
      setIsQuerying(false)
    }
  }

  async function handleSeek(seconds: number) {
    const [tab] = await chrome.tabs.query({
      active: true,
      currentWindow: true
    })

    if (!tab?.id) {
      setError("No active YouTube tab detected.")
      return
    }

    const message: SeekMessage = {
      type: "SEEK_TO",
      payload: { seconds }
    }

    await chrome.tabs.sendMessage(tab.id, message as ExtensionMessage)
  }

  const isBusy = isIngesting || isQuerying

  return (
    <div className="min-h-screen w-full overflow-x-hidden bg-haze text-ink">
      <Header video={video} />

      <main className="space-y-4 px-4 py-4">
        <VideoPreview video={video} />

        {isBackendOffline && (
          <StatusNotice tone="warning">
            Backend appears offline. Start FastAPI to use ingest and chat.
          </StatusNotice>
        )}
        {!video.url && (
          <EmptyState hasVideo={false} />
        )}

        <motion.button
          className="ui-button ui-button-dark w-full"
          onClick={handleIngest}
          disabled={isBusy || !canChat}
          type="button"
          whileHover={!isBusy && canChat ? { y: -2 } : undefined}
          whileTap={!isBusy && canChat ? { scale: 0.99 } : undefined}
        >
          {isIngesting ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              Ingesting transcript
            </>
          ) : (
            <>
              <Captions className="h-4 w-4" aria-hidden="true" />
              Ingest transcript
            </>
          )}
        </motion.button>

        <QueryForm
          disabled={!contextReady || isBusy}
          isLoading={isQuerying}
          onSubmit={handleQuery}
        />

        {!contextReady && video.url && (
          <EmptyState hasVideo />
        )}

        <SuggestedQuestions
          questions={contextReady ? promptSuggestions : []}
          disabled={isBusy}
          onSelect={handleQuery}
        />

        {error && (
          <StatusNotice tone="error">{error}</StatusNotice>
        )}
      </main>

      <AnimatePresence>
        {(results || isQuerying) && (
          <motion.section
            className="border-t border-line px-4 py-4"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.22 }}
          >
            <ResultsList
              results={results}
              isLoading={isQuerying}
              onSeek={handleSeek}
              onFollowUp={handleQuery}
            />
          </motion.section>
        )}
      </AnimatePresence>

      {history.length > 0 && (
        <section className="border-t border-line px-4 py-4">
          <HistoryPanel
            items={history}
            onSelect={(item) => setResults(item.response)}
          />
        </section>
      )}
    </div>
  )
}

export default SidePanel
