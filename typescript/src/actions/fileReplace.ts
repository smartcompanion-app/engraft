import { promises as fs, existsSync } from "node:fs";
import path from "node:path";

import type { Action, Variables } from "./base.js";
import { register } from "./registry.js";

@register("file_replace")
export class FileReplace implements Action {
  private readonly file: string;
  private readonly variable: string;

  constructor(config: Record<string, unknown>) {
    this.file = String(config.file);
    this.variable = String(config.variable);
  }

  async apply(
    variables: Variables,
    workDir: string,
    valuesDir: string,
  ): Promise<void> {
    const value = variables[this.variable];
    if (value == null) return;

    const sourcePath = path.resolve(valuesDir, value);
    const targetPath = path.join(workDir, this.file);

    if (!existsSync(sourcePath)) {
      throw new Error(`Source file does not exist: ${sourcePath}`);
    }
    if (!existsSync(targetPath)) {
      throw new Error(`Target file does not exist: ${targetPath}`);
    }

    await fs.copyFile(sourcePath, targetPath);
  }

  targetFiles(): string[] {
    return [this.file];
  }
}
