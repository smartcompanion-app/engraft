# engraft

Apply customizations to any project without templating placeholders.

engraft keeps the source repo clean and runnable while providing a declarative, reproducible customization layer on top. Repo authors declare **what** can be customized in a template file; consumers supply **their** choices in a values file; `engraft apply` merges them into the working tree in place.

## Implementations

Two implementations with identical behaviour, shipped as native packages in each ecosystem:

- **Python** — see [`python/README.md`](python/README.md), published to [PyPI](https://pypi.org/project/engraft/)
- **TypeScript / Node.js** — see [`typescript/README.md`](typescript/README.md), published to npm

Both implementations accept the same template and values YAML format, ship the same four actions (`json_replace`, `html_replace`, `regex_replace`, `file_replace`), and produce identical output for any given input.

## Shared behavioural contract

The `e2e/` directory holds a pytest-based end-to-end harness that is the source of truth for cross-implementation parity. Each fixture under `e2e/fixtures/` describes an input project, a template, a values file, and the expected post-apply tree. The harness runs every fixture against **both** the Python CLI (`engraft`) and the TypeScript CLI (`node typescript/dist/cli.js`) and asserts that the resulting project tree matches the expected output semantically (format-aware comparators for JSON, YAML, HTML; plain text otherwise).

Running the harness:

```bash
# From the repo root:
pip install -e python/
(cd typescript && npm install && npm run build)
pytest e2e/
```

Setting `ENGRAFT_IMPL=python` or `ENGRAFT_IMPL=typescript` restricts the harness to one implementation.

## Repository layout

```
python/       # Python implementation (published to PyPI as `engraft`)
typescript/   # TypeScript implementation (published to npm as `engraft`)
e2e/          # Shared behavioural fixtures and pytest harness
openspec/     # OpenSpec change proposals and specifications
```

## License

See [LICENSE](LICENSE).
