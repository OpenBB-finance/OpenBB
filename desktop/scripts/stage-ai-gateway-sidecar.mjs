import fs from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const repoRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const isWindows = process.platform === "win32";
const executableName = isWindows ? "openbb-ai-gateway.exe" : "openbb-ai-gateway";
const sourcePath = path.join(repoRoot, "target", "release", executableName);
const targetDir = path.join(repoRoot, "src-tauri", "resources", "ai");
const targetPath = path.join(targetDir, executableName);

if (!fs.existsSync(sourcePath)) {
  throw new Error(`AI gateway sidecar binary was not found at ${sourcePath}`);
}

fs.mkdirSync(targetDir, { recursive: true });
fs.copyFileSync(sourcePath, targetPath);
console.log(`Staged ${executableName} -> ${targetPath}`);
