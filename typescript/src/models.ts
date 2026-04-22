import { readFileSync } from "node:fs";
import yaml from "js-yaml";

import { createAction } from "./actions/index.js";
import type { Action } from "./actions/base.js";

export interface Variable {
  name: string;
  description: string;
  default: string | null;
}

export interface Template {
  variables: Record<string, Variable>;
  customizations: Action[];
}

export type Values = Record<string, string>;

interface RawVariable {
  description?: string;
  default?: string | number | boolean | null;
}

interface RawTemplate {
  variables?: Record<string, RawVariable> | null;
  customizations?: Array<Record<string, unknown>> | null;
}

const loadYaml = (path: string): unknown => {
  const text = readFileSync(path, "utf8");
  return yaml.load(text);
};

export const parseTemplate = (path: string): Template => {
  const data = (loadYaml(path) ?? {}) as RawTemplate;

  const variables: Record<string, Variable> = {};
  for (const [name, raw] of Object.entries(data.variables ?? {})) {
    const hasDefault =
      raw != null &&
      Object.prototype.hasOwnProperty.call(raw, "default") &&
      raw.default !== null &&
      raw.default !== undefined;
    variables[name] = {
      name,
      description: raw?.description ?? "",
      default: hasDefault ? String(raw.default) : null,
    };
  }

  const customizations: Action[] = [];
  for (const item of data.customizations ?? []) {
    const { action: actionName, ...config } = item as { action: string };
    if (typeof actionName !== "string") {
      throw new Error("Each customization must have an 'action' field");
    }
    customizations.push(createAction(actionName, config));
  }

  return { variables, customizations };
};

export const parseValues = (path: string): Values => {
  const data = loadYaml(path);
  if (data == null) {
    return {};
  }
  if (typeof data !== "object" || Array.isArray(data)) {
    throw new Error(`Values file ${path} must be a mapping`);
  }
  const out: Values = {};
  for (const [k, v] of Object.entries(data as Record<string, unknown>)) {
    if (v == null) continue;
    out[k] = String(v);
  }
  return out;
};
