import { motion } from "framer-motion"
import { ChevronDown, Clock3 } from "lucide-react"

import type { SearchResult } from "../../lib/types"

type EvidenceCardProps = {
  chunk: SearchResult
  confidence: string
  isExpanded: boolean
  onSeek: (seconds: number) => void
  onToggle: () => void
  timeLabel: string
}

const EvidenceCard = ({
  chunk,
  confidence,
  isExpanded,
  onSeek,
  onToggle,
  timeLabel
}: EvidenceCardProps) => {
  return (
    <motion.article
      className="rounded-2xl border border-line bg-white/[0.045] p-3 shadow-soft transition duration-200 hover:border-teal/35 hover:bg-white/[0.065]"
      layout
    >
      <div className="flex items-center justify-between gap-3">
        <button
          className="inline-flex items-center gap-1.5 rounded-full border border-youtube/25 bg-youtube/10 px-2.5 py-1 text-[11px] font-semibold text-red-200 transition hover:border-youtube/60 hover:bg-youtube/18 focus:outline-none focus:ring-2 focus:ring-youtube/60 focus:ring-offset-2 focus:ring-offset-haze"
          type="button"
          onClick={() => onSeek(chunk.start_time)}
        >
          <Clock3 className="h-3 w-3" aria-hidden="true" />
          {timeLabel}
        </button>
        <span className="text-micro font-semibold uppercase tracking-[0.12em] text-muted">
          {confidence}
        </span>
      </div>

      <button
        className="mt-3 w-full rounded-xl text-left transition focus:outline-none focus:ring-2 focus:ring-teal/60 focus:ring-offset-2 focus:ring-offset-haze"
        type="button"
        aria-expanded={isExpanded}
        onClick={onToggle}
      >
        <p
          className={`text-compact text-slate-300 transition-all duration-200 ${
            isExpanded ? "line-clamp-6" : "line-clamp-2"
          }`}
        >
          {chunk.content}
        </p>
        <span className="mt-2 inline-flex items-center gap-1 text-[11px] font-medium text-teal">
          {isExpanded ? "Collapse evidence" : "Read evidence"}
          <ChevronDown
            className={`h-3.5 w-3.5 transition ${
              isExpanded ? "rotate-180" : ""
            }`}
            aria-hidden="true"
          />
        </span>
      </button>
    </motion.article>
  )
}

export default EvidenceCard
