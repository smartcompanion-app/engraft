export type Variables = Record<string, string | null>;

export interface Action {
  apply(
    variables: Variables,
    workDir: string,
    valuesDir: string,
  ): Promise<void>;
  targetFiles(): string[];
}

export interface ActionCtor {
  new (config: Record<string, unknown>): Action;
}
