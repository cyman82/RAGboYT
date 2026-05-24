import { motion } from "framer-motion"
import { Copy, CornerDownRight, Sparkles } from "lucide-react"
import type { ReactNode } from "react"

type AnswerCardProps = {
  answer: ReactNode
  confidence: string
  followUp: string
  onCopy: () => void
  onFollowUp: (question: string) => void
}

const AnswerCard = ({
  answer,
  confidence,
  followUp,
  onCopy,
  onFollowUp
}: AnswerCardProps) => {
  return (
    <motion.article
      className="rounded-2xl border border-teal/25 bg-gradient-to-br from-panelElevated to-panel p-4 shadow-glow"
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.26, ease: "easeOut" }}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2.5">
          <span className="rounded-2xl border border-teal/25 bg-tealSoft p-2 text-teal">
            <Sparkles className="h-4 w-4" aria-hidden="true" />
          </span>
          <div>
          <p className="eyebrow">Answer</p>
          <h2 className="mt-1 text-base font-semibold text-slate-50">
            Grounded read
          </h2>
          </div>
        </div>
        <button
          className="ui-button ui-button-quiet shrink-0 px-3 py-2 text-xs"
          type="button"
          onClick={onCopy}
        >
          <Copy className="h-3.5 w-3.5" aria-hidden="true" />
          Copy
        </button>
      </div>

      <div className="mt-4 max-w-none text-body text-slate-200">{answer}</div>

      <div className="mt-4 flex flex-wrap items-center gap-2">
        {confidence && (
          <span className="rounded-full border border-teal/20 bg-tealSoft px-3 py-1 text-[11px] font-medium text-teal">
            Confidence: {confidence}
          </span>
        )}
        {followUp && (
          <button
            className="inline-flex items-center gap-1.5 rounded-full border border-amber/20 bg-amberSoft px-3 py-1 text-left text-[11px] font-medium text-amber transition hover:border-amber/50 hover:bg-amber/20 focus:outline-none focus:ring-2 focus:ring-amber/70 focus:ring-offset-2 focus:ring-offset-haze"
            type="button"
            onClick={() => onFollowUp(followUp)}
          >
            <CornerDownRight className="h-3.5 w-3.5" aria-hidden="true" />
            Follow-up: {followUp}
          </button>
        )}
      </div>
    </motion.article>
  )
}

export default AnswerCard
