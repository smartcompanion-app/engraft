import { existsSync, mkdtempSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import { describe, it, expect, beforeEach } from "vitest";

import { STAGING_DIR_NAME, apply } from "../src/engine.js";

interface Fixture {
  projectDir: string;
  templatePath: string;
  valuesPath: string;
  valuesDir: string;
}

const writeFile = (p: string, content: string): void => {
  mkdirSync(path.dirname(p), { recursive: true });
  writeFileSync(p, content);
};

const makeFixture = (
  template: unknown,
  values: Record<string, unknown>,
  projectFiles: Record<string, string>,
): Fixture => {
  const root = mkdtempSync(path.join(tmpdir(), "engraft-engine-"));
  const projectDir = path.join(root, "project");
  mkdirSync(projectDir, { recursive: true });
  for (const [rel, content] of Object.entries(projectFiles)) {
    writeFile(path.join(projectDir, rel), content);
  }
  const valuesDir = path.join(root, "values");
  mkdirSync(valuesDir, { recursive: true });
  const templatePath = path.join(root, "template.yml");
  const valuesPath = path.join(valuesDir, "values.yml");
  writeFileSync(templatePath, toYaml(template));
  writeFileSync(valuesPath, toYaml(values));
  return { projectDir, templatePath, valuesPath, valuesDir };
};

const toYaml = (obj: unknown): string => {
  // small inline yaml dump - just JSON works since js-yaml reads JSON as YAML
  return JSON.stringify(obj, null, 2);
};

describe("engine.apply", () => {
  let fx: Fixture;

  beforeEach(() => {
    fx = makeFixture(
      {
        variables: { name: { description: "n", default: "original" } },
        customizations: [
          {
            action: "json_replace",
            file: "config.json",
            replace: [{ selector: "$.name", variable: "name" }],
          },
        ],
      },
      { name: "NewApp" },
      { "config.json": JSON.stringify({ name: "original" }, null, 2) + "\n" },
    );
  });

  it("modifies project files on success", async () => {
    await apply(fx.templatePath, fx.valuesPath, { workDir: fx.projectDir });
    const data = JSON.parse(
      readFileSync(path.join(fx.projectDir, "config.json"), "utf8"),
    );
    expect(data.name).toBe("NewApp");
  });

  it("removes the staging directory after success", async () => {
    await apply(fx.templatePath, fx.valuesPath, { workDir: fx.projectDir });
    expect(existsSync(path.join(fx.projectDir, STAGING_DIR_NAME))).toBe(false);
  });

  it("uses default when values omit the override", async () => {
    const fx2 = makeFixture(
      {
        variables: { name: { description: "n", default: "the-default" } },
        customizations: [
          {
            action: "json_replace",
            file: "config.json",
            replace: [{ selector: "$.name", variable: "name" }],
          },
        ],
      },
      {},
      { "config.json": JSON.stringify({ name: "original" }, null, 2) + "\n" },
    );
    await apply(fx2.templatePath, fx2.valuesPath, { workDir: fx2.projectDir });
    const data = JSON.parse(
      readFileSync(path.join(fx2.projectDir, "config.json"), "utf8"),
    );
    expect(data.name).toBe("the-default");
  });

  it("leaves the file untouched when an optional variable is unset (noop)", async () => {
    const fx2 = makeFixture(
      {
        variables: { name: { description: "n" } },
        customizations: [
          {
            action: "json_replace",
            file: "config.json",
            replace: [{ selector: "$.name", variable: "name" }],
          },
        ],
      },
      {},
      { "config.json": JSON.stringify({ name: "original" }, null, 2) + "\n" },
    );
    await apply(fx2.templatePath, fx2.valuesPath, { workDir: fx2.projectDir });
    const data = JSON.parse(
      readFileSync(path.join(fx2.projectDir, "config.json"), "utf8"),
    );
    expect(data.name).toBe("original");
  });

  it("rolls back on action failure", async () => {
    const fx2 = makeFixture(
      {
        variables: { name: { description: "n", default: "NewApp" } },
        customizations: [
          {
            action: "json_replace",
            file: "config.json",
            replace: [{ selector: "$.name", variable: "name" }],
          },
          {
            action: "regex_replace",
            file: "missing.txt",
            replace: [
              { selector: '"(?P<value>x)"', variable: "name" },
            ],
          },
        ],
      },
      {},
      { "config.json": JSON.stringify({ name: "original" }, null, 2) + "\n" },
    );

    await expect(
      apply(fx2.templatePath, fx2.valuesPath, { workDir: fx2.projectDir }),
    ).rejects.toBeDefined();

    const data = JSON.parse(
      readFileSync(path.join(fx2.projectDir, "config.json"), "utf8"),
    );
    expect(data.name).toBe("original");
    expect(existsSync(path.join(fx2.projectDir, STAGING_DIR_NAME))).toBe(false);
  });

  it("removes a pre-existing staging directory", async () => {
    mkdirSync(path.join(fx.projectDir, STAGING_DIR_NAME), { recursive: true });
    writeFile(path.join(fx.projectDir, STAGING_DIR_NAME, "stale.txt"), "stale");
    await apply(fx.templatePath, fx.valuesPath, { workDir: fx.projectDir });
    expect(existsSync(path.join(fx.projectDir, STAGING_DIR_NAME))).toBe(false);
  });
});
