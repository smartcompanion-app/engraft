---
"@smartcompanion/engraft": patch
---

Updated to js-yaml 5, jsdom 30 and commander 15. This raises the supported Node versions to 22.22.2+, 24.15+ or 26+, matching jsdom's own floor. A template or values file containing more than one YAML document is now rejected with a message saying so, instead of silently using the first.
