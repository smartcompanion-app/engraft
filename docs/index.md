# engraft

Apply customizations to any project without templating placeholders.

## The problem

Customizing a project — white-labelling an app, rebranding a starter, shipping
the same product under five names — usually forces a choice between three bad
options:

- **Templating tools** (Cookiecutter, Copier, Yeoman) ask you to put
  `{{ placeholders }}` in your source. The repository stops being a working
  app: you cannot run it, test it or open it in a browser without rendering it
  first.
- **Forking** gives you a working app, and then two codebases that drift apart.
  Every upstream fix becomes a merge.
- **Editing by hand** works once. It is undocumented, unreproducible, and
  nobody remembers which twelve files needed touching.

## What engraft does instead

engraft leaves your repository alone and describes the customization
separately. Nothing in your source changes shape; `config.json` stays valid
JSON, `index.html` stays a page you can open.

Two files carry the whole thing:

- A **template file**, written by whoever maintains the project, declaring what
  may be customized and where it lives.
- A **values file**, written by whoever is customizing it, saying what those
  things should become.

```
project (unchanged, runnable)  +  template  +  values  →  engraft apply  →  customized project
```

An apply is idempotent and re-runnable: point it at different values and you
get a different result from the same starting repository, every time.

## Where to go next

| If you want to…                                         | Read                                  |
| ------------------------------------------------------- | ------------------------------------- |
| Install it and change your first value                  | [Getting started](getting-started.md) |
| Understand the template/values split                    | [Concepts](concepts/index.md)         |
| Look up how a specific action works                     | [Actions](actions/index.md)           |
| Check a command or flag                                 | [CLI reference](cli.md)               |
| Know what happens on disk during an apply, and on error | [Architecture](architecture.md)       |
| Work on engraft itself                                  | [Contributing](../CONTRIBUTING.md)    |
