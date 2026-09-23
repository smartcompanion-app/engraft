# Changesets

This folder collects the pending changes for the next release. Each file
describes one change: the bump level it needs, and a sentence written for the
person reading the changelog.

Add one with:

```shell
npm run changeset
```

Commit the generated file with your pull request. Changes that publish nothing
— CI config, docs, tooling — do not need one.

On merge to `main`, the release workflow turns every pending changeset into a
`chore: release` pull request. Merging that pull request publishes to npm.

See [CONTRIBUTING.md](../CONTRIBUTING.md#releasing) for the full flow, and the
[changesets docs](https://github.com/changesets/changesets) for the file format.
