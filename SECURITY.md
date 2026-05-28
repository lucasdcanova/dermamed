# Security Policy

> **DermaMed is a paused research prototype, not a medical device, and not a
> production service.** It has no users, no patients, no PHI, no clinical
> deployment. There is no on-call rotation and no SLA. This policy exists so
> that anyone who finds a real issue has a clear path to report it
> responsibly.

## Scope

This policy covers the code in this repository (`backend/`, `frontend/`,
`docker-compose.yml`, `docs/`). It does **not** cover:

- The underlying model (`google/medgemma-4b-it`) — report model issues to
  Google via the Hugging Face model card.
- The Hugging Face Inference API, Neon, or any other third-party service.
- Forks or downstream derivatives.

## Do NOT use in patient care

DermaMed is **not** cleared, registered, or authorized for clinical use in any
jurisdiction. See [`docs/DISCLAIMER.md`](docs/DISCLAIMER.md) and
[`docs/REGULATORY_POSITION.md`](docs/REGULATORY_POSITION.md).

If you have deployed this code in a clinical environment: **stop**. That use
is outside the scope of this repository and is the deploying party's
regulatory responsibility, not the author's. Reporting "it gave a wrong
diagnosis" is not a security issue here — the repository explicitly states it
is not for diagnosis.

## What to report

Please report:

1. **Leaked secrets** — credentials, tokens, database URLs, or signing keys
   present in current `HEAD`, in git history, in releases, or in CI logs.
2. **Authentication or authorization defects** — JWT handling bugs, scope
   escalation, route protection bypasses.
3. **Injection or RCE paths** — SQLi, command injection, deserialization,
   SSRF (especially against the Hugging Face Inference endpoint),
   path-traversal in image upload.
4. **Sensitive data leakage** — accidental commit of test images, log files
   containing user content, or error responses that echo internal state.
5. **Dependency vulnerabilities** with a demonstrated exploit path against
   this code (not just a transitive CVE).

Please **do not** report:

- Theoretical clinical-safety issues with the model output. Those are
  documented limitations, not vulnerabilities — see the disclaimer.
- The fact that `backend/.env` once contained credentials in git history.
  That is documented and being rotated; see the README and disclaimer.
- The fact that the prototype does not implement HIPAA / GDPR / LGPD
  controls. That is by design and stated in the disclaimer.

## How to report

Email: open a private email to the address listed on the author's portfolio
(<https://www.lucascanova.com.br/portfolio>), with subject prefix
`[security][DermaMed]`.

Please include:

- Affected file(s) and commit SHA.
- Reproduction steps or a minimal proof of concept.
- Suggested fix, if you have one.

If GitHub Security Advisories are enabled on the repository, you may also use
the "Report a vulnerability" link there.

## Response expectations

This is a paused side project, not a funded product.

- Acknowledgement: best-effort, typically within 14 days.
- Triage and fix: best-effort. There is no guaranteed timeline.
- For trivially-rotatable secrets (leaked tokens), the response is to
  invalidate the credential upstream; the git history is not rewritten in
  most cases (the credential is dead, not the commit).

## Disclosure

Coordinated disclosure preferred. If a fix or invalidation can be applied
within 90 days of the report, please hold public disclosure until then. If
the issue is already public (e.g. a leaked token in a public commit), there
is nothing to coordinate — please flag it directly so it can be invalidated.

## Acknowledgements

Reporters who follow this policy in good faith will be credited in the
repository (with permission) and, where applicable, in the commit or release
notes that address the issue.
