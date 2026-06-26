# Security &amp; privacy posture

This documents what the **front-end** already does, what your **host** must set,
and what a **backend** must implement before going live. It maps directly to the
security and privacy checklists in the brief.

## ✅ Already handled in this repo (front-end)

| Risk (from brief) | How it's addressed here |
|---|---|
| **API keys in front-end** | None. This is static HTML — there are no secrets, no `.env`, no source maps shipped. |
| **No input validation** | All forms validate required fields, email and phone formats client-side, mark `aria-invalid`, and use a **honeypot** anti-bot field. (Re-validate server-side too — see below.) |
| **Missing security headers** | `_headers`, `netlify.toml` and `.htaccess` set CSP, `X-Frame-Options: DENY`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy` and HSTS. |
| **Clickjacking / XSS** | Strict CSP (`script-src 'self'`, `frame-ancestors 'none'`, `object-src 'none'`). No inline event handlers. |
| **PII in URLs** | Forms use `POST` semantics (no PII in query strings); no personal data in links. |
| **No cookie consent** | GDPR/Canada-style banner; **no non-essential cookies set until the visitor accepts**. |
| **Payment card exposure / PCI** | The Pay-bill page is built to hand off to a **hosted** processor (Stripe/Square) — card data never touches this site. |
| **HTTPS** | `.htaccess` forces HTTPS; HSTS header set. Provision a TLS cert at your host (free on Netlify/Cloudflare/Vercel/Let's Encrypt). |

## 🔧 You must configure (host / deploy)

- **TLS certificate** — automatic on Netlify, Vercel, Cloudflare Pages; use Let's Encrypt on a VPS.
- **Reputable hosting with backups** — any of the above, or a managed host.
- **Apply the headers** — keep `_headers` / `netlify.toml` / `.htaccess` for your platform; verify with https://securityheaders.com.

## 🛠 Backend requirements before launch (forms, accounts, payments, CRM)

The interactive features here are **front-end demos**. When you wire a backend
(forms handler, booking/scheduling, customer accounts, payments, CRM), it must
implement — matching the brief's list:

- **Input validation & injection prevention** — validate/escape server-side; use parameterised queries / an ORM. Never trust the client.
- **Authentication & authorization** — hash passwords with **bcrypt/argon2**, enforce per-user **row-level access** (no IDOR), least-privilege roles.
- **Sessions & tokens** — secure, httpOnly, sameSite cookies; short token expiry + refresh; rotate on privilege change.
- **Secrets management** — API keys in server env vars / a secrets manager, never in the repo or front-end.
- **Rate limiting & abuse prevention** — throttle logins, bookings and payments; add CAPTCHA on suspicious traffic; the honeypot here is a first layer only.
- **Multi-tenancy / data isolation** — scope every query to the authenticated user/customer.
- **Idempotency** — idempotency keys on booking & payment endpoints so retries don't double-charge or double-book.
- **PII handling, retention & deletion** — encrypt at rest, documented retention, honour deletion requests (PIPEDA).
- **Audit trails** — tamper-evident logging of admin and payment actions.
- **Dependency scanning** — `npm audit` / Dependabot / Snyk; patch promptly.
- **Regulatory compliance** — PIPEDA (privacy), **CASL** (email consent + unsubscribe), PCI-DSS (via hosted payments).
- **Testing & resilience** — unit/integration/regression tests, load testing, a disaster-recovery/backup plan.

## Reporting

Found a vulnerability? Email **security@bluelineplumbing.ca** (replace with the
client's real address). Please allow reasonable time to remediate before disclosure.
