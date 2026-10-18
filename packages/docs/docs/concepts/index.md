# Concepts

engraft has one idea in it: the description of _what can change_ and the
decision about _what it changes to_ are written by different people, at
different times, and therefore live in different files.

## The two-file model

| File              | Written by             | Lives in                       | Answers                           |
| ----------------- | ---------------------- | ------------------------------ | --------------------------------- |
| **Template file** | The project maintainer | The project repository         | What may be customized, and where |
| **Values file**   | The consumer           | Wherever the consumer keeps it | What it should become             |

The split is what keeps the repository runnable. The project contains no
placeholders and no engraft-specific syntax — only a template file sitting
beside it, which nothing at build or run time reads. Delete engraft entirely
and the project still works.

It also means one repository serves many customizations. Each consumer keeps
their own values file (and their own logo, their own colours) outside the
project; none of them need a fork.

## How an apply reads them

```
engraft apply --template engraft.template.yml --values engraft.values.yml
```

1. **Parse both files.** Both are YAML 1.2.
2. **Resolve variables.** Each variable declared in the template takes its
   value from the values file if present, and its `default` otherwise. See
   [Variables](variables.md).
3. **Run the customizations in order**, top to bottom, against a staging copy
   of the files they touch.
4. **Copy back** — but only if every action succeeded. See
   [Architecture](../architecture.md).

## Path resolution

Two different base directories are in play, and mixing them up is the most
common mistake:

| Path                                                        | Resolves against                             |
| ----------------------------------------------------------- | -------------------------------------------- |
| `file:` on a customization (the target)                     | The current working directory                |
| A variable holding a source path, as used by `file_replace` | The directory containing the **values file** |

Target paths follow the working directory because that is the project being
customized. Source paths follow the values file because they are the
consumer's assets, which travel with the consumer's values — not with the
project.

## Idempotence

Applying a template twice is safe, and applying it with new values over an
already-customized project produces the new values. Actions describe a
destination, not a delta: `json_replace` sets `$.name`, it does not search for
the previous name.

The one exception is `regex_replace`, whose pattern has to still match after
the first apply. A pattern that anchors on surrounding syntax rather than on
the old value — `PRIMARY_COLOR = "(?<value>[^"]*)"`, not
`PRIMARY_COLOR = "(?<value>#ff0000)"` — stays re-appliable. See
[regex_replace](../actions/regex-replace.md).

## Reference

- [Template file](template-file.md)
- [Values file](values-file.md)
- [Variables](variables.md)
