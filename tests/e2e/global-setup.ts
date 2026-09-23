import { existsSync } from "node:fs";

import { CLI_PATH } from "./harness.js";

/**
 * The e2e project runs the published artefact, not the TypeScript sources, so
 * `dist/cli.js` has to exist before any scenario runs. `npm test` and
 * `npm run test:e2e` build first; this guard turns a direct `vitest run` into a
 * clear instruction instead of a pile of ENOENT failures.
 */
export default function setup(): void {
  if (!existsSync(CLI_PATH)) {
    throw new Error(
      `engraft bundle not found at ${CLI_PATH}.\n` +
        "Run `npm run build` first, or use `npm run test:e2e`, which builds for you.",
    );
  }
}
