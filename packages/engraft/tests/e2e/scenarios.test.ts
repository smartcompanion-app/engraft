import { cpSync, existsSync, mkdtempSync, readdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { afterEach, describe, expect, it } from "vitest";

import { compareTree } from "./comparators.js";
import { describeRun, runEngraft } from "./harness.js";

/**
 * Fixture-driven end-to-end suite.
 *
 * Each directory under `fixtures/` is one scenario:
 *
 *   input/          the project tree before the apply
 *   template.yaml   what the repo author declares as customizable
 *   values.yaml     what the consumer chose
 *   expected/       the project tree the apply must produce
 *   expect_failure  optional marker: the CLI must exit non-zero, and
 *                   `expected/` describes the untouched input tree
 *
 * Adding a scenario means adding a directory — no code changes here. New
 * actions must arrive with a fixture exercising them.
 */

const here = path.dirname(fileURLToPath(import.meta.url));
const FIXTURES_DIR = path.join(here, "fixtures");

const scenarios = readdirSync(FIXTURES_DIR, { withFileTypes: true })
  .filter(
    (entry) =>
      entry.isDirectory() && existsSync(path.join(FIXTURES_DIR, entry.name, "template.yaml")),
  )
  .map((entry) => entry.name)
  .toSorted();

const tempDirs: string[] = [];

afterEach(() => {
  while (tempDirs.length > 0) {
    rmSync(tempDirs.pop()!, { recursive: true, force: true });
  }
});

const stageInput = (inputDir: string): string => {
  const root = mkdtempSync(path.join(tmpdir(), "engraft-e2e-"));
  tempDirs.push(root);
  const work = path.join(root, "work");
  cpSync(inputDir, work, { recursive: true });
  return work;
};

describe("fixture scenarios", () => {
  it("discovers at least one fixture", () => {
    expect(scenarios.length).toBeGreaterThan(0);
  });

  it.each(scenarios)("%s", (scenario) => {
    const fixture = path.join(FIXTURES_DIR, scenario);
    const expectFailure = existsSync(path.join(fixture, "expect_failure"));

    const work = stageInput(path.join(fixture, "input"));

    const result = runEngraft(
      [
        "apply",
        "--template",
        path.join(fixture, "template.yaml"),
        "--values",
        path.join(fixture, "values.yaml"),
      ],
      work,
    );

    // A fixture declares its expected outcome; asserting on the boolean keeps
    // one assertion for both shapes instead of branching around `expect`.
    expect(
      result.status === 0,
      `apply should have ${expectFailure ? "failed" : "succeeded"}\n${describeRun(result)}`,
    ).toBe(!expectFailure);

    compareTree(path.join(fixture, "expected"), work);

    // A run leaves no trace of itself behind, successful or not.
    expect(existsSync(path.join(work, ".engraft")), "the staging directory was left behind").toBe(
      false,
    );
  });
});
