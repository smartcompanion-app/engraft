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

  async apply(
    variables: Variables,
    workDir: string,
    _valuesDir: string,
  ): Promise<void> {
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

      const pattern = new RegExp(normalized, "g");
      let matched = false;
      content = content.replace(pattern, (match, ...rest) => {
        matched = true;
        const last = rest[rest.length - 1];
        const groups =
          last && typeof last === "object"
            ? (last as Record<string, string | undefined>)
            : {};
        const valueMatch = groups.value;
        if (valueMatch === undefined) return match;
        // Find the value group's position within the match to preserve prefix/suffix.
        const idx = match.indexOf(valueMatch);
        if (idx === -1) return match;
        return match.slice(0, idx) + newValue + match.slice(idx + valueMatch.length);
      });

      if (!matched) {
        throw new Error(
          `Pattern ${JSON.stringify(entry.selector)} did not match anything in ${this.file}`,
        );
      }
    }

    await fs.writeFile(target, content);
  }

  targetFiles(): string[] {
    return [this.file];
  }
}
