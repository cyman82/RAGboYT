import { motion } from "framer-motion"
import { Captions, Sparkles } from "lucide-react"

type EmptyStateProps = {
  hasVideo: boolean
}

const EmptyState = ({ hasVideo }: EmptyStateProps) => {
  return (
    <motion.section
      className="glass-card p-4"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
    >
      <div className="flex items-start gap-3">
        <div className="rounded-2xl border border-teal/20 bg-tealSoft p-2.5 text-teal">
          {hasVideo ? (
            <Captions className="h-5 w-5" aria-hidden="true" />
          ) : (
            <Sparkles className="h-5 w-5" aria-hidden="true" />
          )}
        </div>
        <div className="space-y-1">
          <h3 className="text-sm font-semibold text-slate-50">
            {hasVideo ? "Transcript intelligence is one step away" : "Waiting for a YouTube video"}
          </h3>
          <p className="text-compact text-muted">
            {hasVideo
              ? "Ingest the transcript to unlock grounded answers, suggested prompts, and timestamp jumps."
              : "Open a YouTube watch page, then return here to start a grounded chat."}
          </p>
        </div>
      </div>
    </motion.section>
  )
}

export default EmptyState
