import { motion } from "framer-motion"
import { PlayCircle, Radio, SquarePlay } from "lucide-react"

import type { VideoContext } from "../../lib/types"

type VideoPreviewProps = {
  video: VideoContext
}

const VideoPreview = ({ video }: VideoPreviewProps) => {
  const thumbnailUrl = video.videoId
    ? `https://i.ytimg.com/vi/${video.videoId}/hqdefault.jpg`
    : ""

  return (
    <motion.section
      className="glass-card overflow-hidden"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.22 }}
    >
      <div className="relative aspect-video bg-slate-950">
        {thumbnailUrl ? (
          <img
            src={thumbnailUrl}
            alt=""
            className="h-full w-full object-cover opacity-85 transition duration-300 hover:scale-[1.015]"
          />
        ) : (
          <div className="flex h-full items-center justify-center bg-gradient-to-br from-panelElevated to-haze">
            <SquarePlay className="h-9 w-9 text-muted" aria-hidden="true" />
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-haze via-haze/10 to-transparent" />
        <div className="absolute bottom-3 left-3 flex items-center gap-2 rounded-full border border-white/10 bg-black/45 px-2.5 py-1 text-[11px] font-medium text-slate-100 backdrop-blur">
          <PlayCircle className="h-3.5 w-3.5 text-youtube" aria-hidden="true" />
          Current video
        </div>
      </div>

      <div className="space-y-2 p-3.5">
        <h2 className="line-clamp-2 text-[15px] font-semibold leading-5 text-slate-50">
          {video.title || "Open a YouTube video to begin"}
        </h2>
        <div className="flex items-center justify-between gap-3 text-[11px] text-muted">
          <span className="inline-flex min-w-0 items-center gap-1.5">
            <Radio className="h-3.5 w-3.5 shrink-0 text-teal" aria-hidden="true" />
            <span className="truncate">
              {video.videoId ? `ID ${video.videoId}` : "No video detected"}
            </span>
          </span>
          <span className="rounded-full border border-line bg-white/[0.04] px-2 py-0.5 text-[10px] text-slate-300">
            RAG ready
          </span>
        </div>
      </div>
    </motion.section>
  )
}

export default VideoPreview
