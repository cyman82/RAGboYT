export type ContentRequestMessage = {
  type: "GET_VIDEO_CONTEXT"
}

export type ContentResponseMessage = {
  type: "VIDEO_CONTEXT"
  payload: {
    url: string
    videoId: string | null
    title: string | null
  }
}

export type SeekMessage = {
  type: "SEEK_TO"
  payload: {
    seconds: number
  }
}

export type ExtensionMessage =
  | ContentRequestMessage
  | ContentResponseMessage
  | SeekMessage
