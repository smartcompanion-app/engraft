import { promises as fs } from "node:fs";
import path from "node:path";

import type { Action, Variables } from "./base.js";
import { register } from "./registry.js";

interface ReplaceEntry {
  selector: string;
  variable: string;
}

@register("regex_replace")
export class RegexReplace implements Action {
  private readonly file: string;
  private readonly replace: ReplaceEntry[];

  constructor(config: Record<string, unknown>) {
    this.file = String(config.file);
    this.replace = (config.replace as ReplaceEntry[] | undefined) ?? [];
  }

  async apply(variables: Variables, workDir: string, _valuesDir: string): Promise<void> {
    const target = path.join(workDir, this.file);
    let content = await fs.readFile(target, "utf8");

    for (const entry of this.replace) {
      const newValue = variables[entry.variable];
      if (newValue == null) continue;

      const normalized = entry.selector.replace(/\(\?P<value>/g, "(?<value>");

      if (!normalized.includes("(?<value>")) {
        throw new Error(
          `Pattern must contain a (?P<value>...) or (?<value>...) named group: ${JSON.stringify(entry.selector)}`,
        );
      }

      // The `d` flag records where each group matched. Searching the match
      // text for the captured string instead would rewrite the wrong run
      // whenever the same text also appears in the pattern's prefix, as in
      // `version="(?<value>[^"]*)"` against `version="version"`.
      const pattern = new RegExp(normalized, "dg");
      const matches = [...content.matchAll(pattern)];

      if (matches.length === 0) {
        throw new Error(
          `Pattern ${JSON.stringify(entry.selector)} did not match anything in ${this.file}`,
        );
      }

      // Splice from the end so each replacement leaves the offsets of the
      // ones still to come untouched.
      for (const match of matches.toReversed()) {
        const span = match.indices?.groups?.["value"];
        if (!span) continue;
        const [start, end] = span;
        content = content.slice(0, start) + newValue + content.slice(end);
      }
    }

    await fs.writeFile(target, content);
  }

  targetFiles(): string[] {
    return [this.file];
  }
}
