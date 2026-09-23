import { existsSync, readFileSync, readdirSync } from "node:fs";
import path from "node:path";

import { JSDOM } from "jsdom";
import { load } from "js-yaml";
import { expect } from "vitest";

/**
 * Semantic comparators for e2e output comparison.
 *
 * A fixture's `expected/` tree describes the *meaning* of a correct apply, not
 * a byte-for-byte rendering. Key order in JSON, quoting style in YAML and
 * attribute order in HTML are all serialiser details engraft is free to change,
 * so each format gets a comparator that looks past them. Anything without a
 * known format falls back to a text comparison with line endings normalised.
 */

const readText = (file: string): string => readFileSync(file, "utf8").replaceAll("\r\n", "\n");

const compareText = (expected: string, actual: string): void => {
  expect(readText(actual), `text content differs: ${actual}`).toBe(readText(expected));
};

const compareJson = (expected: string, actual: string): void => {
  expect(JSON.parse(readText(actual)), `JSON content differs: ${actual}`).toEqual(
    JSON.parse(readText(expected)),
  );
};

const compareYaml = (expected: string, actual: string): void => {
  expect(load(readText(actual)), `YAML content differs: ${actual}`).toEqual(
    load(readText(expected)),
  );
};

const normalizeWhitespace = (text: string | null): string =>
  (text ?? "").replace(/\s+/gu, " ").trim();

type HtmlNode = string | { comment: string } | HtmlElementSignature;

interface HtmlElementSignature {
  tag: string;
  attributes: Record<string, string>;
  children: HtmlNode[];
}

/**
 * Reduce an element to the parts that carry meaning: its tag, its attributes
 * (sorted, so serialiser ordering cannot fail a comparison) and its children,
 * with whitespace-only text nodes dropped. Indentation therefore does not
 * matter, but a changed word does.
 */
const elementSignature = (el: Element): HtmlElementSignature => {
  const attributes: Record<string, string> = {};
  for (const name of el.getAttributeNames().toSorted()) {
    attributes[name] = el.getAttribute(name) ?? "";
  }

  const children: HtmlNode[] = [];
  for (const node of el.childNodes) {
    if (node.nodeType === node.TEXT_NODE) {
      const text = normalizeWhitespace(node.textContent);
      if (text) children.push(text);
    } else if (node.nodeType === node.ELEMENT_NODE) {
      children.push(elementSignature(node as Element));
    } else if (node.nodeType === node.COMMENT_NODE) {
      children.push({ comment: normalizeWhitespace(node.textContent) });
    }
  }

  return { tag: el.tagName.toLowerCase(), attributes, children };
};

const htmlSignature = (file: string): HtmlElementSignature => {
  const dom = new JSDOM(readText(file), { contentType: "text/html" });
  return elementSignature(dom.window.document.documentElement);
};

const compareHtml = (expected: string, actual: string): void => {
  expect(htmlSignature(actual), `HTML structure differs: ${actual}`).toEqual(
    htmlSignature(expected),
  );
};

type Comparator = (expected: string, actual: string) => void;

const COMPARATORS: Record<string, Comparator> = {
  ".json": compareJson,
  ".yaml": compareYaml,
  ".yml": compareYaml,
  ".html": compareHtml,
  ".htm": compareHtml,
};

const walkFiles = (dir: string, prefix = ""): string[] =>
  readdirSync(dir, { withFileTypes: true })
    .flatMap((entry) => {
      const rel = path.join(prefix, entry.name);
      if (entry.isDirectory()) return walkFiles(path.join(dir, entry.name), rel);
      return entry.isFile() ? [rel] : [];
    })
    .toSorted();

/**
 * Assert that every file under `expectedDir` exists under `actualDir` with
 * equivalent content. Extra files in `actualDir` are ignored — fixtures state
 * what must be true, not an exhaustive directory listing.
 */
export const compareTree = (expectedDir: string, actualDir: string): void => {
  for (const rel of walkFiles(expectedDir)) {
    const expected = path.join(expectedDir, rel);
    const actual = path.join(actualDir, rel);
    expect(existsSync(actual), `expected file is missing from the result tree: ${rel}`).toBe(true);
    const comparator = COMPARATORS[path.extname(rel).toLowerCase()] ?? compareText;
    comparator(expected, actual);
  }
};
