import { AnimatePresence, motion } from "framer-motion"
import { Library, TimerReset } from "lucide-react"
import { useState } from "react"

import type { ChatResponse } from "../../lib/types"
import AnswerCard from "./AnswerCard"
import EvidenceCard from "./EvidenceCard"
import LoadingSkeleton from "./LoadingSkeleton"

type ResultsListProps = {
  results: ChatResponse | null
  isLoading: boolean
  onSeek: (seconds: number) => void
  onFollowUp: (question: string) => void
}

const ResultsList = ({
  results,
  isLoading,
  onSeek,
  onFollowUp
}: ResultsListProps) => {
  const [expandedEvidence, setExpandedEvidence] = useState<
    Record<string, boolean>
  >({})

  if (isLoading) {
    return (
      <AnimatePresence mode="wait">
        <LoadingSkeleton />
      </AnimatePresence>
    )
  }

  if (!results) {
    return null
  }

  const uniqueChunks = dedupeChunks(results.chunks)
  const scores = uniqueChunks.map((chunk) => chunk.score)
  const minScore = scores.length > 0 ? Math.min(...scores) : 0
  const maxScore = scores.length > 0 ? Math.max(...scores) : 0
  const highConfidenceChunks = uniqueChunks.filter(
    (chunk) =>
      confidenceLabel(chunk.score, minScore, maxScore) ===
      "confidence: high"
  )
  const displayChunks =
    highConfidenceChunks.length > 0
      ? highConfidenceChunks
      : uniqueChunks.slice(0, 1)
  const answerSections = parseAnswerSections(results.answer)

  return (
    <motion.div
      className="space-y-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.18 }}
    >
      <AnswerCard
        answer={highlightTimestamps(answerSections.body, onSeek)}
        confidence={answerSections.confidence}
        followUp={answerSections.followUp}
        onCopy={() => copyToClipboard(results.answer)}
        onFollowUp={onFollowUp}
      />

      <motion.section
        className="rounded-2xl border border-line bg-panel bg-opacity-80 p-4 shadow-soft backdrop-blur-xl"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.24, delay: 0.06 }}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-2.5">
            <span className="rounded-2xl border border-teal/20 bg-tealSoft p-2 text-teal">
              <Library className="h-4 w-4" aria-hidden="true" />
            </span>
            <div>
            <p className="eyebrow">Evidence</p>
            <h2 className="mt-1 text-base font-semibold text-slate-50">
              Transcript receipts
            </h2>
            </div>
          </div>
          <span className="rounded-full border border-teal/20 bg-tealSoft px-2.5 py-1 text-[11px] font-medium text-teal">
            {displayChunks.length} sources
          </span>
        </div>

        <div className="mt-4 space-y-3">
          {displayChunks.map((chunk, index) => {
            const key = `${chunk.start_time}-${chunk.end_time}-${index}`
            const timeLabel = `${formatTimestamp(
              chunk.start_time
            )} - ${formatTimestamp(chunk.end_time)}`

            return (
              <EvidenceCard
                key={key}
                chunk={chunk}
                confidence={confidenceLabel(chunk.score, minScore, maxScore)}
                isExpanded={Boolean(expandedEvidence[key])}
                onSeek={onSeek}
                onToggle={() =>
                  setExpandedEvidence((prev) => ({
                    ...prev,
                    [key]: !prev[key]
                  }))
                }
                timeLabel={timeLabel}
              />
            )
          })}
        </div>
      </motion.section>

      {displayChunks.length > 0 && (
        <section className="space-y-2">
          <p className="flex items-center gap-2 text-compact font-semibold text-slate-200">
            <TimerReset className="h-4 w-4 text-youtube" aria-hidden="true" />
            Jump points
          </p>
          <div className="flex flex-wrap gap-2">
            {dedupeTimestampChips(displayChunks).map((chip, index) => (
              <motion.button
                key={`${chip.label}-${index}`}
                className="rounded-full border border-youtube/25 bg-youtube/10 px-3 py-1.5 text-[11px] font-semibold text-red-100 transition hover:border-youtube/60 hover:bg-youtube/20 focus:outline-none focus:ring-2 focus:ring-youtube/60 focus:ring-offset-2 focus:ring-offset-haze"
                type="button"
                onClick={() => onSeek(chip.seconds)}
                whileHover={{ y: -2 }}
                whileTap={{ scale: 0.98 }}
              >
                {chip.label}
              </motion.button>
            ))}
          </div>
        </section>
      )}
    </motion.div>
  )
}

function highlightTimestamps(
  text: string,
  onSeek: (seconds: number) => void
) {
  const pattern = /(\b\d{1,2}:\d{2}(?::\d{2})?(?:\.\d{1,3})?\b)/g
  const parts = text.split(pattern)
  const seen = new Set<string>()

  return parts.map((part, index) => {
    const timestampPattern =
      /^(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\.(\d{1,3}))?$/

    if (timestampPattern.test(part)) {
      const seconds = parseTimestamp(part)
      const label = seconds === null ? part : formatTimestamp(seconds)
      const key = label

      if (seconds === null) {
        return (
          <span
            key={`${part}-${index}`}
            className="rounded-md border border-youtube/20 bg-youtube/10 px-1.5 py-0.5 text-red-100"
          >
            {label}
          </span>
        )
      }

      if (seen.has(key)) {
        return <span key={`${part}-${index}`}>{label}</span>
      }

      seen.add(key)

      return (
        <button
          key={`${part}-${index}`}
          className="rounded-md border border-youtube/20 bg-youtube/10 px-1.5 py-0.5 font-semibold text-red-100 transition hover:border-youtube/60 hover:bg-youtube/20 focus:outline-none focus:ring-2 focus:ring-youtube/60 focus:ring-offset-2 focus:ring-offset-haze"
          type="button"
          onClick={() => onSeek(seconds)}
        >
          {label}
        </button>
      )
    }

    return <span key={`${part}-${index}`}>{part}</span>
  })
}

function parseTimestamp(value: string): number | null {
  const match = value.match(
    /^(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\.(\d{1,3}))?$/
  )
  if (!match) {
    return null
  }

  const first = Number(match[1])
  const second = Number(match[2])
  const third = match[3] ? Number(match[3]) : null
  const millis = match[4] ? Number(match[4].padEnd(3, "0")) : 0

  if (third !== null) {
    return first * 3600 + second * 60 + third + millis / 1000
  }

  return first * 60 + second + millis / 1000
}

function confidenceLabel(
  score: number,
  minScore: number,
  maxScore: number
) {
  if (maxScore === minScore) {
    return "confidence: medium"
  }

  const normalized = (score - minScore) / (maxScore - minScore)

  if (normalized <= 0.33) {
    return "confidence: high"
  }

  if (normalized <= 0.66) {
    return "confidence: medium"
  }

  return "confidence: low"
}

function dedupeChunks(chunks: ChatResponse["chunks"]) {
  const seen = new Set<string>()
  const unique: ChatResponse["chunks"] = []

  for (const chunk of chunks) {
    const key = `${chunk.start_time}-${chunk.end_time}`
    if (seen.has(key)) {
      continue
    }

    seen.add(key)
    unique.push(chunk)
  }

  return unique
}

async function copyToClipboard(text: string) {
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    // Clipboard can be unavailable in some extension surfaces.
  }
}

function formatTimestamp(seconds: number) {
  if (seconds < 0) {
    return "00:00"
  }

  const totalSeconds = Math.floor(seconds)
  const hours = Math.floor(totalSeconds / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const secs = totalSeconds % 60

  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(secs)}`
  }

  return `${pad(minutes)}:${pad(secs)}`
}

function pad(value: number) {
  return value.toString().padStart(2, "0")
}

function dedupeTimestampChips(chunks: ChatResponse["chunks"]) {
  const seen = new Set<string>()
  const chips: Array<{ label: string; seconds: number }> = []

  for (const chunk of chunks) {
    const label = formatTimestamp(chunk.start_time)
    if (seen.has(label)) {
      continue
    }

    seen.add(label)
    chips.push({ label, seconds: chunk.start_time })
  }

  return chips
}

function parseAnswerSections(answer: string) {
  const confidenceMatch = answer.match(/Confidence:\s*([^\n]+)/i)
  const followUpMatch = answer.match(/Follow-up:\s*([^\n]+)/i)

  let body = answer
  if (confidenceMatch) {
    body = body.replace(confidenceMatch[0], "").trim()
  }
  if (followUpMatch) {
    body = body.replace(followUpMatch[0], "").trim()
  }

  return {
    body,
    confidence: confidenceMatch ? confidenceMatch[1].trim() : "",
    followUp: followUpMatch ? followUpMatch[1].trim() : ""
  }
}

export default ResultsList
