import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, it, expect } from "vitest";

import { RegexReplace } from "../../src/actions/regexReplace.js";

const makeWorkdir = (files: Record<string, string>): string => {
  const dir = mkdtempSync(path.join(tmpdir(), "engraft-regex-"));
  for (const [rel, content] of Object.entries(files)) {
    writeFileSync(path.join(dir, rel), content);
  }
  return dir;
};

describe("RegexReplace", () => {
  it("accepts ECMAScript named-group syntax", async () => {
    const workDir = makeWorkdir({
      "colors.ts": 'export const PRIMARY = "#ff0000";\n',
    });
    const action = new RegexReplace({
      file: "colors.ts",
      replace: [
        {
          selector: '(PRIMARY\\s*=\\s*)"(?<value>[^"]*)"',
          variable: "c",
        },
      ],
    });
    await action.apply({ c: "#00ff00" }, workDir, workDir);
    const text = readFileSync(path.join(workDir, "colors.ts"), "utf8");
    expect(text).toContain("#00ff00");
    expect(text).not.toContain("#ff0000");
  });

  it("accepts Python-style (?P<value>...) syntax", async () => {
    const workDir = makeWorkdir({
      "colors.ts": 'export const PRIMARY = "#ff0000";\n',
    });
    const action = new RegexReplace({
      file: "colors.ts",
      replace: [
        {
          selector: '(PRIMARY\\s*=\\s*)"(?P<value>[^"]*)"',
          variable: "c",
        },
      ],
    });
    await action.apply({ c: "#00ff00" }, workDir, workDir);
    const text = readFileSync(path.join(workDir, "colors.ts"), "utf8");
    expect(text).toContain("#00ff00");
  });

  it("throws when no named group is present", async () => {
    const workDir = makeWorkdir({ "t.ts": "hello" });
    const action = new RegexReplace({
      file: "t.ts",
      replace: [{ selector: "hello", variable: "c" }],
    });
    await expect(
      action.apply({ c: "world" }, workDir, workDir),
    ).rejects.toThrow(/named group/);
  });

  it("throws when the pattern does not match", async () => {
    const workDir = makeWorkdir({ "t.ts": "hello world" });
    const action = new RegexReplace({
      file: "t.ts",
      replace: [
        { selector: 'MISSING\\s*=\\s*"(?<value>[^"]*)"', variable: "c" },
      ],
    });
    await expect(
      action.apply({ c: "x" }, workDir, workDir),
    ).rejects.toThrow(/did not match/);
  });

  it("applies multiple replacements", async () => {
    const workDir = makeWorkdir({
      "colors.ts":
        'export const PRIMARY = "#ff0000";\nexport const SECONDARY = "#00ff00";\n',
    });
    const action = new RegexReplace({
      file: "colors.ts",
      replace: [
        {
          selector: '(PRIMARY\\s*=\\s*)"(?<value>[^"]*)"',
          variable: "p",
        },
        {
          selector: '(SECONDARY\\s*=\\s*)"(?<value>[^"]*)"',
          variable: "s",
        },
      ],
    });
    await action.apply({ p: "#111111", s: "#222222" }, workDir, workDir);
    const text = readFileSync(path.join(workDir, "colors.ts"), "utf8");
    expect(text).toContain("#111111");
    expect(text).toContain("#222222");
    expect(text).not.toContain("#ff0000");
    expect(text).not.toContain("#00ff00");
  });

  it("skips entry when variable is null", async () => {
    const workDir = makeWorkdir({ "t.ts": 'K = "orig";\n' });
    const action = new RegexReplace({
      file: "t.ts",
      replace: [
        { selector: 'K = "(?<value>[^"]*)"', variable: "c" },
      ],
    });
    await action.apply({ c: null }, workDir, workDir);
    expect(readFileSync(path.join(workDir, "t.ts"), "utf8")).toContain("orig");
  });
});
