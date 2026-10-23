import js from "@eslint/js";
import tseslint from "typescript-eslint";

export default [
  {
    ignores: [
      "dist/",
      "target/",
      "node_modules/",
      "*.js",
      "*.cjs",
      "*.mjs",
      "*.d.ts",
      "src-tauri/",
      ".vscode/",
      ".tanstack/"
    ]
  },
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ["**/*.ts", "**/*.tsx", "**/*.js", "**/*.jsx"],
    plugins: { "@typescript-eslint": tseslint.plugin },
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        project: "./tsconfig.json",
      },
      globals: {
        window: "readonly",
        document: "readonly",
        console: "readonly",
        setTimeout: "readonly",
        clearTimeout: "readonly",
        setInterval: "readonly",
        clearInterval: "readonly",
        Event: "readonly",
        CustomEvent: "readonly",
        Node: "readonly",
        HTMLElement: "readonly",
        HTMLInputElement: "readonly",
        ResizeObserver: "readonly",
        MutationObserver: "readonly",
        AbortController: "readonly",
        URL: "readonly",
        Headers: "readonly",
        Response: "readonly",
        CSS: "readonly",
        self: "readonly",
        navigator: "readonly",
        sessionStorage: "readonly",
        requestAnimationFrame: "readonly",
        cancelAnimationFrame: "readonly",
        NodeFilter: "readonly",
        DocumentFragment: "readonly",
        IntersectionObserver: "readonly",
      }
    },
  },
  {
    files: ["src/components/BackendLogsPage.tsx", "src/routes/backends.tsx"],
    rules: {
      "no-control-regex": "off",
    },
  },
  {
    files: ["**/*.test.ts", "**/*.test.tsx", "**/*.spec.ts", "**/*.spec.tsx", "**/tests/**/*.ts", "**/tests/**/*.tsx"],
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
    },
  },
];