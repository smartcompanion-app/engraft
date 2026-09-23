# Security Policy

## Supported versions

Security fixes land in the **latest published version** and are not backported.
If you are on an older one, upgrading is the fix. The current version is
whatever [`@smartcompanion/engraft`](https://www.npmjs.com/package/@smartcompanion/engraft)
shows on npm — deliberately not restated here, so this page cannot fall out of
date.

Every release is published from CI over
[npm trusted publishing](https://docs.npmjs.com/trusted-publishers), so each
tarball carries a provenance attestation linking it to the commit and workflow
that built it. You can check it with:

```shell
npm audit signatures
```

## What engraft does to your files

Worth knowing before you report something as a vulnerability, because some of
it is by design:

- `engraft apply` **writes to the current working directory**. Template `file:`
  paths resolve against it; `file_replace` source paths resolve against the
  directory holding the values file.
- A template is **executable configuration in the sense that it decides which
  files get rewritten**, but it is not code: engraft never evaluates anything
  from a template or values file. `regex_replace` compiles a pattern, which can
  be made to backtrack pathologically on hostile input.
- Applying a template from an untrusted source is roughly as risky as running
  any other tool that edits files in your repository. Read it first.

## Reporting a vulnerability

Please do not open a public issue for security problems.

Report them through
[GitHub's private vulnerability reporting](https://github.com/smartcompanion-app/engraft/security/advisories/new),
or by email to <hello@smartcompanion.app>.

Include the engraft version, and enough detail to reproduce the issue — ideally
a template, a values file and a target file. You can expect an initial response
within a week.
