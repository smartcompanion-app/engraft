import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    projects: [
      {
        test: {
          name: "unit",
          include: ["tests/unit/**/*.test.ts"],
          environment: "node",
        },
      },
      {
        // These drive the built bundle through a real subprocess, so they are
        // slower than the unit project and need `npm run build` to have run.
        test: {
          name: "e2e",
          include: ["tests/e2e/**/*.test.ts"],
          environment: "node",
          globalSetup: ["./tests/e2e/global-setup.ts"],
          testTimeout: 30_000,
        },
      },
    ],
  },
});
