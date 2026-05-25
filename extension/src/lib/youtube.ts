export function getVideoIdFromUrl(url: string): string | null {
  try {
    const parsed = new URL(url)
    if (parsed.hostname.includes("youtu.be")) {
      return parsed.pathname.replace("/", "") || null
    }

    if (parsed.hostname.includes("youtube.com")) {
      const v = parsed.searchParams.get("v")
      if (v) {
        return v
      }

      const parts = parsed.pathname.split("/")
      const shortsIndex = parts.indexOf("shorts")
      if (shortsIndex >= 0 && parts[shortsIndex + 1]) {
        return parts[shortsIndex + 1]
      }
    }

    return null
  } catch {
    return null
  }
}

export function getVideoTitle(): string | null {
  const element = document.querySelector(
    "h1.title.style-scope.ytd-video-primary-info-renderer"
  )
  if (element && element.textContent) {
    return element.textContent.trim()
  }

  return document.title || null
}

  textarea.innerHTML = value
  return textarea.value
}
