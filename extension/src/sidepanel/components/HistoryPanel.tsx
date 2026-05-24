import { motion } from "framer-motion"
import { History, RotateCcw } from "lucide-react"

import type { ChatResponse } from "../../lib/types"

type HistoryItem = {
  question: string
  response: ChatResponse
}

type HistoryPanelProps = {
  items: HistoryItem[]
  onSelect: (item: HistoryItem) => void
}

const HistoryPanel = ({ items, onSelect }: HistoryPanelProps) => {
  if (!items.length) {
    return (
      <div className="text-compact text-muted">
        Ask a few questions to build your recent history.
      </div>
    )
  }

  return (
    <section className="space-y-2">
      <h3 className="flex items-center gap-2 text-compact font-semibold text-slate-200">
        <History className="h-4 w-4 text-teal" aria-hidden="true" />
        Recent questions
      </h3>
      {items.map((item, index) => (
        <motion.button
          key={`${item.question}-${index}`}
          onClick={() => onSelect(item)}
          className="w-full rounded-2xl border border-line bg-white/[0.045] px-3 py-2.5 text-left text-compact text-muted transition hover:border-teal/35 hover:bg-white/[0.07] hover:text-slate-200 focus:outline-none focus:ring-2 focus:ring-teal/60 focus:ring-offset-2 focus:ring-offset-haze"
          whileHover={{ y: -1 }}
          whileTap={{ scale: 0.99 }}
        >
          <div className="flex items-center justify-between">
            <span className="line-clamp-1 font-medium text-slate-200">
              {item.question}
            </span>
            <span className="inline-flex items-center gap-1 text-[10px] text-muted">
              <RotateCcw className="h-3 w-3" aria-hidden="true" />
              {item.response.chunks.length} refs
            </span>
          </div>
        </motion.button>
      ))}
    </section>
  )
}

export default HistoryPanel
