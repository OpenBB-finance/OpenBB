import path from "node:path";
import { tanstackRouter } from "@tanstack/router-vite-plugin";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";
import svgr from "vite-plugin-svgr";

const host = process.env.TAURI_DEV_HOST;

export default defineConfig(async () => ({
    resolve: {
        alias: {
            "~": path.resolve(__dirname, "./src"),
        },
    },
    plugins: [
        react(),
        svgr(),
        viteStaticCopy({
            targets: [{ src: "./node_modules/@openbb/ui-pro/dist/assets", dest: "" }],
        }),
        tanstackRouter(),
    ],

    base: "./",
    build: {
        outDir: "dist",
        emptyOutDir: true,
        sourcemap: true,
        chunkSizeWarningLimit: 1000, // Increase chunk size warning limit to 1MB
        rollupOptions: {
			output: {
				manualChunks(id: string) {
				if (id.includes('node_modules')) {
					if (id.includes('@openbb')) {
					return 'vendor-openbb';
					}
					if (id.includes('@tanstack')) {
					return 'vendor-tanstack';
					}
					return 'vendor';
				}
				}
			}
		}
    },
    clearScreen: false,
    server: {
        port: 1470,
        strictPort: true,
        host: host || false,
        hmr: host
            ? {
                    protocol: "ws",
                    host,
                    port: 1421,
                }
            : undefined,
        watch: {
            ignored: ["**/src-tauri/**"],
        },
    },
}));