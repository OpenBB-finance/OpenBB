import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";


const stripUseClientDirective = () => {
  return {
    name: 'strip-use-client',
    transform(code) {
      if (code.includes('use client')) {
        return {
          code: code.replace(/"use client"/, ''),
          map: null
        }
      }
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react(),
    stripUseClientDirective(),viteSingleFile()],
});
