# Architecture

What happens on disk during `engraft apply`, and why.

## The pipeline

```
cli.ts                    parse argv, report the outcome
  └─ engine.apply()       resolve variables, stage, run actions, copy back
      ├─ models.ts        parse the template and values YAML
      └─ actions/         the registry, and the four actions
```

An apply runs in five steps:

1. **Parse.** The template and values files are read as YAML 1.2. The template
   becomes a list of variable declarations and a list of instantiated actions.
2. **Resolve variables.** Values override defaults; a variable with neither
   resolves to nothing. This happens once, before any action runs, so every
   action sees the same map. See
   [Variables](concepts/variables.md).
3. **Stage.** Each action declares the files it touches. Those files are copied
   into a staging directory, `.engraft/`, preserving their relative paths.
4. **Run the actions**, in template order, **against the staging copies**. The
   project itself is not touched.
5. **Copy back** — only if every action succeeded. The staging directory is
   then removed.

## Why the staging directory

A customization usually spans several files. Editing them in place means that
the fifth action failing leaves four files already changed and one not — a
state that is neither the original nor the intended result, and that nothing
records how to get out of.

So actions never write to the project. They write to `.engraft/`, and the copy
back only happens once all of them have finished:

```
project/                          project/.engraft/
  package.json        ── copy ─→    package.json
  public/index.html   ── copy ─→    public/index.html
                                       │
                                    actions run here
                                       │
  package.json        ←─ copy ──    package.json
  public/index.html   ←─ copy ──    public/index.html
```

If anything throws — a selector matching nothing, a missing source file,
malformed JSON — the copy back never starts and the project is untouched. The
staging directory is removed either way.

This is what the CLI's exit code means: **1 means nothing was written**, not
"something was half written".

### `.engraft/`

- Created fresh at the start of every apply. One left over from a crashed run
  is removed first, so a stale directory cannot leak into a later result.
- Removed at the end, success or failure.
- Listed in the project's `.gitignore` as a precaution. You should never see
  it.

## Target file collection

Every action implements `targetFiles()`, returning the project-relative paths
it operates on. The engine collects them across all actions, deduplicates, and
copies only those files into staging — not the whole project.

Two consequences worth knowing:

- Two actions targeting the same file share one staging copy, so the second
  sees the first one's result. Ordering within a template is meaningful.
- An action that writes to a file it does not declare would write outside the
  transaction and break rollback. This is the rule to remember when
  [adding an action](../CONTRIBUTING.md#adding-an-action).

Files an action targets that do not exist in the project are simply not staged.
Each action decides what that means: `json_replace` fails on a missing file,
`file_replace` fails with a message naming the path.

## The action registry

Actions are a plugin registry keyed by the string used in a template:

```ts
@register("json_replace")
export class JsonReplace implements Action {
  constructor(config: Record<string, unknown>) { … }
  async apply(variables, workDir, valuesDir): Promise<void> { … }
  targetFiles(): string[] { … }
}
```

`createAction(name, config)` looks the name up and constructs it; an unknown
name throws an error listing the registered ones.

Registration is a **side effect of importing the module**, which is why
`src/actions/index.ts` imports every action file. An action nobody imports is
not registered and does not exist as far as a template is concerned.

## Implementation notes

| Concern            | Choice                                                                                                                           |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| YAML               | js-yaml, default schema — YAML 1.2, so `yes`/`no`/`on`/`off` are strings                                                         |
| JSON paths         | A small dot-path parser, not a JSONPath library — no wildcards, no filters                                                       |
| HTML               | jsdom, with XPath via `document.evaluate`                                                                                        |
| Regex named groups | `(?P<value>…)` is normalised to `(?<value>…)` before compiling                                                                   |
| Regex positioning  | The `d` flag gives exact group offsets, so the captured run is rewritten even when the same text appears in the pattern's prefix |
| Distribution       | tsup/esbuild bundles `src/cli.ts` to a single ESM file with a shebang                                                            |

The Node floor (22.22.2) comes from jsdom, the heaviest dependency and the only
reason engraft needs a DOM at all.

## Why two test projects

The `unit` project imports the TypeScript sources directly and covers each
action's behaviour in detail. The `e2e` project runs `dist/cli.js` as a
subprocess against fixture directories, and can only assert what a user could
observe.

Both are needed. Unit tests catch logic errors quickly; the e2e project catches
everything that only goes wrong in the shipped artefact — a broken bundle, a
missing shebang, an entry point that does not run when invoked through an npm
bin symlink. That last one shipped in v0.2.1 with a fully green unit suite, and
is now covered by a test that packs and runs the tarball in CI.

See [Contributing](../CONTRIBUTING.md#testing).
