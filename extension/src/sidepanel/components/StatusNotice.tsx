import { AlertTriangle, WifiOff } from "lucide-react"

type StatusNoticeProps = {
  tone: "warning" | "error"
  children: string
}

const StatusNotice = ({ tone, children }: StatusNoticeProps) => {
  const Icon = tone === "warning" ? WifiOff : AlertTriangle

  return (
    <div
      className={`rounded-2xl border px-3 py-2.5 text-compact shadow-soft ${
        tone === "warning"
          ? "border-amber/30 bg-amberSoft text-amber"
          : "border-red-400/25 bg-red-500/10 text-red-200"
      }`}
    >
      <div className="flex gap-2">
        <Icon className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
        <p>{children}</p>
      </div>
    </div>
  )
}

export default StatusNotice
