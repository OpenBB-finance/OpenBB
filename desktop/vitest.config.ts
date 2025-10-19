import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'], // Path to your setup file
    coverage: {
      reporter: ['text', 'html'],
    },
  },
  resolve: {
    alias: {
      '~': '/src', // Map '~' to the 'src' directory
    },
  },
});
