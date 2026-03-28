/// <reference types="vitest/globals" />
// @vitest-environment node

import os from "node:os";
import path from "node:path";
import { describe, expect, test, vi } from "vitest";
import { __aiBrowserFallbackInternals } from "../../../dev/aiBrowserFallback";

describe("aiBrowserFallback internals", () => {
  test("resolves the default settings path under the OpenBB user settings directory", () => {
    const homeDirSpy = vi.spyOn(os, "homedir").mockReturnValue("C:\\Users\\tester");

    const settingsPath = __aiBrowserFallbackInternals.defaultSettingsPath();

    expect(settingsPath).toBe(
      path.join("C:\\Users\\tester", ".openbb_platform", "user_settings.json"),
    );

    homeDirSpy.mockRestore();
  });

  test("builds the gateway command for the local Rust sidecar", () => {
    const homeDirSpy = vi.spyOn(os, "homedir").mockReturnValue("C:\\Users\\tester");

    const command = __aiBrowserFallbackInternals.gatewayCommand("C:\\repo\\OpenBB-develop");

    expect(command.command).toBe("cargo");
    expect(command.args).toEqual([
      "run",
      "--manifest-path",
      path.join("C:\\repo\\OpenBB-develop", "desktop", "src-tauri", "Cargo.toml"),
      "--bin",
      "openbb-ai-gateway",
      "--",
      "--host",
      "127.0.0.1",
      "--port",
      "0",
      "--settings",
      path.join("C:\\Users\\tester", ".openbb_platform", "user_settings.json"),
    ]);

    homeDirSpy.mockRestore();
  });
});
