/// <reference types="chrome" />

declare const process: {
  env: {
    PLASMO_PUBLIC_API_BASE_URL?: string
  }
}

declare module "*.css"
