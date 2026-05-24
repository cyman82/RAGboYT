module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        ink: "#f8fafc",
        haze: "#0b0f14",
        panel: "rgb(17 24 32 / <alpha-value>)",
        panelElevated: "rgb(22 31 41 / <alpha-value>)",
        line: "rgba(148, 163, 184, 0.16)",
        muted: "#94a3b8",
        teal: "rgb(66 198 207 / <alpha-value>)",
        tealSoft: "rgba(66, 198, 207, 0.12)",
        amber: "#d4a574",
        amberSoft: "rgba(212, 165, 116, 0.14)",
        youtube: "rgb(255 59 48 / <alpha-value>)",
        accent: "#42c6cf",
        ember: "#b9824e"
      },
      boxShadow: {
        soft: "0 16px 48px rgba(0, 0, 0, 0.28)",
        circuit: "0 18px 56px rgba(66, 198, 207, 0.12)",
        glow: "0 0 0 1px rgba(66, 198, 207, 0.18), 0 18px 60px rgba(0, 0, 0, 0.35)"
      },
      fontSize: {
        micro: ["10px", "14px"],
        compact: ["12px", "18px"],
        body: ["13px", "21px"]
      }
    }
  },
  plugins: []
}
