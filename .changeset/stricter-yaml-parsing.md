---
"@smartcompanion/engraft": patch
---

Update js-yaml to 5.5.0 and jsdom to 30.1.3. js-yaml now follows the YAML spec more strictly: an unquoted value that starts with `,`, `]` or `}` is rejected instead of being read as text. If a template or values file relied on that, quote the value.
