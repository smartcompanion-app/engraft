import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, it, expect } from "vitest";

import { FileReplace } from "../../src/actions/fileReplace.js";

describe("FileReplace", () => {
  it("copies source file over target file", async () => {
    const root = mkdtempSync(path.join(tmpdir(), "engraft-fr-"));
    const workDir = path.join(root, "work");
    const valuesDir = path.join(root, "values");
    writeFileSync(
      path.join(root, "work-target"),
      "target-content",
    );
    // setup dirs
    const { mkdirSync } = await import("node:fs");
    mkdirSync(workDir, { recursive: true });
    mkdirSync(valuesDir, { recursive: true });
    writeFileSync(path.join(workDir, "logo.png"), "OLD");
    writeFileSync(path.join(valuesDir, "new-logo.png"), "NEW");

    const action = new FileReplace({ file: "logo.png", variable: "logo" });
    await action.apply(
      { logo: "new-logo.png" },
      workDir,
      valuesDir,
    );
    expect(readFileSync(path.join(workDir, "logo.png"), "utf8")).toBe("NEW");
  });

  it("errors when source file does not exist", async () => {
    const root = mkdtempSync(path.join(tmpdir(), "engraft-fr-"));
    const workDir = path.join(root, "work");
    const valuesDir = path.join(root, "values");
    const { mkdirSync } = await import("node:fs");
    mkdirSync(workDir, { recursive: true });
    mkdirSync(valuesDir, { recursive: true });
    writeFileSync(path.join(workDir, "logo.png"), "OLD");

    const action = new FileReplace({ file: "logo.png", variable: "logo" });
    await expect(
      action.apply({ logo: "missing.png" }, workDir, valuesDir),
    ).rejects.toThrow(/Source file does not exist/);
  });

  it("is a noop when the variable is null", async () => {
    const root = mkdtempSync(path.join(tmpdir(), "engraft-fr-"));
    const workDir = path.join(root, "work");
    const valuesDir = path.join(root, "values");
    const { mkdirSync } = await import("node:fs");
    mkdirSync(workDir, { recursive: true });
    mkdirSync(valuesDir, { recursive: true });
    writeFileSync(path.join(workDir, "logo.png"), "ORIGINAL");

    const action = new FileReplace({ file: "logo.png", variable: "logo" });
    await action.apply({ logo: null }, workDir, valuesDir);
    expect(readFileSync(path.join(workDir, "logo.png"), "utf8")).toBe(
      "ORIGINAL",
    );
  });

  it("returns the target file", () => {
    const action = new FileReplace({ file: "assets/logo.png", variable: "l" });
    expect(action.targetFiles()).toEqual(["assets/logo.png"]);
  });
});
