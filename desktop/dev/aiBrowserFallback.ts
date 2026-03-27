import crypto from "node:crypto";
import fs from "node:fs";
import fsp from "node:fs/promises";
import type { IncomingMessage, ServerResponse } from "node:http";
import os from "node:os";
import path from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import type { Plugin } from "vite";

const execFileAsync = promisify(execFile);

const OLLAMA_BASE_URL = "http://localhost:11434/api";
const MAX_FILE_SIZE_BYTES = 256 * 1024;
const CHUNK_LINES = 120;
const CHUNK_OVERLAP = 20;
const MAX_INDEX_LINE_CHARS = 1200;
const MAX_INDEX_CHUNK_CHARS = 8000;
const MAX_EMBED_INPUT_CHARS = 2000;
const DEFAULT_CONTEXT_CHUNKS = 10;
const MAX_CONTEXT_CHUNKS = 16;
const MAX_SEMANTIC_CANDIDATES = 12;
const MAX_CHAT_CANDIDATES = 4;
const CHAT_KEEP_ALIVE = "15m";
const CHAT_REQUEST_TIMEOUT_MS = 45000;
const EMBED_BATCH_SIZE = 4;
const DISCOVERY_CACHE_TTL_MS = 30000;
const GIT_REVISION_CACHE_TTL_MS = 30000;
const SUMMARY_CHUNK_PATH = "__project_summary__.md";
const PINNED_PATHS = [
  "README.md",
  "desktop/src/routes/__root.tsx",
  "desktop/src-tauri/src/main.rs",
];
const EXCLUDED_DIRS = new Set([
  ".git",
  "node_modules",
  "dist",
  "target",
  ".venv",
  "logs",
  "build",
  ".playwright-cli",
]);
const ALLOWED_EXTENSIONS = new Set([
  ".ts",
  ".tsx",
  ".js",
  ".jsx",
  ".rs",
  ".py",
  ".md",
  ".toml",
  ".json",
  ".yml",
  ".yaml",
  ".ps1",
]);
const LOCKFILES = new Set([
  "package-lock.json",
  "pnpm-lock.yaml",
  "yarn.lock",
  "poetry.lock",
  "uv.lock",
  "Cargo.lock",
  "bun.lockb",
  "composer.lock",
]);
const NOISY_PATH_PATTERNS = [
  /(^|\/)(tests?|__tests__)\/record\//i,
  /(^|\/)record\/http\//i,
];
const STOPWORDS = new Set([
  "how",
  "does",
  "this",
  "that",
  "the",
  "and",
  "for",
  "from",
  "with",
  "into",
  "what",
  "when",
  "where",
  "which",
  "why",
  "please",
  "could",
  "would",
  "should",
  "project",
  "explain",
  "about",
  "tell",
  "show",
  "give",
  "there",
  "their",
  "uses",
  "using",
]);
const ENDPOINT_QUERY_PATTERN =
  /(endpoint|endpoints|route|routes|command|commands|handler|handlers|api|apis|path|paths|url|urls|invoke|invokes|expose|exposes|tauri|middleware)/i;
const ROUTE_LITERAL_PATTERN = /["'`](\/[A-Za-z0-9_./:-]+)["'`]/g;
const ENDPOINT_ROUTE_MARKERS: Array<[string, number]> = [
  ['server.middlewares.use("/__ai"', 26],
  ['server.middlewares.use("/"', 10],
  ["requesturl.pathname ===", 16],
  ['req.method === "get"', 6],
  ['req.method === "post"', 6],
  ["#[tauri::command]", 20],
  ["generate_handler!(", 18],
  ["invoke_handler(", 12],
  ['jsonresponse(res, 200', 4],
  ['jsonresponse(res, 400', 3],
  ['jsonresponse(res, 404', 3],
];

type RetrievalMode = "semantic" | "lexical" | "supplemental";
type AiChatRole = "user" | "assistant";

interface AiStatus {
  repoRoot: string | null;
  repoReady: boolean;
  ollamaReachable: boolean;
  chatModel: string | null;
  chatCandidates: string[];
  embeddingModel: string | null;
  availableModels: string[];
  indexReady: boolean;
  lastIndexedAt: string | null;
  chunkCount: number;
  mode: RetrievalMode;
}

interface AiIndexResult {
  repoRoot: string;
  scannedFiles: number;
  indexedFiles: number;
  skippedFiles: number;
  chunkCount: number;
  lastIndexedAt: string;
  revision: string;
}

interface AiCitation {
  path: string;
  startLine: number;
  endLine: number;
  score: number;
}

interface AiAskRequest {
  repoRoot: string;
  messages: Array<{ role: AiChatRole; content: string }>;
  maxContextChunks?: number;
  supplementalContext?: string;
  supplementalOnly?: boolean;
}

interface AiAskResponse {
  answer: string;
  citations: AiCitation[];
  usedModel: string;
  attemptedModels?: string[];
  modelTotalMs?: number | null;
  loadMs?: number | null;
  promptEvalMs?: number | null;
  evalMs?: number | null;
  timingMs: number;
  retrievalMode: RetrievalMode;
}

interface BrowserAiManifest {
  repoRoot: string;
  repoHash: string;
  headRevision: string;
  configHash: string;
  revision: string;
  scannedFiles: number;
  indexedFiles: number;
  skippedFiles: number;
  chunkCount: number;
  lastIndexedAt: string;
  embeddingModel: string | null;
  embeddingDim: number | null;
  mode: RetrievalMode;
  summaryPrompt: string;
}

interface IndexedChunk {
  path: string;
  startLine: number;
  endLine: number;
  sha1: string;
  language: string;
  text: string;
}

interface CachedIndex {
  manifest: BrowserAiManifest;
  chunks: IndexedChunk[];
  embeddings: number[][];
}

interface OllamaModel {
  name: string;
  size?: number;
  details?: {
    parameter_size?: string;
  };
}

interface OllamaDiscovery {
  reachable: boolean;
  availableModels: string[];
  chatModel: string | null;
  chatCandidates: string[];
  embeddingModel: string | null;
  mode: RetrievalMode;
}

interface RankedChunk {
  index: number;
  score: number;
}

const indexCache = new Map<string, CachedIndex>();
const warmModelPromises = new Map<string, Promise<string | null>>();
let discoveryCache: { expiresAt: number; value: OllamaDiscovery } | null = null;
const gitRevisionCache = new Map<string, { expiresAt: number; revision: string }>();

function sha1Hex(input: string | Buffer): string {
  return crypto.createHash("sha1").update(input).digest("hex");
}

function jsonResponse(res: ServerResponse, status: number, payload: unknown): void {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(payload));
}

async function readJsonBody(req: IncomingMessage): Promise<unknown> {
  const chunks: Buffer[] = [];
  for await (const chunk of req) {
    chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
  }
  if (chunks.length === 0) {
    return {};
  }
  return JSON.parse(Buffer.concat(chunks).toString("utf8"));
}

function isGitRepo(directory: string): boolean {
  return fs.existsSync(path.join(directory, ".git"));
}

function resolveRepoRoot(workspaceRoot: string, defaultDir: string): string | null {
  const candidates = [
    path.resolve(workspaceRoot, defaultDir || "."),
    workspaceRoot,
    path.resolve(workspaceRoot, ".."),
  ];

  for (const candidate of candidates) {
    if (isGitRepo(candidate)) {
      return candidate;
    }
  }

  return null;
}

function resolveRequestedRepoRoot(workspaceRoot: string, requestedRepoRoot?: string): string | null {
  if (requestedRepoRoot) {
    const normalized = path.resolve(requestedRepoRoot);
    if (fs.existsSync(normalized)) {
      return normalized;
    }
  }

  return resolveRepoRoot(workspaceRoot, ".");
}

async function fetchJson<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, init);
  if (!response.ok) {
    throw new Error(`${url} returned ${response.status}`);
  }
  return response.json() as Promise<T>;
}

function modelBaseName(modelName: string): string {
  return modelName.split(":")[0] ?? modelName;
}

function parseParameterSize(input: string | undefined): number | null {
  if (!input) {
    return null;
  }

  const normalized = input.trim().toUpperCase();
  if (normalized.endsWith("B")) {
    const value = Number.parseFloat(normalized.slice(0, -1));
    return Number.isFinite(value) ? value : null;
  }
  if (normalized.endsWith("M")) {
    const value = Number.parseFloat(normalized.slice(0, -1));
    return Number.isFinite(value) ? value / 1000 : null;
  }
  return null;
}

function isEmbeddingOnlyModelName(modelName: string): boolean {
  const normalized = modelName.toLowerCase();
  return (
    normalized.includes("embed")
    || normalized.includes("embedding")
    || normalized.includes("minilm")
    || normalized.includes("nomic")
    || normalized.includes("bge")
    || normalized.includes("e5")
  );
}

function chatModelPriority(model: OllamaModel): number {
  const normalized = model.name.toLowerCase();
  if (isEmbeddingOnlyModelName(normalized)) {
    return 99;
  }
  if (normalized.includes("coder")) {
    return 0;
  }
  if (normalized.includes("instruct") || normalized.includes("chat")) {
    return 1;
  }
  if (
    normalized.includes("qwen")
    || normalized.includes("llama")
    || normalized.includes("mistral")
    || normalized.includes("gemma")
    || normalized.includes("phi")
  ) {
    return 2;
  }
  return 3;
}

function sortChatCandidates(models: OllamaModel[]): OllamaModel[] {
  return [...models]
    .filter((model) => !isEmbeddingOnlyModelName(model.name))
    .sort((left, right) => {
    const priorityDelta = chatModelPriority(left) - chatModelPriority(right);
    if (priorityDelta !== 0) {
      return priorityDelta;
    }

    const leftParams = parseParameterSize(left.details?.parameter_size);
    const rightParams = parseParameterSize(right.details?.parameter_size);
    if (leftParams !== null && rightParams !== null && leftParams !== rightParams) {
      return leftParams - rightParams;
    }
    if (leftParams !== null && rightParams === null) {
      return -1;
    }
    if (leftParams === null && rightParams !== null) {
      return 1;
    }

    const leftSize = left.size ?? Number.MAX_SAFE_INTEGER;
    const rightSize = right.size ?? Number.MAX_SAFE_INTEGER;
    if (leftSize !== rightSize) {
      return leftSize - rightSize;
    }

    return left.name.localeCompare(right.name);
    })
    .slice(0, MAX_CHAT_CANDIDATES);
}

function ollamaDurationToMs(value: unknown): number | null {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0) {
    return null;
  }

  return Math.round(value / 1_000_000);
}

async function canUseEmbeddingModel(model: string): Promise<boolean> {
  try {
    const response = await fetchJson<{ embeddings?: number[][] }>(`${OLLAMA_BASE_URL}/embed`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model,
        input: "ping",
        truncate: true,
      }),
    });

    return Boolean(response.embeddings?.[0]?.length);
  } catch {
    return false;
  }
}

async function chooseEmbeddingModel(models: OllamaModel[]): Promise<string | null> {
  const exactPreferences = ["qwen3-embedding", "embeddinggemma", "all-minilm"];

  for (const preferred of exactPreferences) {
    const match = models.find((model) => modelBaseName(model.name).toLowerCase() === preferred);
    if (match && await canUseEmbeddingModel(match.name)) {
      return match.name;
    }
  }

  for (const model of models) {
    if (model.name.toLowerCase().includes("embed") && await canUseEmbeddingModel(model.name)) {
      return model.name;
    }
  }

  return null;
}

async function discoverOllama(): Promise<OllamaDiscovery> {
  if (discoveryCache && Date.now() < discoveryCache.expiresAt) {
    return discoveryCache.value;
  }

  try {
    const payload = await fetchJson<{ models?: OllamaModel[] }>(`${OLLAMA_BASE_URL}/tags`);
    const models = Array.isArray(payload.models) ? payload.models : [];
    const availableModels = models.map((model) => model.name);
    const chatCandidates = sortChatCandidates(models).map((model) => model.name);
    const embeddingModel = await chooseEmbeddingModel(models);

    const discovery: OllamaDiscovery = {
      reachable: true,
      availableModels,
      chatModel: chatCandidates[0] ?? null,
      chatCandidates,
      embeddingModel,
      mode: embeddingModel ? "semantic" : "lexical",
    };
    discoveryCache = {
      expiresAt: Date.now() + DISCOVERY_CACHE_TTL_MS,
      value: discovery,
    };
    return discovery;
  } catch {
    const discovery: OllamaDiscovery = {
      reachable: false,
      availableModels: [],
      chatModel: null,
      chatCandidates: [],
      embeddingModel: null,
      mode: "lexical",
    };
    discoveryCache = {
      expiresAt: Date.now() + DISCOVERY_CACHE_TTL_MS,
      value: discovery,
    };
    return discovery;
  }
}

async function gitHeadRevision(repoRoot: string): Promise<string> {
  const cached = gitRevisionCache.get(repoRoot);
  if (cached && Date.now() < cached.expiresAt) {
    return cached.revision;
  }

  try {
    const { stdout } = await execFileAsync("git", ["-C", repoRoot, "rev-parse", "HEAD"], {
      windowsHide: true,
      timeout: 10000,
    });
    const revision = stdout.trim();
    const nextRevision = revision || "nogit";
    gitRevisionCache.set(repoRoot, {
      expiresAt: Date.now() + GIT_REVISION_CACHE_TTL_MS,
      revision: nextRevision,
    });
    return nextRevision;
  } catch {
    gitRevisionCache.set(repoRoot, {
      expiresAt: Date.now() + GIT_REVISION_CACHE_TTL_MS,
      revision: "nogit",
    });
    return "nogit";
  }
}

async function buildIndexContext(repoRoot: string, _embeddingModel: string | null) {
  const repoHash = sha1Hex(repoRoot);
  const headRevision = await gitHeadRevision(repoRoot);
  const configHash = sha1Hex([
    `chunk_lines=${CHUNK_LINES}`,
    `chunk_overlap=${CHUNK_OVERLAP}`,
    `max_file_size=${MAX_FILE_SIZE_BYTES}`,
    `max_index_line_chars=${MAX_INDEX_LINE_CHARS}`,
    `max_index_chunk_chars=${MAX_INDEX_CHUNK_CHARS}`,
    `max_embed_input_chars=${MAX_EMBED_INPUT_CHARS}`,
    `extensions=${Array.from(ALLOWED_EXTENSIONS).join(",")}`,
    `excluded_dirs=${Array.from(EXCLUDED_DIRS).join(",")}`,
    `noisy_path_patterns=${NOISY_PATH_PATTERNS.map((pattern) => pattern.source).join(",")}`,
    "retrieval_mode=dynamic",
  ].join(";"));
  const revision = sha1Hex(`${repoRoot}\n${headRevision}\n${configHash}`);

  return {
    repoHash,
    headRevision,
    configHash,
    revision,
  };
}

function isManifestReusable(
  manifest: BrowserAiManifest | null,
  context: Awaited<ReturnType<typeof buildIndexContext>>,
  repoRoot: string,
): manifest is BrowserAiManifest {
  if (!manifest) {
    return false;
  }

  return (
    manifest.repoHash === context.repoHash
    && path.resolve(manifest.repoRoot) === path.resolve(repoRoot)
    && manifest.headRevision === context.headRevision
    && manifest.chunkCount > 0
  );
}

function browserIndexDirectory(repoHash: string): string {
  return path.join(os.homedir(), ".openbb_platform", "ai_index_browser", repoHash);
}

function manifestPath(indexDir: string): string {
  return path.join(indexDir, "manifest.json");
}

function chunksPath(indexDir: string): string {
  return path.join(indexDir, "chunks.jsonl");
}

function embeddingsPath(indexDir: string): string {
  return path.join(indexDir, "embeddings.json");
}

function shouldSkipRelativePath(relativePath: string): boolean {
  const normalized = relativePath.replace(/\\/g, "/");
  const basename = path.basename(normalized);
  const segments = normalized.split("/");
  if (
    LOCKFILES.has(basename)
    || basename.endsWith(".min.js")
    || segments.some((segment) => EXCLUDED_DIRS.has(segment))
    || NOISY_PATH_PATTERNS.some((pattern) => pattern.test(normalized))
  ) {
    return true;
  }

  return !ALLOWED_EXTENSIONS.has(path.extname(normalized).toLowerCase());
}

function shouldIncludeFile(relativePath: string, stat: fs.Stats): boolean {
  if (!stat.isFile()) {
    return false;
  }
  if (stat.size > MAX_FILE_SIZE_BYTES) {
    return false;
  }

  return !shouldSkipRelativePath(relativePath);
}

async function listGitFiles(repoRoot: string): Promise<string[]> {
  const { stdout } = await execFileAsync("git", ["-C", repoRoot, "ls-files"], {
    windowsHide: true,
    timeout: 30000,
    maxBuffer: 20 * 1024 * 1024,
  });

  return stdout
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

async function walkFiles(directory: string, rootDir: string, output: string[]): Promise<void> {
  const entries = await fsp.readdir(directory, { withFileTypes: true });

  for (const entry of entries) {
    const absolutePath = path.join(directory, entry.name);
    const relativePath = path.relative(rootDir, absolutePath).replace(/\\/g, "/");

    if (entry.isDirectory()) {
      if (!EXCLUDED_DIRS.has(entry.name)) {
        await walkFiles(absolutePath, rootDir, output);
      }
      continue;
    }

    const stat = await fsp.stat(absolutePath);
    if (shouldIncludeFile(relativePath, stat)) {
      output.push(relativePath);
    }
  }
}

async function collectCandidateFiles(repoRoot: string): Promise<string[]> {
  try {
    const tracked = await listGitFiles(repoRoot);
    const filtered: string[] = [];

    for (const relativePath of tracked) {
      const absolutePath = path.join(repoRoot, relativePath);
      try {
        const stat = await fsp.stat(absolutePath);
        if (shouldIncludeFile(relativePath, stat)) {
          filtered.push(relativePath.replace(/\\/g, "/"));
        }
      } catch {
        // Ignore files that disappear during the scan.
      }
    }

    return filtered;
  } catch {
    const fallback: string[] = [];
    await walkFiles(repoRoot, repoRoot, fallback);
    return fallback;
  }
}

function detectLanguage(relativePath: string): string {
  const ext = path.extname(relativePath).toLowerCase();
  return ext ? ext.slice(1) : "text";
}

function truncateIndexedLine(line: string): string {
  if (line.length <= MAX_INDEX_LINE_CHARS) {
    return line;
  }
  return `${line.slice(0, MAX_INDEX_LINE_CHARS)} …[line truncated for AI index]`;
}

function truncateChunkBody(body: string): string {
  if (body.length <= MAX_INDEX_CHUNK_CHARS) {
    return body;
  }
  return `${body.slice(0, MAX_INDEX_CHUNK_CHARS)}\n...[chunk truncated for AI index]`;
}

function buildEmbeddingInput(chunk: IndexedChunk): string {
  const prefix = `${chunk.path}:${chunk.startLine}-${chunk.endLine}\n`;
  const remaining = Math.max(256, MAX_EMBED_INPUT_CHARS - prefix.length);
  const body = chunk.text.length > remaining
    ? `${chunk.text.slice(0, remaining)}\n...[embedding input truncated]`
    : chunk.text;
  return `${prefix}${body}`;
}

function chunkText(relativePath: string, text: string): IndexedChunk[] {
  const normalizedText = text.replace(/\r\n/g, "\n");
  const lines = normalizedText.split("\n");
  const chunks: IndexedChunk[] = [];
  const step = Math.max(1, CHUNK_LINES - CHUNK_OVERLAP);

  for (let start = 0; start < lines.length; start += step) {
    const end = Math.min(lines.length, start + CHUNK_LINES);
    const chunkLines = lines.slice(start, end).map(truncateIndexedLine);
    const chunkBody = truncateChunkBody(chunkLines.join("\n").trim());

    if (chunkBody.length > 0) {
      chunks.push({
        path: relativePath,
        startLine: start + 1,
        endLine: end,
        sha1: sha1Hex(chunkBody),
        language: detectLanguage(relativePath),
        text: chunkBody,
      });
    }

    if (end >= lines.length) {
      break;
    }
  }

  return chunks;
}

async function readTextFile(filePath: string): Promise<string | null> {
  try {
    const content = await fsp.readFile(filePath, "utf8");
    if (content.includes("\u0000")) {
      return null;
    }
    return content;
  } catch {
    return null;
  }
}

async function buildSummaryPrompt(repoRoot: string): Promise<string> {
  const lines: string[] = [];

  lines.push("# Repository Summary");
  lines.push(`Repo root: ${repoRoot}`);

  try {
    const rootEntries = await fsp.readdir(repoRoot, { withFileTypes: true });
    const topLevel = rootEntries
      .filter((entry) => !entry.name.startsWith("."))
      .map((entry) => entry.name)
      .sort()
      .slice(0, 32);
    lines.push(`Top-level entries: ${topLevel.join(", ")}`);
  } catch {
    // Ignore summary enrichment failures.
  }

  try {
    const routesDir = path.join(repoRoot, "desktop", "src", "routes");
    const routeEntries = await fsp.readdir(routesDir, { withFileTypes: true });
    const routes = routeEntries
      .filter((entry) => entry.isFile() && /\.(ts|tsx)$/.test(entry.name))
      .map((entry) => entry.name)
      .sort()
      .slice(0, 64);
    lines.push(`Desktop routes: ${routes.join(", ")}`);
  } catch {
    // Ignore summary enrichment failures.
  }

  try {
    const mainSource = await readTextFile(path.join(repoRoot, "desktop", "src-tauri", "src", "main.rs"));
    if (mainSource) {
      const handlerMatch = mainSource.match(/generate_handler!\s*\[([\s\S]*?)\]/m);
      if (handlerMatch?.[1]) {
        const commands = handlerMatch[1]
          .split(",")
          .map((value) => value.trim())
          .filter(Boolean)
          .slice(0, 48);
        lines.push(`Tauri commands: ${commands.join(", ")}`);
      }
    }
  } catch {
    // Ignore summary enrichment failures.
  }

  const readme = await readTextFile(path.join(repoRoot, "README.md"));
  if (readme) {
    lines.push(`README excerpt: ${readme.replace(/\s+/g, " ").trim().slice(0, 1600)}`);
  }

  lines.push("Backend resolution references: desktop/src/lib/openbbBackend.ts, desktop/src/routes/quant.tsx, desktop/src/routes/dashboard.tsx");

  return lines.join("\n");
}

async function writeIndex(
  indexDir: string,
  manifest: BrowserAiManifest,
  chunks: IndexedChunk[],
  embeddings: number[][],
): Promise<void> {
  await fsp.mkdir(indexDir, { recursive: true });
  await fsp.writeFile(manifestPath(indexDir), JSON.stringify(manifest, null, 2), "utf8");
  const serializedChunks = chunks.map((chunk) => JSON.stringify(chunk)).join("\n");
  await fsp.writeFile(chunksPath(indexDir), serializedChunks, "utf8");
  await fsp.writeFile(embeddingsPath(indexDir), JSON.stringify(embeddings), "utf8");
}

async function readManifest(indexDir: string): Promise<BrowserAiManifest | null> {
  try {
    const content = await fsp.readFile(manifestPath(indexDir), "utf8");
    return JSON.parse(content) as BrowserAiManifest;
  } catch {
    return null;
  }
}

async function readChunks(indexDir: string): Promise<IndexedChunk[]> {
  try {
    const content = await fsp.readFile(chunksPath(indexDir), "utf8");
    return content
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => JSON.parse(line) as IndexedChunk);
  } catch {
    return [];
  }
}

async function readEmbeddings(indexDir: string): Promise<number[][]> {
  try {
    const content = await fsp.readFile(embeddingsPath(indexDir), "utf8");
    const parsed = JSON.parse(content) as unknown;
    return Array.isArray(parsed)
      ? parsed.filter((value): value is number[] => Array.isArray(value))
      : [];
  } catch {
    return [];
  }
}

async function loadIndex(repoRoot: string, embeddingModel: string | null): Promise<CachedIndex | null> {
  const context = await buildIndexContext(repoRoot, embeddingModel);
  const cached = indexCache.get(context.repoHash);
  if (cached && isManifestReusable(cached.manifest, context, repoRoot)) {
    return cached;
  }

  const indexDir = browserIndexDirectory(context.repoHash);
  const manifest = await readManifest(indexDir);
  if (!isManifestReusable(manifest, context, repoRoot)) {
    return null;
  }

  const chunks = await readChunks(indexDir);
  const embeddings = await readEmbeddings(indexDir);
  const index = { manifest, chunks, embeddings };
  indexCache.set(context.repoHash, index);
  return index;
}

function tokenize(input: string): string[] {
  const baseTokens = input
    .replace(/([a-z0-9])([A-Z])/g, "$1 $2")
    .toLowerCase()
    .split(/[^a-z0-9_./-]+/i)
    .map((token) => token.trim())
    .filter((token) => token.length >= 2 && !STOPWORDS.has(token));

  const combinedTokens: string[] = [];
  for (let index = 0; index < baseTokens.length - 1; index += 1) {
    combinedTokens.push(`${baseTokens[index]}${baseTokens[index + 1]}`);
  }

  return Array.from(new Set([...baseTokens, ...combinedTokens]));
}

function hasEndpointIntent(query: string, queryTokens: string[]): boolean {
  return ENDPOINT_QUERY_PATTERN.test(query)
    || queryTokens.some((token) => token.includes("/") || token.includes("__"));
}

function countSubstringOccurrences(haystack: string, needle: string): number {
  if (!needle) {
    return 0;
  }
  let count = 0;
  let offset = 0;
  while (true) {
    const next = haystack.indexOf(needle, offset);
    if (next === -1) {
      return count;
    }
    count += 1;
    offset = next + needle.length;
  }
}

function countLiteralRouteStrings(input: string): number {
  return Array.from(input.matchAll(ROUTE_LITERAL_PATTERN)).length;
}

function lexicalScore(query: string, queryTokens: string[], chunk: IndexedChunk): number {
  if (queryTokens.length === 0) {
    return 0;
  }

  const queryLower = query.toLowerCase();
  const haystack = `${chunk.path}\n${chunk.text}`.toLowerCase();
  const pathValue = chunk.path.toLowerCase();
  const basename = path.basename(pathValue).toLowerCase();
  const compactPath = pathValue.replace(/[^a-z0-9]+/g, "");
  const compactBasename = basename.replace(/[^a-z0-9]+/g, "");
  const compactQuery = queryTokens.join("");
  const endpointIntent = hasEndpointIntent(query, queryTokens);
  const uniqueTokens = Array.from(new Set(queryTokens));
  let score = 0;

  for (const token of uniqueTokens) {
    if (pathValue.includes(token)) {
      score += 6;
    }
    if (haystack.includes(token)) {
      score += 2;
      const occurrences = haystack.split(token).length - 1;
      score += Math.min(occurrences, 6) * 0.5;
    }
  }

  const queryPhrase = queryTokens.join(" ");
  if (queryPhrase.length >= 6 && haystack.includes(queryPhrase)) {
    score += 6;
  }
  if (compactQuery.length >= 6 && compactPath.includes(compactQuery)) {
    score += 10;
  }
  if (compactQuery.length >= 6 && compactBasename.includes(compactQuery)) {
    score += 14;
  }
  if (/(^|\/)(tests?|__tests__)\//.test(pathValue) || /\.test\.[a-z]+$/i.test(pathValue)) {
    score -= 8;
  }

  if (PINNED_PATHS.includes(chunk.path)) {
    score += 1.25;
  }

  if (endpointIntent) {
    let routeScore = 0;
    for (const [marker, weight] of ENDPOINT_ROUTE_MARKERS) {
      routeScore += Math.min(countSubstringOccurrences(haystack, marker), 2) * weight;
    }

    const literalRouteCount = countLiteralRouteStrings(chunk.text);
    const literalQueryHits = uniqueTokens.filter(
      (token) => (token.includes("/") || token.includes("__") || token.includes("."))
        && haystack.includes(token),
    ).length;

    score += Math.min(literalRouteCount, 8) * 3.5;
    score += literalQueryHits * 10;

    if (routeScore > 0) {
      score += routeScore;
      const strongPathMatch = uniqueTokens.filter((token) => pathValue.includes(token)).length;
      if (strongPathMatch >= 2) {
        score += 18 + strongPathMatch * 3;
      }
    }

    if (queryLower.includes("browser") && queryLower.includes("fallback") && compactPath.includes("aibrowserfallback")) {
      score += 18;
    }
    if (queryLower.includes("tauri") && (pathValue.endsWith("main.rs") || pathValue.includes("/tauri_handlers/ai.rs"))) {
      score += 12;
    }
    if (path.extname(pathValue) === ".md") {
      score -= 10;
    }
  }

  return score;
}

function rankChunksLexical(query: string, chunks: IndexedChunk[]): RankedChunk[] {
  const tokens = tokenize(query);
  return chunks
    .map((chunk, index) => ({ index, score: lexicalScore(query, tokens, chunk) }))
    .sort((left, right) => right.score - left.score);
}

function cosineSimilarity(left: number[], right: number[]): number {
  if (left.length === 0 || left.length !== right.length) {
    return 0;
  }

  let dot = 0;
  let leftNorm = 0;
  let rightNorm = 0;
  for (let index = 0; index < left.length; index += 1) {
    const leftValue = left[index] ?? 0;
    const rightValue = right[index] ?? 0;
    dot += leftValue * rightValue;
    leftNorm += leftValue * leftValue;
    rightNorm += rightValue * rightValue;
  }

  if (leftNorm === 0 || rightNorm === 0) {
    return 0;
  }

  return dot / (Math.sqrt(leftNorm) * Math.sqrt(rightNorm));
}

async function embedInputs(model: string, inputs: string[]): Promise<number[][]> {
  const payload = await fetchJson<{ embeddings?: number[][] }>(`${OLLAMA_BASE_URL}/embed`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      model,
      input: inputs,
      truncate: true,
      keep_alive: "5m",
    }),
  });

  return Array.isArray(payload.embeddings) ? payload.embeddings : [];
}

async function probeEmbeddingDimension(model: string): Promise<number | null> {
  try {
    const embeddings = await embedInputs(model, ["ping"]);
    const dimension = embeddings[0]?.length ?? 0;
    return dimension > 0 ? dimension : null;
  } catch {
    return null;
  }
}

function splitStringBatch(batch: string[]): [string[], string[]] {
  const midpoint = Math.max(1, Math.floor(batch.length / 2));
  return [batch.slice(0, midpoint), batch.slice(midpoint)];
}

async function embedChunkBatches(model: string, chunks: IndexedChunk[]): Promise<number[][]> {
  const embeddings: number[][] = [];
  const embeddingDim = await probeEmbeddingDimension(model);

  for (let index = 0; index < chunks.length; index += EMBED_BATCH_SIZE) {
    const queue: string[][] = [
      chunks
        .slice(index, index + EMBED_BATCH_SIZE)
        .map((chunk) => buildEmbeddingInput(chunk)),
    ];

    while (queue.length > 0) {
      const batch = queue.shift() ?? [];
      if (batch.length === 0) {
        continue;
      }

      try {
        const batchEmbeddings = await embedInputs(model, batch);
        if (batchEmbeddings.length !== batch.length) {
          throw new Error(
            `Ollama returned ${batchEmbeddings.length} embeddings for a batch of ${batch.length} chunks.`,
          );
        }
        embeddings.push(...batchEmbeddings);
      } catch (error) {
        if (batch.length > 1) {
          const [left, right] = splitStringBatch(batch);
          queue.unshift(right);
          queue.unshift(left);
          continue;
        }
        if (embeddingDim) {
          embeddings.push(Array.from({ length: embeddingDim }, () => 0));
          continue;
        }
        throw error;
      }
    }
  }

  return embeddings;
}

async function rerankSemantic(
  query: string,
  index: CachedIndex,
  lexicalCandidates: RankedChunk[],
): Promise<RankedChunk[] | null> {
  const embeddingModel = index.manifest.embeddingModel;
  if (!embeddingModel) {
    return null;
  }

  const candidates = lexicalCandidates
    .filter((entry) => entry.score > 0)
    .slice(0, MAX_SEMANTIC_CANDIDATES);

  if (candidates.length === 0) {
    return null;
  }

  try {
    if (index.embeddings.length !== index.chunks.length) {
      return null;
    }

    const embeddings = await embedInputs(embeddingModel, [query]);
    if (embeddings.length !== 1) {
      return null;
    }

    return candidates
      .map((entry) => ({
        index: entry.index,
        score: cosineSimilarity(embeddings[0] ?? [], index.embeddings[entry.index] ?? []),
      }))
      .sort((left, right) => right.score - left.score);
  } catch {
    return null;
  }
}

function mergeRankings(lexical: RankedChunk[], semantic: RankedChunk[] | null): RankedChunk[] {
  if (!semantic) {
    return lexical;
  }

  const semanticMap = new Map(semantic.map((entry) => [entry.index, entry.score]));
  return lexical
    .map((entry) => ({
      index: entry.index,
      score: entry.score + (semanticMap.get(entry.index) ?? 0) * 4,
    }))
    .sort((left, right) => right.score - left.score);
}

function shouldIncludeRepositorySummary(query: string): boolean {
  return !hasEndpointIntent(query, tokenize(query))
    && !/(function|class|file|filepath|\.tsx|\.ts|\.rs|main\.rs|aibrowserfallback)/i.test(query);
}

function buildSelection(
  chunks: IndexedChunk[],
  ranked: RankedChunk[],
  requestedContextChunks: number,
  includeSummaryPrompt: boolean,
): number[] {
  const selected = new Set<number>();
  const ordered: number[] = [];
  const totalSlots = Math.min(requestedContextChunks, 6) + (includeSummaryPrompt ? 1 : 0);

  const summaryIndex = includeSummaryPrompt
    ? chunks.findIndex((chunk) => chunk.path === SUMMARY_CHUNK_PATH)
    : -1;
  if (summaryIndex >= 0) {
    selected.add(summaryIndex);
    ordered.push(summaryIndex);
  }

  for (const candidate of ranked) {
    if (candidate.score <= 0) {
      continue;
    }
    if (!selected.has(candidate.index)) {
      selected.add(candidate.index);
      ordered.push(candidate.index);
    }
    if (ordered.length >= totalSlots) {
      break;
    }
  }

  return ordered;
}

function compactCitations(citations: AiCitation[]): AiCitation[] {
  const merged: AiCitation[] = [];

  for (const citation of citations) {
    const previous = merged[merged.length - 1];
    if (
      previous
      && previous.path === citation.path
      && citation.startLine <= previous.endLine + 25
    ) {
      previous.endLine = Math.max(previous.endLine, citation.endLine);
      previous.score = Math.max(previous.score, citation.score);
      continue;
    }

    merged.push({ ...citation });
  }

  return merged.slice(0, 4);
}

const AI_SYSTEM_PROMPT = [
  "You are the OpenBB repository assistant.",
  "Answer from the provided repository context first.",
  "Keep answers concise and concrete: use at most 6 bullets or 2 short paragraphs unless the user asks for more detail.",
  "Prefer file paths, route names, commands, and implementation facts from the retrieved context.",
  "When enumerating items, match the count you state to the list you provide.",
  "If the user asks about endpoints or commands, list every matching endpoint or command found in the provided context.",
  "For endpoints or commands, only quote literal path strings or command names that appear verbatim in the context. Never rename or infer new endpoint names.",
  "If the retrieved code shows a middleware or mount prefix together with nested pathname checks in the same chunk, report the public route as prefix plus nested pathname.",
  "Avoid generic software advice unless the repository context clearly supports it.",
  "If the context is insufficient, say so plainly and state what is missing.",
].join(" ");

function buildSystemPrompt(hasRepositoryContext: boolean, hasSupplementalContext: boolean): string {
  if (hasRepositoryContext && hasSupplementalContext) {
    return [
      AI_SYSTEM_PROMPT,
      "You also have supplemental OpenBB market data. Use it as the primary source for market, financial statement, and expected price-range questions.",
      "Do not claim that you cannot access market data when supplemental context is present.",
    ].join(" ");
  }

  if (hasSupplementalContext) {
    return [
      "You are the OpenBB market data assistant.",
      "Answer from the provided OpenBB market data first.",
      "Keep answers concise and concrete: use at most 6 bullets or 2 short paragraphs unless the user asks for more detail.",
      "If the user asks for an expected stock-price range, anchor on analyst target low, consensus, median, and high when available and label it as a scenario range, not a guarantee.",
      "If the provided market data is insufficient for a precise range, say what is missing.",
      "Do not say that you cannot access market data when the supplemental context is present.",
    ].join(" ");
  }

  return AI_SYSTEM_PROMPT;
}

function buildContextPrompt(
  index: CachedIndex | null,
  selectedIndexes: number[],
  includeSummaryPrompt: boolean,
  userQuery: string,
  supplementalContext?: string,
): string {
  const sections: string[] = [];
  if (supplementalContext?.trim()) {
    sections.push(`OpenBB supplemental market data:\n${supplementalContext.trim()}`);
  }

  if (!index) {
    return sections.join("\n\n");
  }

  if (hasEndpointIntent(userQuery, tokenize(userQuery))) {
    sections.push(
      "Task hint: this is an endpoint or command lookup. Use only literal route strings or command names from the retrieved code chunks.",
    );
  }
  if (includeSummaryPrompt) {
    sections.push(index.manifest.summaryPrompt);
  }

  for (const indexValue of selectedIndexes) {
    const chunk = index.chunks[indexValue];
    if (!chunk || chunk.path === SUMMARY_CHUNK_PATH) {
      continue;
    }

    sections.push([
      `### ${chunk.path}:${chunk.startLine}-${chunk.endLine}`,
      chunk.text,
    ].join("\n"));
  }

  return sections.join("\n\n");
}

async function callOllamaChat(candidateModels: string[], messages: Array<Record<string, string>>) {
  let lastError = "No Ollama chat model could answer the request.";
  const attemptedModels: string[] = [];

  for (const model of candidateModels) {
    attemptedModels.push(model);
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), CHAT_REQUEST_TIMEOUT_MS);

    try {
      const response = await fetch(`${OLLAMA_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: controller.signal,
        body: JSON.stringify({
          model,
          stream: false,
          keep_alive: CHAT_KEEP_ALIVE,
          messages,
        }),
      });

      if (!response.ok) {
        const body = await response.text().catch(() => "");
        throw new Error(body || `chat returned ${response.status}`);
      }

      const payload = await response.json() as {
        model: string;
        message?: { content?: string };
        total_duration?: number;
        load_duration?: number;
        prompt_eval_duration?: number;
        eval_duration?: number;
      };

      if (payload.message?.content?.trim()) {
        return {
          model: payload.model,
          content: payload.message.content.trim(),
          attemptedModels,
          loadMs: ollamaDurationToMs(payload.load_duration),
          promptEvalMs: ollamaDurationToMs(payload.prompt_eval_duration),
          evalMs: ollamaDurationToMs(payload.eval_duration),
          totalModelMs: ollamaDurationToMs(payload.total_duration),
        };
      }
    } catch (error) {
      const reason = error instanceof Error && error.name === "AbortError"
        ? `${model}: chat timed out after ${CHAT_REQUEST_TIMEOUT_MS}ms`
        : error instanceof Error
          ? `${model}: ${error.message}`
          : `${model}: chat failed`;
      lastError = reason;
    } finally {
      clearTimeout(timeout);
    }
  }

  throw new Error(lastError);
}

async function warmBrowserChatModel(candidateModels: string[]): Promise<string | null> {
  const warmupKey = candidateModels.join("|");
  const existing = warmModelPromises.get(warmupKey);
  if (existing) {
    return existing;
  }

  const pending = callOllamaChat(candidateModels.slice(0, 1), [
    { role: "system", content: "Reply with READY only." },
    { role: "user", content: "READY" },
  ])
    .then((response) => response.model ?? null)
    .catch(() => null)
    .finally(() => {
      warmModelPromises.delete(warmupKey);
    });

  warmModelPromises.set(warmupKey, pending);
  return pending;
}

async function buildBrowserIndex(repoRoot: string, discovery: OllamaDiscovery, force: boolean): Promise<AiIndexResult> {
  const context = await buildIndexContext(repoRoot, discovery.embeddingModel);
  const indexDir = browserIndexDirectory(context.repoHash);
  const existingManifest = await readManifest(indexDir);

  if (!force && existingManifest && existingManifest.revision === context.revision) {
    return {
      repoRoot: existingManifest.repoRoot,
      scannedFiles: existingManifest.scannedFiles,
      indexedFiles: existingManifest.indexedFiles,
      skippedFiles: existingManifest.skippedFiles,
      chunkCount: existingManifest.chunkCount,
      lastIndexedAt: existingManifest.lastIndexedAt,
      revision: existingManifest.revision,
    };
  }

  const files = await collectCandidateFiles(repoRoot);
  const chunks: IndexedChunk[] = [];
  let indexedFiles = 0;
  let skippedFiles = 0;

  for (const relativePath of files) {
    const absolutePath = path.join(repoRoot, relativePath);
    const text = await readTextFile(absolutePath);
    if (!text) {
      skippedFiles += 1;
      continue;
    }

    const nextChunks = chunkText(relativePath, text);
    if (nextChunks.length === 0) {
      skippedFiles += 1;
      continue;
    }

    indexedFiles += 1;
    chunks.push(...nextChunks);
  }

  const summaryPrompt = await buildSummaryPrompt(repoRoot);
  chunks.unshift({
    path: SUMMARY_CHUNK_PATH,
    startLine: 1,
    endLine: summaryPrompt.split("\n").length,
    sha1: sha1Hex(summaryPrompt),
    language: "md",
    text: summaryPrompt,
  });

  let embeddings: number[][] = [];
  let effectiveEmbeddingModel = discovery.embeddingModel;
  let mode: RetrievalMode = discovery.embeddingModel ? "semantic" : "lexical";

  if (effectiveEmbeddingModel) {
    try {
      embeddings = await embedChunkBatches(effectiveEmbeddingModel, chunks);
    } catch {
      embeddings = [];
      effectiveEmbeddingModel = null;
      mode = "lexical";
    }
  }

  const manifest: BrowserAiManifest = {
    repoRoot,
    repoHash: context.repoHash,
    headRevision: context.headRevision,
    configHash: context.configHash,
    revision: context.revision,
    scannedFiles: files.length,
    indexedFiles,
    skippedFiles,
    chunkCount: chunks.length,
    lastIndexedAt: new Date().toISOString(),
    embeddingModel: effectiveEmbeddingModel,
    embeddingDim: embeddings[0]?.length ?? null,
    mode,
    summaryPrompt,
  };

  await writeIndex(indexDir, manifest, chunks, embeddings);
  indexCache.set(context.repoHash, { manifest, chunks, embeddings });

  return {
    repoRoot,
    scannedFiles: manifest.scannedFiles,
    indexedFiles: manifest.indexedFiles,
    skippedFiles: manifest.skippedFiles,
    chunkCount: manifest.chunkCount,
    lastIndexedAt: manifest.lastIndexedAt,
    revision: manifest.revision,
  };
}

async function getBrowserAiStatus(workspaceRoot: string, defaultDir: string): Promise<AiStatus> {
  const repoRoot = resolveRepoRoot(workspaceRoot, defaultDir);
  const discovery = await discoverOllama();

  if (!repoRoot) {
    return {
      repoRoot: null,
      repoReady: false,
      ollamaReachable: discovery.reachable,
      chatModel: discovery.chatModel,
      chatCandidates: discovery.chatCandidates,
      embeddingModel: discovery.embeddingModel,
      availableModels: discovery.availableModels,
      indexReady: false,
      lastIndexedAt: null,
      chunkCount: 0,
      mode: discovery.mode,
    };
  }

  const context = await buildIndexContext(repoRoot, discovery.embeddingModel);
  const manifest = await readManifest(browserIndexDirectory(context.repoHash));
  const indexReady = isManifestReusable(manifest, context, repoRoot);
  const hasSemanticIndex = Boolean(
    indexReady
    && manifest?.embeddingModel
    && (manifest.embeddingDim ?? 0) > 0,
  );

  return {
    repoRoot,
    repoReady: true,
    ollamaReachable: discovery.reachable,
    chatModel: discovery.chatModel,
    chatCandidates: discovery.chatCandidates,
    embeddingModel: discovery.embeddingModel,
    availableModels: discovery.availableModels,
    indexReady,
    lastIndexedAt: manifest?.lastIndexedAt ?? null,
    chunkCount: manifest?.chunkCount ?? 0,
    mode: hasSemanticIndex ? "semantic" : "lexical",
  };
}

async function clearBrowserIndex(repoRoot: string, embeddingModel: string | null): Promise<void> {
  const context = await buildIndexContext(repoRoot, embeddingModel);
  const indexDir = browserIndexDirectory(context.repoHash);
  await fsp.rm(indexDir, { recursive: true, force: true });
  indexCache.delete(context.repoHash);
}

async function askBrowserAi(request: AiAskRequest): Promise<AiAskResponse> {
  const startedAt = Date.now();
  const discovery = await discoverOllama();
  const hasSupplementalContext = Boolean(request.supplementalContext?.trim());
  const supplementalOnly = Boolean(request.supplementalOnly && hasSupplementalContext);

  if (!discovery.chatCandidates.length) {
    throw new Error("No Ollama chat model is available. Install one with `ollama pull qwen2.5-coder:1.5b`.");
  }

  const latestUserMessage = [...request.messages]
    .reverse()
    .find((message) => message.role === "user")
    ?? request.messages[request.messages.length - 1];

  if (!latestUserMessage?.content?.trim()) {
    throw new Error("A question is required before asking the project AI.");
  }

  let index: CachedIndex | null = null;
  let semantic: RankedChunk[] | null = null;
  let selectedIndexes: number[] = [];
  let citations: AiCitation[] = [];
  let retrievalMode: RetrievalMode = "supplemental";
  let includeSummaryPrompt = false;

  if (!supplementalOnly) {
    const requestedRepoRoot = path.resolve(request.repoRoot);
    const repoRoot = fs.existsSync(requestedRepoRoot)
      ? requestedRepoRoot
      : process.cwd();
    index = await loadIndex(repoRoot, discovery.embeddingModel);
    if (!index || index.chunks.length === 0) {
      throw new Error("Build the AI index before asking a question.");
    }

    const requestedContextChunks = Math.min(
      Math.max(request.maxContextChunks ?? DEFAULT_CONTEXT_CHUNKS, 1),
      MAX_CONTEXT_CHUNKS,
    );
    includeSummaryPrompt = shouldIncludeRepositorySummary(latestUserMessage.content);

    const lexical = rankChunksLexical(latestUserMessage.content, index.chunks);
    semantic = await rerankSemantic(latestUserMessage.content, index, lexical);
    const ranked = mergeRankings(lexical, semantic);
    selectedIndexes = buildSelection(
      index.chunks,
      ranked,
      requestedContextChunks,
      includeSummaryPrompt,
    );
    citations = selectedIndexes
      .map((indexValue) => {
        const chunk = index?.chunks[indexValue];
        if (!chunk || chunk.path === SUMMARY_CHUNK_PATH) {
          return null;
        }
        const rankedEntry = ranked.find((entry) => entry.index === indexValue);
        return {
          path: chunk.path,
          startLine: chunk.startLine,
          endLine: chunk.endLine,
          score: Number((rankedEntry?.score ?? 0).toFixed(3)),
        } satisfies AiCitation;
      })
      .filter((citation): citation is AiCitation => Boolean(citation))
      .filter((citation) => citation.score > 0)
      .slice(0, Math.min(requestedContextChunks, 6));
    retrievalMode = semantic ? "semantic" : "lexical";
  } else if (!hasSupplementalContext) {
    throw new Error("Supplemental market data is required for market-data-only AI questions.");
  }

  const response = await callOllamaChat(discovery.chatCandidates, [
    {
      role: "system",
      content: buildSystemPrompt(Boolean(index), hasSupplementalContext),
    },
    {
      role: "system",
      content: buildContextPrompt(
        index,
        selectedIndexes,
        includeSummaryPrompt,
        latestUserMessage.content,
        request.supplementalContext,
      ),
    },
    ...request.messages.map((message) => ({
      role: message.role,
      content: message.content,
    })),
  ]);

  return {
    answer: response.content,
    citations: compactCitations(citations),
    usedModel: response.model,
    attemptedModels: response.attemptedModels,
    modelTotalMs: response.totalModelMs,
    loadMs: response.loadMs,
    promptEvalMs: response.promptEvalMs,
    evalMs: response.evalMs,
    timingMs: Date.now() - startedAt,
    retrievalMode,
  };
}

async function warmBrowserAiChatModel(defaultDir: string, workspaceRoot: string): Promise<{ ok: boolean; usedModel: string | null }> {
  resolveRepoRoot(workspaceRoot, defaultDir);
  const discovery = await discoverOllama();
  if (!discovery.chatCandidates.length) {
    return { ok: false, usedModel: null };
  }

  const usedModel = await warmBrowserChatModel(discovery.chatCandidates);
  return {
    ok: Boolean(usedModel),
    usedModel,
  };
}

export function createAiBrowserFallbackPlugin(workspaceRoot: string): Plugin {
  return {
    name: "openbb-ai-browser-fallback",
    configureServer(server) {
      server.middlewares.use("/__ai", async (req, res) => {
        try {
          const requestUrl = new URL(req.url ?? "/", "http://127.0.0.1:1470");

          if (req.method === "GET" && requestUrl.pathname === "/status") {
            const defaultDir = requestUrl.searchParams.get("defaultDir") ?? ".";
            const status = await getBrowserAiStatus(workspaceRoot, defaultDir);
            jsonResponse(res, 200, status);
            return;
          }

          if (req.method === "POST" && requestUrl.pathname === "/index") {
            const body = await readJsonBody(req) as { repoRoot?: string; force?: boolean };
            const repoRoot = resolveRequestedRepoRoot(workspaceRoot, body.repoRoot);
            if (!repoRoot) {
              jsonResponse(res, 400, { error: "A Git repository is required before indexing." });
              return;
            }

            const discovery = await discoverOllama();
            const result = await buildBrowserIndex(repoRoot, discovery, body.force === true);
            jsonResponse(res, 200, result);
            return;
          }

          if (req.method === "POST" && requestUrl.pathname === "/clear") {
            const body = await readJsonBody(req) as { repoRoot?: string };
            const repoRoot = resolveRequestedRepoRoot(workspaceRoot, body.repoRoot);
            if (!repoRoot) {
              jsonResponse(res, 400, { error: "A Git repository is required before clearing the index." });
              return;
            }

            const discovery = await discoverOllama();
            await clearBrowserIndex(repoRoot, discovery.embeddingModel);
            jsonResponse(res, 200, { ok: true });
            return;
          }

          if (req.method === "POST" && requestUrl.pathname === "/warmup") {
            const body = await readJsonBody(req) as { defaultDir?: string };
            const response = await warmBrowserAiChatModel(body.defaultDir ?? ".", workspaceRoot);
            jsonResponse(res, 200, response);
            return;
          }

          if (req.method === "POST" && requestUrl.pathname === "/ask") {
            const body = await readJsonBody(req) as { request?: AiAskRequest };
            if (!body.request) {
              jsonResponse(res, 400, { error: "Missing AI request body." });
              return;
            }

            const repoRoot = resolveRequestedRepoRoot(workspaceRoot, body.request.repoRoot);
            if (!repoRoot) {
              jsonResponse(res, 400, { error: "A Git repository is required before asking the project AI." });
              return;
            }

            body.request.repoRoot = repoRoot;
            const response = await askBrowserAi(body.request);
            jsonResponse(res, 200, response);
            return;
          }

          jsonResponse(res, 404, { error: "Not found" });
        } catch (error) {
          jsonResponse(res, 500, {
            error: error instanceof Error ? error.message : "AI browser fallback failed.",
          });
        }
      });
    },
  };
}

export const __aiBrowserFallbackInternals = {
  chatModelPriority,
  sortChatCandidates,
  compactCitations,
  ollamaDurationToMs,
  isEmbeddingOnlyModelName,
  rankChunksLexical,
  shouldIncludeRepositorySummary,
  shouldSkipRelativePath,
  chunkText,
};
