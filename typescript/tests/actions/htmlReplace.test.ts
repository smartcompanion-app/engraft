import { mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, it, expect } from "vitest";

import { HtmlReplace } from "../../src/actions/htmlReplace.js";

const makeWorkdir = (files: Record<string, string>): string => {
  const dir = mkdtempSync(path.join(tmpdir(), "engraft-html-"));
  for (const [rel, content] of Object.entries(files)) {
    writeFileSync(path.join(dir, rel), content);
  }
  return dir;
};

describe("HtmlReplace", () => {
  it("replaces element text content", async () => {
    const workDir = makeWorkdir({
      "index.html":
        "<!DOCTYPE html>\n<html><head><title>Old Title</title></head><body></body></html>\n",
    });
    const action = new HtmlReplace({
      file: "index.html",
      replace: [{ selector: "//title", variable: "t" }],
    });
    await action.apply({ t: "New Title" }, workDir, workDir);
    const text = readFileSync(path.join(workDir, "index.html"), "utf8");
    expect(text).toContain("<title>New Title</title>");
    expect(text).not.toContain("Old Title");
  });

  it("replaces an attribute value", async () => {
    const workDir = makeWorkdir({
      "index.html":
        '<!DOCTYPE html>\n<html><head><meta name="description" content="old"></head><body></body></html>\n',
    });
    const action = new HtmlReplace({
      file: "index.html",
      replace: [
        { selector: '//meta[@name="description"]/@content', variable: "d" },
      ],
    });
    await action.apply({ d: "new description" }, workDir, workDir);
    const text = readFileSync(path.join(workDir, "index.html"), "utf8");
    expect(text).toContain('content="new description"');
  });

  it("preserves the DOCTYPE", async () => {
    const workDir = makeWorkdir({
      "index.html":
        "<!DOCTYPE html>\n<html><head><title>t</title></head><body></body></html>\n",
    });
    const action = new HtmlReplace({
      file: "index.html",
      replace: [{ selector: "//title", variable: "t" }],
    });
    await action.apply({ t: "Renamed" }, workDir, workDir);
    const text = readFileSync(path.join(workDir, "index.html"), "utf8");
    expect(text.startsWith("<!DOCTYPE html>")).toBe(true);
  });

  it("errors on 0 matches", async () => {
    const workDir = makeWorkdir({
      "index.html":
        "<!DOCTYPE html>\n<html><head></head><body></body></html>\n",
    });
    const action = new HtmlReplace({
      file: "index.html",
      replace: [{ selector: "//title", variable: "t" }],
    });
    await expect(action.apply({ t: "x" }, workDir, workDir)).rejects.toThrow(
      /matched no elements/,
    );
  });

  it("errors on multiple matches", async () => {
    const workDir = makeWorkdir({
      "index.html":
        "<!DOCTYPE html>\n<html><head></head><body><p>one</p><p>two</p></body></html>\n",
    });
    const action = new HtmlReplace({
      file: "index.html",
      replace: [{ selector: "//p", variable: "t" }],
    });
    await expect(action.apply({ t: "x" }, workDir, workDir)).rejects.toThrow(
      /matched 2 elements/,
    );
  });

  it("skips entry when variable is null", async () => {
    const workDir = makeWorkdir({
      "index.html":
        "<!DOCTYPE html>\n<html><head><title>keep</title></head><body></body></html>\n",
    });
    const action = new HtmlReplace({
      file: "index.html",
      replace: [{ selector: "//title", variable: "t" }],
    });
    await action.apply({ t: null }, workDir, workDir);
    const text = readFileSync(path.join(workDir, "index.html"), "utf8");
    expect(text).toContain("<title>keep</title>");
  });
});
