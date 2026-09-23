import {
  chmodSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { spawnSync } from "node:child_process";
import { tmpdir } from "node:os";
import path from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import { CLI_PATH, REPO_ROOT, describeRun, runEngraft } from "./harness.js";

const TEMPLATE = `variables:
  name:
    description: name
    default: original
customizations:
  - action: json_replace
    file: config.json
    replace:
      - selector: "$.name"
        variable: name
`;

const tempDirs: string[] = [];

afterEach(() => {
  while (tempDirs.length > 0) {
    rmSync(tempDirs.pop()!, { recursive: true, force: true });
  }
});

/** A throwaway project with a single `config.json` to customize. */
const scaffold = (prefix: string) => {
  const root = mkdtempSync(path.join(tmpdir(), prefix));
  tempDirs.push(root);
  const projectDir = path.join(root, "project");
  mkdirSync(projectDir, { recursive: true });
  writeFileSync(
    path.join(projectDir, "config.json"),
    `${JSON.stringify({ name: "original" }, null, 2)}\n`,
  );
  writeFileSync(path.join(root, "template.yml"), TEMPLATE);
  return { root, projectDir };
};

const readName = (projectDir: string): unknown =>
  (
    JSON.parse(readFileSync(path.join(projectDir, "config.json"), "utf8")) as {
      name: unknown;
    }
  ).name;

describe("built CLI", () => {
  it("--version prints the package version", () => {
    const pkg = JSON.parse(readFileSync(path.join(REPO_ROOT, "package.json"), "utf8")) as {
      version: string;
    };

    const result = runEngraft(["--version"], REPO_ROOT);

    expect(result.status, describeRun(result)).toBe(0);
    expect(result.stdout.trim()).toBe(pkg.version);
  });

  it("reports a missing template file and exits non-zero", () => {
    const { root, projectDir } = scaffold("engraft-cli-missing-");
    writeFileSync(path.join(root, "values.yml"), "name: Whatever\n");

    const result = runEngraft(
      [
        "apply",
        "--template",
        path.join(root, "does-not-exist.yml"),
        "--values",
        path.join(root, "values.yml"),
      ],
      projectDir,
    );

    expect(result.status).not.toBe(0);
    expect(result.stderr).toContain("Error:");
    expect(readName(projectDir)).toBe("original");
  });

  it("applies a template end to end", () => {
    const { root, projectDir } = scaffold("engraft-cli-");
    const valuesDir = path.join(root, "values");
    mkdirSync(valuesDir, { recursive: true });
    writeFileSync(path.join(valuesDir, "values.yml"), "name: CliApp\n");

    const result = runEngraft(
      [
        "apply",
        "--template",
        path.join(root, "template.yml"),
        "--values",
        path.join(valuesDir, "values.yml"),
      ],
      projectDir,
    );

    expect(result.status, describeRun(result)).toBe(0);
    expect(readName(projectDir)).toBe("CliApp");
  });

  // Regression test for the silent no-op bug: when invoked via an npm bin
  // symlink, isMain() must still recognise the entry point. argv[1] points at
  // the unresolved symlink, while import.meta.url resolves to the real file —
  // both sides need to be normalised before comparing.
  it("applies a template when invoked through a symlink (npm bin shape)", () => {
    const { root, projectDir } = scaffold("engraft-cli-symlink-");
    writeFileSync(path.join(root, "values.yml"), "name: ViaSymlink\n");

    const binDir = path.join(root, "bin");
    mkdirSync(binDir, { recursive: true });
    chmodSync(CLI_PATH, 0o755);
    const symlinkPath = path.join(binDir, "engraft");
    symlinkSync(CLI_PATH, symlinkPath);

    const result = spawnSync(
      process.execPath,
      [
        symlinkPath,
        "apply",
        "--template",
        path.join(root, "template.yml"),
        "--values",
        path.join(root, "values.yml"),
      ],
      { cwd: projectDir, encoding: "utf8" },
    );

    expect(result.status, result.stderr).toBe(0);
    expect(result.stdout).toContain("Done.");
    expect(readName(projectDir)).toBe("ViaSymlink");
  });
});
