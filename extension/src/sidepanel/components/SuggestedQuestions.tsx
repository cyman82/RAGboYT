import { motion } from "framer-motion"
import { MessageSquareText } from "lucide-react"

type SuggestedQuestionsProps = {
  disabled?: boolean
  questions: string[]
  onSelect: (question: string) => void
}

const SuggestedQuestions = ({
  disabled,
  questions,
  onSelect
}: SuggestedQuestionsProps) => {
  if (!questions.length) {
    return null
  }

  return (
    <motion.div
      className="space-y-2"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <h3 className="flex items-center gap-2 text-compact font-semibold text-slate-200">
        <MessageSquareText className="h-4 w-4 text-teal" aria-hidden="true" />
        Suggested prompts
      </h3>
      <div className="flex flex-wrap gap-2">
        {questions.map((question, index) => (
          <motion.button
            key={`${question}-${index}`}
            type="button"
            onClick={() => onSelect(question)}
            disabled={disabled}
            className="ui-chip"
            whileHover={{ y: -2 }}
            whileTap={{ scale: 0.98 }}
          >
            {question}
          </motion.button>
        ))}
      </div>
    </motion.div>
  )
}

export default SuggestedQuestions
