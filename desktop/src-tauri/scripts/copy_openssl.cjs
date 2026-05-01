#!/usr/bin/env node
// Cross-platform dispatcher that copies OpenSSL runtime binaries from the
// build container (vcpkg on Windows, Homebrew on macOS) into the locations
// the Tauri bundler expects. Linux uses system libssl3 at runtime and is a
// no-op here. Invoked via the `openssl:copy` npm script and the Tauri
// beforeDevCommand / beforeBuildCommand hooks.

const { spawnSync } = require("node:child_process");
const path = require("node:path");
const process = require("node:process");

const scriptsDir = __dirname;
const platform = process.platform;

function run(cmd, args) {
  const result = spawnSync(cmd, args, { stdio: "inherit" });
  if (result.error) {
    console.error(`[copy_openssl] failed to launch ${cmd}: ${result.error.message}`);
    process.exit(1);
  }
  if (typeof result.status === "number" && result.status !== 0) {
    process.exit(result.status);
  }
}

if (platform === "win32") {
  const script = path.join(scriptsDir, "copy_openssl_win.ps1");
  run("powershell", [
    "-NoProfile",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    script,
  ]);
} else if (platform === "darwin") {
  const script = path.join(scriptsDir, "copy_openssl_macos.sh");
  run("sh", [script]);
} else {
  console.log(
    `[copy_openssl] platform '${platform}' does not require bundled OpenSSL; skipping.`,
  );
}
