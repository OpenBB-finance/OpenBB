import path from "node:path";
import { Readable } from "node:stream";
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

async function readRequestBody(req: NodeJS.ReadableStream): Promise<Buffer> {
    const chunks: Buffer[] = [];
    for await (const chunk of req) {
        chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    }
    return Buffer.concat(chunks);
}

function buildProxyHeaders(headers: Record<string, string | string[] | undefined>): Headers {
    const forwarded = new Headers();
    for (const [key, value] of Object.entries(headers)) {
        if (!value) {
            continue;
        }

        const lower = key.toLowerCase();
        if (["host", "connection", "content-length", "origin", "referer"].includes(lower)) {
            continue;
        }

        if (Array.isArray(value)) {
            value.forEach((entry) => forwarded.append(key, entry));
        } else {
            forwarded.set(key, value);
        }
    }
    return forwarded;
}

function copyProxyResponseHeaders(source: Headers, target: import("node:http").ServerResponse): void {
    for (const [key, value] of source.entries()) {
        const lower = key.toLowerCase();
        if (["content-encoding", "content-length", "transfer-encoding", "connection"].includes(lower)) {
            continue;
        }
        target.setHeader(key, value);
    }
}

function packageChunkName(id: string): string | undefined {
    if (!id.includes("node_modules")) {
        return undefined;
    }

    if (id.includes("@openbb")) {
        return "vendor-openbb";
    }
    if (id.includes("@tanstack")) {
        return "vendor-tanstack";
    }
    if (id.includes("@tauri-apps")) {
        return "vendor-tauri";
    }
    if (id.includes("react-markdown")) {
        return "vendor-markdown";
    }
    if (id.includes("react-hook-form") || id.includes("@hookform")) {
        return "vendor-forms";
    }
    if (id.includes("echarts")) {
        return "vendor-echarts";
    }
    if (id.includes("recharts")) {
        return "vendor-recharts";
    }
    if (id.includes("react-dom") || id.includes("\\react\\") || id.includes("/react/")) {
        return "vendor-react";
    }

    return "vendor";
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
                server.middlewares.use("/__openbb_proxy", async (req, res) => {
                    const requestUrl = new URL(req.url ?? "/", "http://127.0.0.1:1470");
                    const target = requestUrl.searchParams.get("target");
                    const timeoutMs = Number.parseInt(requestUrl.searchParams.get("timeoutMs") ?? "30000", 10);

                    if (!target) {
                        res.statusCode = 400;
                        res.setHeader("Content-Type", "application/json");
                        res.end(JSON.stringify({ error: "target is required" }));
                        return;
                    }

                    let parsedTarget: URL;
                    try {
                        parsedTarget = new URL(target);
                    } catch {
                        res.statusCode = 400;
                        res.setHeader("Content-Type", "application/json");
                        res.end(JSON.stringify({ error: "target must be a valid URL" }));
                        return;
                    }

                    if (!["http:", "https:"].includes(parsedTarget.protocol) || !isLoopbackHost(parsedTarget.hostname)) {
                        res.statusCode = 403;
                        res.setHeader("Content-Type", "application/json");
                        res.end(JSON.stringify({ error: "target host is not allowed" }));
                        return;
                    }

                    const isEventStream = (req.headers.accept ?? "").includes("text/event-stream");

                    try {
                        const requestBody = req.method && !["GET", "HEAD"].includes(req.method.toUpperCase())
                            ? await readRequestBody(req)
                            : undefined;

                        const response = await fetch(parsedTarget, {
                            method: req.method ?? "GET",
                            headers: buildProxyHeaders(req.headers),
                            body: requestBody && requestBody.byteLength > 0 ? requestBody : undefined,
                            signal: isEventStream
                                ? undefined
                                : AbortSignal.timeout(Number.isFinite(timeoutMs) ? timeoutMs : 30000),
                            duplex: requestBody && requestBody.byteLength > 0 ? "half" : undefined,
                        });

                        res.statusCode = response.status;
                        copyProxyResponseHeaders(response.headers, res);

                        if (!response.body) {
                            res.end();
                            return;
                        }

                        if ((response.headers.get("content-type") ?? "").includes("text/event-stream")) {
                            Readable.fromWeb(response.body as globalThis.ReadableStream<Uint8Array>).pipe(res);
                            return;
                        }

                        const buffer = Buffer.from(await response.arrayBuffer());
                        res.end(buffer);
                    } catch (error) {
                        res.statusCode = 502;
                        res.setHeader("Content-Type", "application/json");
                        res.end(JSON.stringify({
                            error: error instanceof Error ? error.message : "proxy request failed",
                        }));
                    }
                });

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
                            headers: buildProxyHeaders(req.headers),
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
				    return packageChunkName(id);
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
