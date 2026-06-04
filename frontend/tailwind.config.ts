import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#08111f",
        panel: "#101b2d",
        line: "#26344f",
        signal: "#34d399",
        caution: "#f59e0b",
        danger: "#fb7185"
      },
      boxShadow: {
        "soft-border": "0 0 0 1px rgba(148, 163, 184, 0.14)"
      }
    },
  },
  plugins: [],
};

export default config;
