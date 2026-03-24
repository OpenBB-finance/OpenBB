import path from "node:path";
import { tanstackRouter } from "@tanstack/router-vite-plugin";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";
import { viteStaticCopy } from "vite-plugin-static-copy";
import svgr from "vite-plugin-svgr";
import { createAiBrowserFallbackPlugin } from "./dev/aiBrowserFallback";

const host = process.env.TAURI_DEV_HOST;

function isLoopbackHost(hostname: string): boolean {
    return hostname === "127.0.0.1" || hostname === "localhost" || hostname === "::1" || hostname.endsWith(".localhost");
}

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
        createAiBrowserFallbackPlugin(path.resolve(__dirname, "..")),
        {
            name: "openbb-dev-probe",
            configureServer(server) {
                server.middlewares.use("/__openbb_probe", async (req, res) => {
                    const requestUrl = new URL(req.url ?? "/", "http://127.0.0.1:1470");
                    const target = requestUrl.searchParams.get("target");
                    const timeoutMs = Number.parseInt(requestUrl.searchParams.get("timeoutMs") ?? "3000", 10);

                    if (!target) {
                        res.statusCode = 400;
                        res.setHeader("Content-Type", "application/json");
                        res.end(JSON.stringify({ ok: false, error: "target is required" }));
                        return;
                    }

                    let parsedTarget: URL;
                    try {
                        parsedTarget = new URL(target);
                    } catch {
                        res.statusCode = 400;
                        res.setHeader("Content-Type", "application/json");
                        res.end(JSON.stringify({ ok: false, error: "target must be a valid URL" }));
                        return;
                    }

                    if (!["http:", "https:"].includes(parsedTarget.protocol) || !isLoopbackHost(parsedTarget.hostname)) {
                        res.statusCode = 403;
                        res.setHeader("Content-Type", "application/json");
                        res.end(JSON.stringify({ ok: false, error: "target host is not allowed" }));
                        return;
                    }

                    try {
                        const response = await fetch(parsedTarget, {
                            method: "GET",
                            signal: AbortSignal.timeout(Number.isFinite(timeoutMs) ? timeoutMs : 3000),
                        });

                        res.statusCode = 200;
                        res.setHeader("Content-Type", "application/json");
                        res.end(JSON.stringify({ ok: response.ok, status: response.status }));
                    } catch (error) {
                        res.statusCode = 200;
                        res.setHeader("Content-Type", "application/json");
                        res.end(JSON.stringify({
                            ok: false,
                            status: 0,
                            error: error instanceof Error ? error.message : "probe failed",
                        }));
                    }
                });
            },
        },
        // TanStack Router owns routeTree.gen.ts generation during the build path.
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
