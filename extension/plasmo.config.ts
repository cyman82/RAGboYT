const config = {
  manifest: {
    name: "YouTube RAG Chatbot",
    version: "0.1.0",
    permissions: ["activeTab", "tabs", "sidePanel"],
    host_permissions: ["https://www.youtube.com/*", "https://youtu.be/*"],
    side_panel: {
      default_path: "sidepanel.html"
    }
  }
}

export default config
