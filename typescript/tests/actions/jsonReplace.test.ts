import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, it, expect } from "vitest";

import { JsonReplace } from "../../src/actions/jsonReplace.js";

const makeWorkdir = (files: Record<string, string>): string => {
  const dir = mkdtempSync(path.join(tmpdir(), "engraft-json-"));
  for (const [rel, content] of Object.entries(files)) {
    writeFileSync(path.join(dir, rel), content);
  }
  return dir;
};

describe("JsonReplace", () => {
  it("replaces a simple top-level key", async () => {
    const workDir = makeWorkdir({
      "config.json": JSON.stringify({ name: "old" }, null, 2) + "\n",
    });
    const action = new JsonReplace({
      file: "config.json",
      replace: [{ selector: "$.name", variable: "n" }],
    });
    await action.apply({ n: "new" }, workDir, workDir);
    const data = JSON.parse(readFileSync(path.join(workDir, "config.json"), "utf8"));
    expect(data.name).toBe("new");
  });

  it("handles nested paths with array indices", async () => {
    const workDir = makeWorkdir({
      "config.json":
        JSON.stringify(
          { items: [{ label: "a" }, { label: "b" }, { label: "c" }] },
          null,
          2,
        ) + "\n",
    });
    const action = new JsonReplace({
      file: "config.json",
      replace: [{ selector: "$.items[1].label", variable: "lbl" }],
    });
    await action.apply({ lbl: "MIDDLE" }, workDir, workDir);
    const data = JSON.parse(readFileSync(path.join(workDir, "config.json"), "utf8"));
    expect(data.items[1].label).toBe("MIDDLE");
    expect(data.items[0].label).toBe("a");
    expect(data.items[2].label).toBe("c");
  });

  it("applies multiple replacements in order", async () => {
    const workDir = makeWorkdir({
      "pkg.json":
        JSON.stringify({ name: "x", version: "1.0.0" }, null, 2) + "\n",
    });
    const action = new JsonReplace({
      file: "pkg.json",
      replace: [
        { selector: "$.name", variable: "n" },
        { selector: "$.version", variable: "v" },
      ],
    });
    await action.apply({ n: "my-pkg", v: "2.0.0" }, workDir, workDir);
    const data = JSON.parse(readFileSync(path.join(workDir, "pkg.json"), "utf8"));
    expect(data).toEqual({ name: "my-pkg", version: "2.0.0" });
  });

  it("writes with 2-space indent and trailing newline", async () => {
    const workDir = makeWorkdir({
      "config.json": JSON.stringify({ name: "old" }) + "\n",
    });
    const action = new JsonReplace({
      file: "config.json",
      replace: [{ selector: "$.name", variable: "n" }],
    });
    await action.apply({ n: "new" }, workDir, workDir);
    const text = readFileSync(path.join(workDir, "config.json"), "utf8");
    expect(text).toBe(`{\n  "name": "new"\n}\n`);
  });

  it("returns the target file", () => {
    const action = new JsonReplace({ file: "x.json", replace: [] });
    expect(action.targetFiles()).toEqual(["x.json"]);
  });

  it("skips an entry when its variable is null (optional unset)", async () => {
    const workDir = makeWorkdir({
      "config.json":
        JSON.stringify({ a: "keep", b: "replace" }, null, 2) + "\n",
    });
    const action = new JsonReplace({
      file: "config.json",
      replace: [
        { selector: "$.a", variable: "missing" },
        { selector: "$.b", variable: "present" },
      ],
    });
    await action.apply({ missing: null, present: "new" }, workDir, workDir);
    const data = JSON.parse(readFileSync(path.join(workDir, "config.json"), "utf8"));
    expect(data).toEqual({ a: "keep", b: "new" });
  });
});
