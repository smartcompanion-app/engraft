import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import { Command } from "commander";

import { apply } from "./engine.js";

const readVersion = (): string => {
  try {
    const here = path.dirname(fileURLToPath(import.meta.url));
    // In dev (ts source) this lands in src/; in built output it lands in dist/.
    // In both cases, package.json sits one directory up.
    const pkgPath = path.resolve(here, "..", "package.json");
    const pkg = JSON.parse(readFileSync(pkgPath, "utf8")) as { version?: string };
    return pkg.version ?? "0.0.0";
  } catch {
    return "0.0.0";
  }
};

export const buildProgram = (): Command => {
  const program = new Command();
  program
    .name("engraft")
    .description(
      "engraft - Apply customizations to any project without templating placeholders.",
    )
    .version(readVersion(), "--version", "Show the engraft version and exit.");

  program
    .command("apply")
    .description("Apply a template with values to the current directory.")
    .requiredOption("--template <path>", "Path to the template YAML file")
    .requiredOption("--values <path>", "Path to the values YAML file")
    .action(async (opts: { template: string; values: string }) => {
      try {
        await apply(opts.template, opts.values);
        process.stdout.write("Done. Customizations applied successfully.\n");
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        process.stderr.write(`Error: ${msg}\n`);
        process.exit(1);
      }
    });

  return program;
};

const isMain = (): boolean => {
  if (!process.argv[1]) return false;
  try {
    return (
      fileURLToPath(import.meta.url) === path.resolve(process.argv[1])
    );
  } catch {
    return false;
  }
};

if (isMain()) {
  buildProgram().parseAsync(process.argv);
}
