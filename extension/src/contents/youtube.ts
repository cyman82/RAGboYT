import type { PlasmoContentScript } from "plasmo"

import type {
  ContentRequestMessage,
  ContentResponseMessage,
  ExtensionMessage,
  SeekMessage
} from "../lib/messages"
import {
  fetchTranscriptSegments,
  getVideoIdFromUrl,
  getVideoTitle
} from "../lib/youtube"

export const config: PlasmoContentScript = {
  matches: ["https://www.youtube.com/*", "https://youtu.be/*"],
  run_at: "document_idle"
}

export {}

chrome.runtime.onMessage.addListener(
  (
    message: ExtensionMessage,
    _sender,
    sendResponse
  ) => {
    if (message.type === "GET_VIDEO_CONTEXT") {
      const response: ContentResponseMessage = {
        type: "VIDEO_CONTEXT",
        payload: {
          url: window.location.href,
          videoId: getVideoIdFromUrl(window.location.href),
          title: getVideoTitle()
        }
      }
      sendResponse(response)
      return true
    }

    if (message.type === "GET_TRANSCRIPT") {
      const videoId = getVideoIdFromUrl(window.location.href)
      if (!videoId) {
        sendResponse({
          type: "TRANSCRIPT",
          payload: {
            url: window.location.href,
            videoId: null,
            title: getVideoTitle(),
            transcript: [],
            error: "Unable to determine video ID."
          }
        })
        return true
      }

      fetchTranscriptSegments(videoId)
        .then((transcript) => {
          sendResponse({
            type: "TRANSCRIPT",
            payload: {
              url: window.location.href,
              videoId,
              title: getVideoTitle(),
              transcript
            }
          })
        })
        .catch((error) => {
          sendResponse({
            type: "TRANSCRIPT",
            payload: {
              url: window.location.href,
              videoId,
              title: getVideoTitle(),
              transcript: [],
              error: error instanceof Error ? error.message : "Transcript fetch failed"
            }
          })
        })
      return true
    }

    if (message.type === "SEEK_TO") {
      const payload = (message as SeekMessage).payload
      const video = document.querySelector("video")
      if (video) {
        video.currentTime = payload.seconds
        video.play().catch(() => undefined)
      }
      sendResponse({ ok: true })
      return true
    }

    return false
  }
)
