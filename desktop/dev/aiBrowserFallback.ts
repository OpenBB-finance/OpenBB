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
const DEFAULT_CONTEXT_CHUNKS = 10;
const MAX_CONTEXT_CHUNKS = 16;
const MAX_SEMANTIC_CANDIDATES = 12;
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

type RetrievalMode = "semantic" | "lexical";
type AiChatRole = "user" | "assistant";

interface AiStatus {
  repoRoot: string | null;
  repoReady: boolean;
  ollamaReachable: boolean;
  chatModel: string | null;
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
}

interface AiAskResponse {
  answer: string;
  citations: AiCitation[];
  usedModel: string;
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

function chatModelPriority(model: OllamaModel): number {
  const normalized = model.name.toLowerCase();
  if (normalized.includes("coder")) {
    return 0;
  }
  if (normalized.includes("instruct") || normalized.includes("chat")) {
    return 1;
  }
  return 2;
}

function sortChatCandidates(models: OllamaModel[]): OllamaModel[] {
  return [...models].sort((left, right) => {
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
  });
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
  try {
    const payload = await fetchJson<{ models?: OllamaModel[] }>(`${OLLAMA_BASE_URL}/tags`);
    const models = Array.isArray(payload.models) ? payload.models : [];
    const availableModels = models.map((model) => model.name);
    const chatCandidates = sortChatCandidates(models).map((model) => model.name);
    const embeddingModel = await chooseEmbeddingModel(models);

    return {
      reachable: true,
      availableModels,
      chatModel: chatCandidates[0] ?? null,
      chatCandidates,
      embeddingModel,
      mode: embeddingModel ? "semantic" : "lexical",
    };
  } catch {
    return {
      reachable: false,
      availableModels: [],
      chatModel: null,
      chatCandidates: [],
      embeddingModel: null,
      mode: "lexical",
    };
  }
}

async function gitHeadRevision(repoRoot: string): Promise<string> {
  try {
    const { stdout } = await execFileAsync("git", ["-C", repoRoot, "rev-parse", "HEAD"], {
      windowsHide: true,
      timeout: 10000,
    });
    const revision = stdout.trim();
    return revision || "nogit";
  } catch {
    return "nogit";
  }
}

async function buildIndexContext(repoRoot: string, embeddingModel: string | null) {
  const repoHash = sha1Hex(repoRoot);
  const headRevision = await gitHeadRevision(repoRoot);
  const configHash = sha1Hex([
    `chunk_lines=${CHUNK_LINES}`,
    `chunk_overlap=${CHUNK_OVERLAP}`,
    `max_file_size=${MAX_FILE_SIZE_BYTES}`,
    `extensions=${Array.from(ALLOWED_EXTENSIONS).join(",")}`,
    `excluded_dirs=${Array.from(EXCLUDED_DIRS).join(",")}`,
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

function shouldIncludeFile(relativePath: string, stat: fs.Stats): boolean {
  if (!stat.isFile()) {
    return false;
  }
  if (stat.size > MAX_FILE_SIZE_BYTES) {
    return false;
  }

  const normalized = relativePath.replace(/\\/g, "/");
  const basename = path.basename(normalized);
  if (LOCKFILES.has(basename) || basename.endsWith(".min.js")) {
    return false;
  }

  const segments = normalized.split("/");
  if (segments.some((segment) => EXCLUDED_DIRS.has(segment))) {
    return false;
  }

  return ALLOWED_EXTENSIONS.has(path.extname(normalized).toLowerCase());
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

function chunkText(relativePath: string, text: string): IndexedChunk[] {
  const normalizedText = text.replace(/\r\n/g, "\n");
  const lines = normalizedText.split("\n");
  const chunks: IndexedChunk[] = [];
  const step = Math.max(1, CHUNK_LINES - CHUNK_OVERLAP);

  for (let start = 0; start < lines.length; start += step) {
    const end = Math.min(lines.length, start + CHUNK_LINES);
    const chunkLines = lines.slice(start, end);
    const chunkBody = chunkLines.join("\n").trim();

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

async function writeIndex(indexDir: string, manifest: BrowserAiManifest, chunks: IndexedChunk[]): Promise<void> {
  await fsp.mkdir(indexDir, { recursive: true });
  await fsp.writeFile(manifestPath(indexDir), JSON.stringify(manifest, null, 2), "utf8");
  const serializedChunks = chunks.map((chunk) => JSON.stringify(chunk)).join("\n");
  await fsp.writeFile(chunksPath(indexDir), serializedChunks, "utf8");
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
  const index = { manifest, chunks };
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

function lexicalScore(queryTokens: string[], chunk: IndexedChunk): number {
  if (queryTokens.length === 0) {
    return 0;
  }

  const haystack = `${chunk.path}\n${chunk.text}`.toLowerCase();
  const pathValue = chunk.path.toLowerCase();
  const basename = path.basename(pathValue).toLowerCase();
  const compactPath = pathValue.replace(/[^a-z0-9]+/g, "");
  const compactBasename = basename.replace(/[^a-z0-9]+/g, "");
  const compactQuery = queryTokens.join("");
  let score = 0;

  for (const token of new Set(queryTokens)) {
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

  return score;
}

function rankChunksLexical(query: string, chunks: IndexedChunk[]): RankedChunk[] {
  const tokens = tokenize(query);
  return chunks
    .map((chunk, index) => ({ index, score: lexicalScore(tokens, chunk) }))
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

async function rerankSemantic(
  query: string,
  chunks: IndexedChunk[],
  lexicalCandidates: RankedChunk[],
  embeddingModel: string | null,
): Promise<RankedChunk[] | null> {
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
    const candidateTexts = candidates.map(({ index }) => {
      const chunk = chunks[index];
      return `${chunk.path}:${chunk.startLine}-${chunk.endLine}\n${chunk.text}`;
    });

    const embeddings = await embedInputs(embeddingModel, [query, ...candidateTexts]);
    if (embeddings.length !== candidateTexts.length + 1) {
      return null;
    }

    const [queryEmbedding, ...chunkEmbeddings] = embeddings;
    return chunkEmbeddings
      .map((embedding, index) => ({
        index: candidates[index]?.index ?? 0,
        score: cosineSimilarity(queryEmbedding ?? [], embedding ?? []),
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

function buildSelection(
  chunks: IndexedChunk[],
  ranked: RankedChunk[],
  requestedContextChunks: number,
): number[] {
  const selected = new Set<number>();
  const ordered: number[] = [];
  const totalSlots = Math.min(requestedContextChunks, 6) + 1;

  const summaryIndex = chunks.findIndex((chunk) => chunk.path === SUMMARY_CHUNK_PATH);
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

function buildContextPrompt(index: CachedIndex, selectedIndexes: number[]): string {
  const sections: string[] = [];
  sections.push(index.manifest.summaryPrompt);

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

  for (const model of candidateModels) {
    try {
      const response = await fetchJson<{ model: string; message?: { content?: string } }>(`${OLLAMA_BASE_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model,
          stream: false,
          keep_alive: "5m",
          messages,
        }),
      });

      if (response.message?.content?.trim()) {
        return {
          model: response.model,
          content: response.message.content.trim(),
        };
      }
    } catch (error) {
      lastError = error instanceof Error ? `${model}: ${error.message}` : `${model}: chat failed`;
    }
  }

  throw new Error(lastError);
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
    embeddingModel: discovery.embeddingModel,
    mode: discovery.embeddingModel ? "semantic" : "lexical",
    summaryPrompt,
  };

  await writeIndex(indexDir, manifest, chunks);
  indexCache.set(context.repoHash, { manifest, chunks });

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

  return {
    repoRoot,
    repoReady: true,
    ollamaReachable: discovery.reachable,
    chatModel: discovery.chatModel,
    embeddingModel: discovery.embeddingModel,
    availableModels: discovery.availableModels,
    indexReady,
    lastIndexedAt: manifest?.lastIndexedAt ?? null,
    chunkCount: manifest?.chunkCount ?? 0,
    mode: discovery.mode,
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
  const requestedRepoRoot = path.resolve(request.repoRoot);
  const repoRoot = fs.existsSync(requestedRepoRoot)
    ? requestedRepoRoot
    : process.cwd();
  const discovery = await discoverOllama();

  if (!discovery.chatCandidates.length) {
    throw new Error("No Ollama chat model is available. Install one with `ollama pull qwen2.5-coder:1.5b`.");
  }

  const index = await loadIndex(repoRoot, discovery.embeddingModel);
  if (!index || index.chunks.length === 0) {
    throw new Error("Build the AI index before asking a question.");
  }

  const latestUserMessage = [...request.messages]
    .reverse()
    .find((message) => message.role === "user")
    ?? request.messages[request.messages.length - 1];

  if (!latestUserMessage?.content?.trim()) {
    throw new Error("A question is required before asking the project AI.");
  }

  const requestedContextChunks = Math.min(
    Math.max(request.maxContextChunks ?? DEFAULT_CONTEXT_CHUNKS, 1),
    MAX_CONTEXT_CHUNKS,
  );

  const lexical = rankChunksLexical(latestUserMessage.content, index.chunks);
  const semantic = await rerankSemantic(
    latestUserMessage.content,
    index.chunks,
    lexical,
    discovery.embeddingModel,
  );
  const ranked = mergeRankings(lexical, semantic);
  const selectedIndexes = buildSelection(index.chunks, ranked, requestedContextChunks);
  const citations = selectedIndexes
    .map((indexValue) => {
      const chunk = index.chunks[indexValue];
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

  const contextPrompt = buildContextPrompt(index, selectedIndexes);
  const systemPrompt = "You are a read-only project guide for this repository. Explain the codebase precisely, never invent files or behaviors, say when information is missing, and cite file paths with line ranges in every substantive answer.";
  const response = await callOllamaChat(discovery.chatCandidates, [
    { role: "system", content: systemPrompt },
    { role: "system", content: contextPrompt },
    ...request.messages.map((message) => ({
      role: message.role,
      content: message.content,
    })),
  ]);

  return {
    answer: response.content,
    citations,
    usedModel: response.model,
    timingMs: Date.now() - startedAt,
    retrievalMode: semantic ? "semantic" : "lexical",
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
