# Security & privacy

This repository ships a **static front-end** that is secure by default. The
items below marked _front-end done_ are live in this codebase; the rest are the
**backend checklist** to complete before the dashboard, payments, and customer
data go to production.

## Front-end posture (done here)

- **No secrets in the frontend.** No API keys, tokens, or credentials are
  committed or inlined. The login/portal forms are demo-only.
- **No source-map leakage.** No build step emits source maps; CSS/JS are
  hand-written and inlined.
- **Strict CSP + security headers** for the major hosts: `_headers` (Netlify/
  Cloudflare Pages), `netlify.toml`, and `.htaccess` (Apache). Includes
  `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options:
  nosniff`, `Referrer-Policy`, `Permissions-Policy`, and HSTS.
- **Force HTTPS** via `.htaccess` redirect + `upgrade-insecure-requests` in CSP.
- **Forms:** client-side validation, a honeypot field, and CASL consent
  checkboxes with an unsubscribe commitment. Server-side validation is required
  (below).
- **Payments:** the Pay page is a hosted-checkout posture only — no card fields
  on-site, no card data ever touches our origin (PCI SAQ-A).
- **`/admin/*` and staff pages excluded** from `sitemap.xml` and `robots.txt`.
- **Accessibility & privacy:** essential-only cookies until consent; no
  third-party trackers loaded before consent.

## Backend checklist (to build)

| Area | Requirement |
|------|-------------|
| **Authentication** | Argon2/bcrypt password hashing; secure, httpOnly, SameSite session cookies; login rate-limiting + lockout; password reset via signed expiring tokens. |
| **Authorization** | Role-based access (Technician/Office/Admin) enforced server-side. Row-level access on every record — no IDOR (never trust client-supplied IDs). |
| **Sessions & tokens** | Short-lived sessions, idle + absolute timeout, rotation on privilege change, revoke on sign-out. |
| **Idempotency** | Idempotency keys on booking/payment POSTs to prevent double-charges and duplicate jobs. |
| **Injection prevention** | Parameterised queries / ORM only; output-encode all user content; validate + sanitise every input server-side. |
| **Rate limiting & abuse** | Per-IP and per-account limits on forms, login, and payment endpoints; CAPTCHA (hCaptcha/Turnstile) on public forms. |
| **Secrets management** | Secrets in a vault / platform env vars, never in the repo; rotate regularly. |
| **Multi-tenancy / isolation** | Scope every query to the owning customer/tenant; deny-by-default. |
| **PII handling** | Encrypt at rest + in transit; documented retention + deletion (PIPEDA access/correction/erasure requests honoured). |
| **Compliance** | PIPEDA (privacy), CASL (consent + unsubscribe on every commercial email), PCI SAQ-A (hosted checkout only). |
| **Audit logging** | Append-only logs for auth events, record access, payments, and admin changes. |
| **Dependency scanning** | Automated SCA (e.g. Dependabot / npm audit / pip-audit) in CI. |
| **Async / queues** | Offload email, invoicing sync, and heavy work to a queue; avoid N+1 queries on list views. |
| **Testing** | Unit + integration tests on auth, authz, and payment paths before release. |
| **Disaster recovery** | Automated encrypted backups, tested restore runbook, defined RTO/RPO. |

## Reporting

Report security issues privately to **security@bluelineplumbing.ca**
(placeholder). Do not open public issues for vulnerabilities.
