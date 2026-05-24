import { motion } from "framer-motion"

import type { VideoContext } from "../../lib/types"

type HeaderProps = {
  video: VideoContext
}

// Parcel turns the project asset into a bundled URL for the extension panel.
const logoUrl = new URL("../../../assets/image.png", import.meta.url)
  .toString()

const Header = ({ video }: HeaderProps) => {
  return (
    <motion.header
      className="border-b border-line bg-haze/80 px-4 pb-4 pt-4 backdrop-blur-xl"
      initial={{ opacity: 0, y: -6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.24 }}
    >
      <div className="flex w-full justify-center">
        <img
          src={logoUrl}
          alt="YTBot"
          className="h-auto w-full max-w-[340px] object-contain drop-shadow-[0_14px_34px_rgba(66,198,207,0.14)]"
        />
      </div>
    </motion.header>
  )
}

export default Header
