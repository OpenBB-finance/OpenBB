import { spawn, type ChildProcess } from "node:child_process";
import type { IncomingMessage, ServerResponse } from "node:http";
import os from "node:os";
import path from "node:path";
import type { Plugin } from "vite";

interface GatewayRuntimeState {
  baseUrl: string | null;
  process: ChildProcess | null;
  readyPromise: Promise<string> | null;
}

const runtimeState: GatewayRuntimeState = {
  baseUrl: null,
  process: null,
  readyPromise: null,
};

function defaultSettingsPath(): string {
  return path.join(os.homedir(), ".openbb_platform", "user_settings.json");
}

function gatewayCommand(workspaceRoot: string): { command: string; args: string[] } {
  return {
    command: "cargo",
    args: [
      "run",
      "--manifest-path",
      path.join(workspaceRoot, "desktop", "src-tauri", "Cargo.toml"),
      "--bin",
      "openbb-ai-gateway",
      "--",
      "--host",
      "127.0.0.1",
      "--port",
      "0",
      "--settings",
      defaultSettingsPath(),
    ],
  };
}

async function ensureGateway(workspaceRoot: string): Promise<string> {
  if (runtimeState.baseUrl && runtimeState.process && runtimeState.process.exitCode === null) {
    return runtimeState.baseUrl;
  }
  if (runtimeState.readyPromise) {
    return runtimeState.readyPromise;
  }

  const { command, args } = gatewayCommand(workspaceRoot);
  runtimeState.readyPromise = new Promise<string>((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: workspaceRoot,
      env: process.env,
      stdio: ["ignore", "pipe", "pipe"],
    });
    runtimeState.process = child;

    let settled = false;
    const finishError = (error: Error) => {
      if (settled) {
        return;
      }
      settled = true;
      runtimeState.readyPromise = null;
      reject(error);
    };
    const finishSuccess = (baseUrl: string) => {
      if (settled) {
        return;
      }
      settled = true;
      runtimeState.baseUrl = baseUrl;
      runtimeState.readyPromise = null;
      resolve(baseUrl);
    };

    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");

    let stdoutBuffer = "";
    child.stdout.on("data", (chunk: string) => {
      stdoutBuffer += chunk;
      let newlineIndex = stdoutBuffer.indexOf("\n");
      while (newlineIndex >= 0) {
        const line = stdoutBuffer.slice(0, newlineIndex).trim();
        stdoutBuffer = stdoutBuffer.slice(newlineIndex + 1);
        if (line) {
          try {
            const payload = JSON.parse(line) as { type?: string; host?: string; port?: number };
            if (payload.type === "ready" && payload.port) {
              finishSuccess(`http://${payload.host ?? "127.0.0.1"}:${payload.port}`);
            }
          } catch {
            // Ignore log lines after readiness.
          }
        }
        newlineIndex = stdoutBuffer.indexOf("\n");
      }
    });

    child.stderr.on("data", (chunk: string) => {
      const text = chunk.trim();
      if (text) {
        // eslint-disable-next-line no-console
        console.warn(`[ai-gateway] ${text}`);
      }
    });

    child.on("error", (error) => {
      finishError(new Error(`Failed to start AI gateway: ${error.message}`));
    });
    child.on("exit", (code) => {
      runtimeState.process = null;
      runtimeState.baseUrl = null;
      if (!settled) {
        finishError(new Error(`AI gateway exited before readiness (code ${code ?? "unknown"}).`));
      }
    });
  });

  return runtimeState.readyPromise;
}

async function readRequestBody(req: IncomingMessage): Promise<Buffer | undefined> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  if (!chunks.length) {
    return undefined;
  }
  return Buffer.concat(chunks);
}

async function proxyRequest(baseUrl: string, req: IncomingMessage, res: ServerResponse) {
  const target = new URL(req.url?.replace(/^\/__ai/, "") || "/", `${baseUrl}/`);
  const body = req.method && ["POST", "PUT", "PATCH"].includes(req.method) ? await readRequestBody(req) : undefined;
  const headers = new Headers();
  for (const [key, value] of Object.entries(req.headers)) {
    if (!value || key.toLowerCase() === "host") {
      continue;
    }
    if (Array.isArray(value)) {
      for (const entry of value) {
        headers.append(key, entry);
      }
    } else {
      headers.set(key, value);
    }
  }

  const response = await fetch(target, {
    method: req.method,
    headers,
    body,
    duplex: body ? "half" : undefined,
  } as RequestInit);

  res.statusCode = response.status;
  response.headers.forEach((value, key) => {
    res.setHeader(key, value);
  });

  if (!response.body) {
    res.end();
    return;
  }

  const reader = response.body.getReader();
  while (true) {
    const { done, value } = await reader.read();
    if (done) {
      break;
    }
    res.write(Buffer.from(value));
  }
  res.end();
}

export function createAiBrowserFallbackPlugin(workspaceRoot: string): Plugin {
  return {
    name: "openbb-ai-gateway-proxy",
    configureServer(server) {
      server.middlewares.use("/__ai", async (req, res) => {
        try {
          const baseUrl = await ensureGateway(workspaceRoot);
          await proxyRequest(baseUrl, req, res);
        } catch (error) {
          res.statusCode = 500;
          res.setHeader("Content-Type", "application/json");
          res.end(
            JSON.stringify({
              error: error instanceof Error ? error.message : "Failed to start AI gateway.",
            }),
          );
        }
      });
    },
  };
}

export const __aiBrowserFallbackInternals = {
  defaultSettingsPath,
  gatewayCommand,
};
