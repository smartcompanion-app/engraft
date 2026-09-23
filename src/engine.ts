import { promises as fs, existsSync } from "node:fs";
import path from "node:path";

import { parseTemplate, parseValues } from "./models.js";
import type { Variables } from "./actions/base.js";

export const STAGING_DIR_NAME = ".engraft";

interface ApplyOptions {
  workDir?: string;
}

const rmrf = async (dir: string): Promise<void> => {
  await fs.rm(dir, { recursive: true, force: true });
};

const copyFile = async (src: string, dst: string): Promise<void> => {
  await fs.mkdir(path.dirname(dst), { recursive: true });
  await fs.copyFile(src, dst);
};

const walkFiles = async (dir: string): Promise<string[]> => {
  const out: string[] = [];
  const entries = await fs.readdir(dir, { withFileTypes: true });
  for (const entry of entries) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      out.push(...(await walkFiles(full)));
    } else if (entry.isFile()) {
      out.push(full);
    }
  }
  return out;
};

export const apply = async (
  templatePath: string,
  valuesPath: string,
  options: ApplyOptions = {},
): Promise<void> => {
  const absTemplate = path.resolve(templatePath);
  const absValues = path.resolve(valuesPath);
  const workDir = path.resolve(options.workDir ?? process.cwd());
  const valuesDir = path.dirname(absValues);

  const template = parseTemplate(absTemplate);
  const values = parseValues(absValues);

  const variables: Variables = {};
  for (const [name, variable] of Object.entries(template.variables)) {
    if (Object.prototype.hasOwnProperty.call(values, name)) {
      variables[name] = values[name] ?? null;
    } else {
      variables[name] = variable.default;
    }
  }

  const stagingDir = path.join(workDir, STAGING_DIR_NAME);

  const targetFiles = new Set<string>();
  for (const action of template.customizations) {
    for (const rel of action.targetFiles()) {
      targetFiles.add(rel);
    }
  }

  if (existsSync(stagingDir)) {
    await rmrf(stagingDir);
  }
  await fs.mkdir(stagingDir);

  try {
    for (const rel of targetFiles) {
      const src = path.join(workDir, rel);
      const dst = path.join(stagingDir, rel);
      if (existsSync(src)) {
        await copyFile(src, dst);
      }
    }

    for (const action of template.customizations) {
      await action.apply(variables, stagingDir, valuesDir);
    }

    const stagedFiles = await walkFiles(stagingDir);
    for (const staged of stagedFiles) {
      const rel = path.relative(stagingDir, staged);
      const dest = path.join(workDir, rel);
      await copyFile(staged, dest);
    }
  } finally {
    await rmrf(stagingDir);
  }
};
