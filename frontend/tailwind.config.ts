import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        sas_blue: "#0766D1",
        midnight_blue: "#032954",
        medium_blue: "#4398F9",
        light_blue: "#C4DEFD",
        slate: "#7E889A",
      },
    },
  },
  plugins: [],
};
export default config;
