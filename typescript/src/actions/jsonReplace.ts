import { promises as fs } from "node:fs";
import path from "node:path";

import type { Action, Variables } from "./base.js";
import { register } from "./registry.js";

type JsonValue =
  | string
  | number
  | boolean
  | null
  | JsonValue[]
  | { [k: string]: JsonValue };

type PathPart = string | number;

const parsePath = (dotPath: string): PathPart[] => {
  const parts: PathPart[] = [];
  for (const segment of dotPath.split(".")) {
    const bracket = /^([^\[]*)\[(\d+)\]$/.exec(segment);
    if (bracket) {
      const [, key, index] = bracket;
      if (key) parts.push(key);
      parts.push(Number(index));
    } else {
      parts.push(segment);
    }
  }
  return parts;
};

const setAtPath = (
  obj: JsonValue,
  keys: PathPart[],
  value: string,
): void => {
  let cursor: JsonValue = obj;
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i]!;
    const next = keys[i + 1]!;
    if (typeof key === "number") {
      if (!Array.isArray(cursor) || key >= cursor.length) {
        throw new Error(`Array index ${key} out of range`);
      }
      cursor = cursor[key]!;
    } else {
      if (
        cursor === null ||
        typeof cursor !== "object" ||
        Array.isArray(cursor)
      ) {
        throw new Error(`Cannot descend into non-object at key ${key}`);
      }
      const container = cursor as { [k: string]: JsonValue };
      if (!(key in container)) {
        container[key] = typeof next === "number" ? [] : {};
      }
      cursor = container[key]!;
    }
  }
  const last = keys[keys.length - 1]!;
  if (typeof last === "number") {
    if (!Array.isArray(cursor)) {
      throw new Error(`Cannot set index ${last} on non-array`);
    }
    cursor[last] = value;
  } else {
    if (
      cursor === null ||
      typeof cursor !== "object" ||
      Array.isArray(cursor)
    ) {
      throw new Error(`Cannot set key ${last} on non-object`);
    }
    (cursor as { [k: string]: JsonValue })[last] = value;
  }
};

interface ReplaceEntry {
  selector: string;
  variable: string;
}

@register("json_replace")
export class JsonReplace implements Action {
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
    const text = await fs.readFile(target, "utf8");
    const data = JSON.parse(text) as JsonValue;

    for (const entry of this.replace) {
      const value = variables[entry.variable];
      if (value == null) continue;

      let selector = entry.selector;
      if (selector.startsWith("$.")) {
        selector = selector.slice(2);
      }
      const parsed = parsePath(selector);
      setAtPath(data, parsed, value);
    }

    await fs.writeFile(target, JSON.stringify(data, null, 2) + "\n");
  }

  targetFiles(): string[] {
    return [this.file];
  }
}
