# `regex_replace`

Replaces the part of a text file captured by a named group. Works on any text
file — source code, INI, TOML, `.env`, a shell script.

```yaml
- action: regex_replace
  file: src/theme.ts
  replace:
    - selector: '(PRIMARY_COLOR\s*=\s*)"(?<value>[^"]*)"'
      variable: primary_color
```

| Field                | Meaning                                          |
| -------------------- | ------------------------------------------------ |
| `file`               | The file, relative to the working directory      |
| `replace[].selector` | A regex containing a capture group named `value` |
| `replace[].variable` | The variable supplying the new value             |

## The `value` group

The pattern **must** contain a capture group named `value`, and only what that
group captures is replaced. Everything else in the match is context: it decides
_where_ to write, and is left exactly as it was.

```
selector:  (PRIMARY_COLOR\s*=\s*)"(?<value>[^"]*)"
file:      export const PRIMARY_COLOR = "#ff0000";
match:                  ───────────────────────────
value:                                    ───────
result:    export const PRIMARY_COLOR = "#0055ff";
```

Both naming syntaxes are accepted and mean the same thing:

- `(?<value>…)` — ECMAScript
- `(?P<value>…)` — Python

The Python form is supported because engraft's template format predates this
implementation and templates written against it are still valid. Prefer
`(?<value>…)` in new templates.

A pattern with no `value` group is an error, not a no-op.

## Every match is replaced

The pattern is applied globally: if it matches three times, all three
occurrences are rewritten. A pattern matching **nothing** is an error — the
apply aborts rather than reporting success on a file it did not change.

```
Pattern "(VERSION = \")(?<value>[^\"]*)\"" did not match anything in src/version.ts
```

That error is the main thing this action gives you over editing by hand: a
selector that stops matching, because the file was refactored, fails loudly on
the next apply instead of quietly doing nothing.

## Writing patterns that survive

Anchor the pattern on the **surrounding syntax**, not on the current value:

```yaml
# Good — still matches after the first apply
- selector: 'PRIMARY_COLOR\s*=\s*"(?<value>[^"]*)"'

# Bad — matches once, then never again
- selector: 'PRIMARY_COLOR\s*=\s*"(?<value>#ff0000)"'
```

The second form works the first time and then fails with "did not match
anything", because the value it anchors on is the value it just replaced.
Re-applying a template with new values is a normal thing to do; patterns have
to hold up to it.

A few more habits worth keeping:

- Use `[^"]*` rather than `.*` so the match stops at the closing quote.
- Include enough context to be unambiguous — `"(?<value>[^"]*)"` on its own
  matches every quoted string in the file.
- Quote the selector in YAML with single quotes, so backslashes reach the regex
  engine untouched.

## Examples

**A colour in TypeScript**

```yaml
- selector: '(PRIMARY_COLOR\s*=\s*)"(?<value>[^"]*)"'
  variable: primary_color
```

**An INI key**

```yaml
- selector: '^app_name\s*=\s*(?<value>.*)$'
  variable: app_name
```

**A bundle identifier in a Gradle file**

```yaml
- selector: 'applicationId\s+"(?<value>[^"]*)"'
  variable: android_application_id
```

**A number that has to stay a number**

`json_replace` writes strings; this does not:

```yaml
- selector: '"versionCode":\s*(?<value>\d+)'
  variable: version_code
```

## Errors

| Situation                         | Result                                      |
| --------------------------------- | ------------------------------------------- |
| The file does not exist           | Error; the apply aborts                     |
| The pattern has no `value` group  | Error naming the selector                   |
| The pattern matches nothing       | Error naming the selector and the file      |
| The pattern matches several times | Every occurrence is replaced                |
| The variable resolved to nothing  | The entry is skipped; the file is untouched |

## When to use something else

`regex_replace` is the escape hatch, and it is blind to structure. For JSON,
[`json_replace`](json-replace.md) addresses `$.a.b` regardless of formatting;
for HTML, [`html_replace`](html-replace.md) tells you when a selector has
become ambiguous. Both survive reformatting that would break a regex.
