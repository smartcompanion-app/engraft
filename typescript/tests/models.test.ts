import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, it, expect } from "vitest";

import { parseTemplate, parseValues } from "../src/models.js";

const writeTmp = (name: string, contents: string): string => {
  const dir = mkdtempSync(path.join(tmpdir(), "engraft-"));
  const p = path.join(dir, name);
  writeFileSync(p, contents);
  return p;
};

describe("parseTemplate", () => {
  it("parses empty template to empty variables and customizations", () => {
    const p = writeTmp("template.yml", "");
    const t = parseTemplate(p);
    expect(t.variables).toEqual({});
    expect(t.customizations).toEqual([]);
  });

  it("parses variables with and without defaults", () => {
    const p = writeTmp(
      "template.yml",
      `variables:
  a:
    description: has default
    default: hello
  b:
    description: no default
`,
    );
    const t = parseTemplate(p);
    expect(t.variables.a?.default).toBe("hello");
    expect(t.variables.b?.default).toBeNull();
  });

  it("distinguishes explicit empty default from absent default", () => {
    const p = writeTmp(
      "template.yml",
      `variables:
  a:
    description: empty
    default: ""
  b:
    description: absent
`,
    );
    const t = parseTemplate(p);
    expect(t.variables.a?.default).toBe("");
    expect(t.variables.b?.default).toBeNull();
  });

  it("throws on malformed YAML", () => {
    const p = writeTmp("template.yml", "variables:\n  a:\n    - bad: : :\n");
    expect(() => parseTemplate(p)).toThrow();
  });

  it("instantiates customizations through the registry", () => {
    const p = writeTmp(
      "template.yml",
      `customizations:
  - action: json_replace
    file: config.json
    replace:
      - { selector: "$.name", variable: n }
`,
    );
    const t = parseTemplate(p);
    expect(t.customizations).toHaveLength(1);
    expect(t.customizations[0]?.targetFiles()).toEqual(["config.json"]);
  });
});

describe("parseValues", () => {
  it("returns empty dict for empty file", () => {
    const p = writeTmp("values.yml", "");
    expect(parseValues(p)).toEqual({});
  });

  it("returns string map for key:value file", () => {
    const p = writeTmp("values.yml", "a: hello\nb: 42\n");
    expect(parseValues(p)).toEqual({ a: "hello", b: "42" });
  });

  it("parses yes/no/on/off as strings (YAML 1.2)", () => {
    const p = writeTmp("values.yml", "flag: yes\nother: on\n");
    const v = parseValues(p);
    expect(v.flag).toBe("yes");
    expect(v.other).toBe("on");
  });
});
