import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#050a0e",
        panel: "#0b141b",
        line: "#24323a",
        signal: "#34d399",
        caution: "#fbbf24",
        danger: "#fb7185"
      },
      boxShadow: {
        "soft-border": "0 14px 42px rgba(0, 0, 0, 0.24)"
      }
    },
  },
  plugins: [],
};

export default config;
