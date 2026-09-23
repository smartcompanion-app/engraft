# `html_replace`

Sets element text or attribute values in an HTML file, addressed by XPath.

```yaml
- action: html_replace
  file: public/index.html
  replace:
    - selector: //title
      variable: page_title
    - selector: //meta[@name='description']/@content
      variable: page_description
```

| Field                | Meaning                                             |
| -------------------- | --------------------------------------------------- |
| `file`               | The HTML file, relative to the working directory    |
| `replace[].selector` | XPath expression selecting one element or attribute |
| `replace[].variable` | The variable supplying the new value                |

## Selectors

The document is parsed as HTML and queried with XPath.

**Element text** — the selector resolves to an element, and its text content is
replaced:

| Selector           | Sets the text of                  |
| ------------------ | --------------------------------- |
| `//title`          | `<title>`                         |
| `//h1[@id='main']` | `<h1 id="main">`                  |
| `//header/h1`      | The `h1` directly inside `header` |

**Attributes** — end the selector with `/@name`:

| Selector                               | Sets                             |
| -------------------------------------- | -------------------------------- |
| `//html/@lang`                         | The `lang` attribute on `<html>` |
| `//meta[@name='description']/@content` | That meta tag's `content`        |
| `//link[@rel='icon']/@href`            | The favicon path                 |

Use single quotes inside the selector so the YAML stays unquoted, or quote the
whole selector and use double quotes inside.

Tag names are matched in lowercase, as the HTML parser normalises them.

## Exactly one match

A selector **must** match exactly one node. Zero matches is an error, and so is
two or more:

```
XPath selector "//p" matched 3 elements in index.html, expected exactly 1
```

This is the point of the action. A selector that silently matched nothing would
turn a typo, or a page that has since been restructured, into an apply that
reports success and changes nothing. Being told the page has three `<p>`
elements is more useful than editing an arbitrary one.

To target one of several similar elements, narrow the XPath with a predicate:

```yaml
- selector: //meta[@property='og:title']/@content
- selector: //div[@id='footer']/p[1]
```

## Example

```html
<!doctype html>
<html lang="en">
  <head>
    <title>Default App</title>
    <meta name="description" content="A default application" />
  </head>
  <body>
    <h1 id="main">Welcome</h1>
  </body>
</html>
```

```yaml
- action: html_replace
  file: index.html
  replace:
    - selector: //title
      variable: page_title
    - selector: //meta[@name='description']/@content
      variable: page_description
    - selector: //html/@lang
      variable: lang
```

```yaml
page_title: Acme Portal
page_description: The Acme customer portal
lang: de
```

```html
<!doctype html>
<html lang="de">
  <head>
    <title>Acme Portal</title>
    <meta name="description" content="The Acme customer portal" />
  </head>
  <body>
    <h1 id="main">Welcome</h1>
  </body>
</html>
```

## Text replacement replaces everything inside

Setting an element's text content discards its children. On
`<h1>Hello <em>there</em></h1>`, a selector of `//h1` leaves `<h1>NewText</h1>`
— the `<em>` is gone.

That is usually right for the elements worth customizing (`<title>`, a heading,
a tagline). When it is not, target the inner element instead, or use
[`regex_replace`](regex-replace.md).

## Formatting

The document is parsed and re-serialised. A leading `<!DOCTYPE html>` is
detected and written back at the top, and void elements stay unclosed in HTML
style. Whitespace and indentation elsewhere follow the parser's serialisation,
so expect a first apply to reformat the file somewhat.

Since the whole document round-trips, run engraft once on an untouched page and
commit that normalisation separately from the actual customization — otherwise
the two are tangled in one diff.

## Errors

| Situation                                                                      | Result                                        |
| ------------------------------------------------------------------------------ | --------------------------------------------- |
| The file does not exist                                                        | Error; the apply aborts                       |
| The selector matches no node                                                   | Error naming the selector and the file        |
| The selector matches more than one node                                        | Error naming the selector and the match count |
| The selector resolves to something that is neither an element nor an attribute | Error                                         |
| The variable resolved to nothing                                               | The entry is skipped; the file is untouched   |
