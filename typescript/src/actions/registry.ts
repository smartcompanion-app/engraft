import type { Action, ActionCtor } from "./base.js";

const registry = new Map<string, ActionCtor>();

export const register =
  (name: string) =>
  <T extends ActionCtor>(ctor: T): T => {
    registry.set(name, ctor);
    return ctor;
  };

export const createAction = (
  name: string,
  config: Record<string, unknown>,
): Action => {
  const ctor = registry.get(name);
  if (!ctor) {
    const available = [...registry.keys()];
    throw new Error(
      `Unknown action: ${JSON.stringify(name)}. Available: ${JSON.stringify(available)}`,
    );
  }
  return new ctor(config);
};
