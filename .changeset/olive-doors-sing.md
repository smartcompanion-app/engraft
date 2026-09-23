---
"@smartcompanion/engraft": patch
---

`regex_replace` now rewrites the run captured by the `value` group rather than the first occurrence of that text within the match. A pattern like `version = "(?<value>[^"]*)"` against `const version = "version"` previously replaced the wrong `version`.
