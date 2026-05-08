import { spawnSync } from "node:child_process";
import {
  chmodSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { describe, it, expect } from "vitest";

const here = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(here, "..");
const cliPath = path.join(projectRoot, "dist", "cli.js");

const runCli = (args: string[], cwd?: string) =>
  spawnSync("node", [cliPath, ...args], {
    cwd: cwd ?? projectRoot,
    encoding: "utf8",
  });

describe("CLI (built)", () => {
  it("skips cleanly when dist/cli.js is missing", () => {
    if (!existsSync(cliPath)) {
      // Signal rather than fail — the user hasn't built yet.
      expect.soft(false, "Skipping: run `npm run build` first").toBe(true);
      return;
    }
  });

  it("--version prints the package version", () => {
    if (!existsSync(cliPath)) return;
    const pkg = JSON.parse(
      readFileSync(path.join(projectRoot, "package.json"), "utf8"),
    ) as { version: string };
    const result = runCli(["--version"]);
    expect(result.status).toBe(0);
    expect(result.stdout.trim()).toBe(pkg.version);
  });

  it("apply applies the template end-to-end", () => {
    if (!existsSync(cliPath)) return;

    const root = mkdtempSync(path.join(tmpdir(), "engraft-cli-"));
    const projectDir = path.join(root, "project");
    mkdirSync(projectDir, { recursive: true });
    writeFileSync(
      path.join(projectDir, "config.json"),
      JSON.stringify({ name: "original" }, null, 2) + "\n",
    );
    writeFileSync(
      path.join(root, "template.yml"),
      `variables:
  name:
    description: name
    default: original
customizations:
  - action: json_replace
    file: config.json
    replace:
      - selector: "$.name"
        variable: name
`,
    );
    const valuesDir = path.join(root, "values");
    mkdirSync(valuesDir, { recursive: true });
    writeFileSync(path.join(valuesDir, "values.yml"), "name: CliApp\n");

    const result = runCli(
      [
        "apply",
        "--template",
        path.join(root, "template.yml"),
        "--values",
        path.join(valuesDir, "values.yml"),
      ],
      projectDir,
    );
    expect(result.status).toBe(0);
    const data = JSON.parse(
      readFileSync(path.join(projectDir, "config.json"), "utf8"),
    );
    expect(data.name).toBe("CliApp");
  });

  // Regression test for the silent no-op bug: when invoked via an npm bin
  // symlink, isMain() must still recognise the entry point. argv[1] points at
  // the unresolved symlink, while import.meta.url resolves to the real file —
  // both sides need to be normalised before comparing.
  it("apply works when invoked through a symlink (npm bin shape)", () => {
    if (!existsSync(cliPath)) return;

    const root = mkdtempSync(path.join(tmpdir(), "engraft-cli-symlink-"));
    const projectDir = path.join(root, "project");
    const binDir = path.join(root, "bin");
    mkdirSync(projectDir, { recursive: true });
    mkdirSync(binDir, { recursive: true });

    writeFileSync(
      path.join(projectDir, "config.json"),
      JSON.stringify({ name: "original" }, null, 2) + "\n",
    );
    writeFileSync(
      path.join(root, "template.yml"),
      `variables:
  name:
    description: name
    default: original
customizations:
  - action: json_replace
    file: config.json
    replace:
      - selector: "$.name"
        variable: name
`,
    );
    writeFileSync(path.join(root, "values.yml"), "name: ViaSymlink\n");

    chmodSync(cliPath, 0o755);
    const symlinkPath = path.join(binDir, "engraft");
    symlinkSync(cliPath, symlinkPath);

    const result = spawnSync(
      "node",
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

    expect(result.status).toBe(0);
    expect(result.stdout).toContain("Done.");
    const data = JSON.parse(
      readFileSync(path.join(projectDir, "config.json"), "utf8"),
    );
    expect(data.name).toBe("ViaSymlink");
  });
});
