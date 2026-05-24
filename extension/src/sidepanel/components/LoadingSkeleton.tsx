import { motion } from "framer-motion"

const LoadingSkeleton = () => {
  return (
    <motion.div
      className="space-y-4"
      role="status"
      aria-label="Preparing answer"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
    >
      <div className="rounded-2xl border border-teal/20 bg-panel p-4 shadow-circuit">
        <div className="flex items-center justify-between">
          <div className="h-3 w-24 animate-shimmer rounded-full" />
          <div className="h-6 w-20 animate-shimmer rounded-full" />
        </div>
        <div className="mt-5 space-y-2.5">
          <div className="h-3 w-full animate-shimmer rounded-full" />
          <div className="h-3 w-11/12 animate-shimmer rounded-full" />
          <div className="h-3 w-4/5 animate-shimmer rounded-full" />
        </div>
        <div className="mt-5 h-8 w-44 animate-shimmer rounded-full" />
      </div>

      <div className="rounded-2xl border border-line bg-panel bg-opacity-80 p-4 shadow-soft">
        <div className="h-3 w-28 animate-shimmer rounded-full" />
        <div className="mt-4 space-y-3">
          {[0, 1, 2].map((item) => (
            <div
              key={item}
              className="rounded-2xl border border-line bg-white/[0.035] p-3"
            >
              <div className="flex items-center justify-between">
                <div className="h-3 w-24 animate-shimmer rounded-full" />
                <div className="h-3 w-20 animate-shimmer rounded-full" />
              </div>
              <div className="mt-3 h-3 w-full animate-shimmer rounded-full" />
              <div className="mt-2 h-3 w-3/4 animate-shimmer rounded-full" />
            </div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

export default LoadingSkeleton
