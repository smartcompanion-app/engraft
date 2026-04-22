import { promises as fs } from "node:fs";
import path from "node:path";

import { JSDOM } from "jsdom";

import type { Action, Variables } from "./base.js";
import { register } from "./registry.js";

interface ReplaceEntry {
  selector: string;
  variable: string;
}

const DOCTYPE_RE = /^\s*<!DOCTYPE[^>]*>/i;

const extractDoctype = (html: string): string | null => {
  const match = DOCTYPE_RE.exec(html);
  return match ? match[0].replace(/^\s+/, "") : null;
};

const stripDoctype = (html: string): string => html.replace(DOCTYPE_RE, "");

@register("html_replace")
export class HtmlReplace implements Action {
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
    const rawHtml = await fs.readFile(target, "utf8");
    const doctype = extractDoctype(rawHtml);
    const withoutDoctype = stripDoctype(rawHtml);

    const dom = new JSDOM(withoutDoctype, { contentType: "text/html" });
    const { document } = dom.window;
    const XPathResult = dom.window.XPathResult;

    for (const entry of this.replace) {
      const value = variables[entry.variable];
      if (value == null) continue;

      const result = document.evaluate(
        entry.selector,
        document,
        null,
        XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
        null,
      );

      const count = result.snapshotLength;
      if (count === 0) {
        throw new Error(
          `XPath selector ${JSON.stringify(entry.selector)} matched no elements in ${this.file}`,
        );
      }
      if (count > 1) {
        throw new Error(
          `XPath selector ${JSON.stringify(entry.selector)} matched ${count} elements in ${this.file}, expected exactly 1`,
        );
      }

      const node = result.snapshotItem(0)!;
      if (node.nodeType === dom.window.Node.ATTRIBUTE_NODE) {
        (node as Attr).value = value;
      } else if (node.nodeType === dom.window.Node.ELEMENT_NODE) {
        (node as Element).textContent = value;
      } else {
        throw new Error(
          `XPath selector ${JSON.stringify(entry.selector)} resolved to an unsupported node type`,
        );
      }
    }

    const body = dom.serialize();
    const output = doctype ? `${doctype}\n${body}\n` : `${body}\n`;
    await fs.writeFile(target, output);
  }

  targetFiles(): string[] {
    return [this.file];
  }
}
