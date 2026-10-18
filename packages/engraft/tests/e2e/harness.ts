import { spawnSync, type SpawnSyncReturns } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));

/** Repository root — `tests/e2e/` sits two levels below it. */
export const REPO_ROOT = path.resolve(here, "..", "..");

/** The bundle the e2e suite exercises. Built by `npm run build`. */
export const CLI_PATH = path.join(REPO_ROOT, "dist", "cli.js");

export type RunResult = SpawnSyncReturns<string>;

/**
 * Invoke the built CLI as a subprocess, the way a consumer would.
 *
 * The e2e suite deliberately treats engraft as an opaque binary: no module
 * imports, no internal state. Anything it can assert, a user could observe.
 */
export const runEngraft = (args: string[], cwd: string): RunResult =>
  spawnSync(process.execPath, [CLI_PATH, ...args], {
    cwd,
    encoding: "utf8",
  });

/** Format a failed run for an assertion message. */
export const describeRun = (result: RunResult): string =>
  `exit=${result.status}\nstdout=${JSON.stringify(result.stdout)}\nstderr=${JSON.stringify(result.stderr)}`;
