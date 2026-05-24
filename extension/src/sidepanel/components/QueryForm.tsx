import { motion } from "framer-motion"
import { Loader2, Send, Sparkles } from "lucide-react"
import { useState } from "react"

type QueryFormProps = {
  disabled?: boolean
  isLoading?: boolean
  onSubmit: (question: string) => void
}

const QueryForm = ({
  disabled,
  isLoading,
  onSubmit
}: QueryFormProps) => {
  const [question, setQuestion] = useState("")

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault()
    if (!question.trim()) {
      return
    }

    onSubmit(question.trim())
  }

  return (
    <motion.form
      className="glass-card overflow-hidden p-3"
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
    >
      <label
        className="mb-2 flex items-center gap-2 text-compact font-medium text-slate-200"
        htmlFor="video-question"
      >
        <Sparkles className="h-4 w-4 text-teal" aria-hidden="true" />
        Ask the transcript
      </label>
      <textarea
        id="video-question"
        className="min-h-[104px] w-full resize-none rounded-2xl border border-line bg-black/20 px-3.5 py-3 text-body text-slate-100 shadow-inner transition placeholder:text-slate-500 focus:border-teal/50 focus:bg-black/30 focus:outline-none focus:ring-2 focus:ring-teal/20 disabled:cursor-not-allowed disabled:opacity-60"
        placeholder="Ask for a summary, a timestamp, or the key argument..."
        value={question}
        onChange={(event) => setQuestion(event.target.value)}
        disabled={disabled}
      />
      <button
        className="ui-button ui-button-accent mt-3 w-full"
        type="submit"
        disabled={disabled}
      >
        {isLoading ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
            Reading transcript
          </>
        ) : (
          <>
            <Send className="h-4 w-4" aria-hidden="true" />
            Ask
          </>
        )}
      </button>
    </motion.form>
  )
}

export default QueryForm
