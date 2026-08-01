# Ghosh Designs — plumbing outreach

Cold email that leads with a homepage mockup carrying the prospect's **own**
business name, city and phone number. Targets Canadian plumbing companies that
are big enough to afford a site and currently have a bad one — or none.

Built to send ~50/day from `srijan.ghosh201107@gmail.com` without torching the
account.

---

## How it works

1. **Import** a CSV of plumbing companies.
2. **Audit** each one's current website — is it mobile-hostile, insecure, dead,
   stale, or missing entirely? This produces a 0–100 "needs a site" score *and*
   one true sentence about their specific site that goes in the email.
3. **Mockup** — screenshot the demo template with their name in the nav, their
   city in the headline, their number in the CTA. Optimized to ~110 KB.
4. **Send** — sequence of 4 emails, warm-up ramped, paced, business hours only.
5. **Replies** — anyone who writes back drops out of the sequence immediately.

The mockup is the whole pitch. A generic template gets ignored; the same design
with *their* name on it gets replies.

## Setup

```bash
pip install -r requirements.txt
playwright install chromium
python3 src/cli.py fetch-template        # downloads the demo site locally
cp .env.example .env                     # then add your Gmail App Password
python3 src/cli.py doctor                # tells you what's still missing
```

`doctor` checks dependencies, the browser, config placeholders, the template
and your credentials, and prints the fix for anything broken. `doctor --network`
also attempts a real SMTP login, which is the fastest way to find out an App
Password was pasted wrong. Run it before the first send and any time something
behaves oddly.

Edit `config.toml` — `mailing_address`, `phone`, `demo_link`, `booking_link`,
`website`. `send` **refuses to run** while any of them still says `TODO`;
`--dry-run` still works so you can read the copy first.

`mockups` serves the demo template itself on a random free port — set
`[template] dir` to the folder containing the built site's `index.html`.
No second terminal, which is what makes cron possible.

## Daily run

```bash
python3 src/cli.py import leads.csv   # whenever you have new prospects
python3 src/cli.py daily --dry-run    # read the copy, send nothing
python3 src/cli.py daily              # audit + mockups + replies + send
python3 src/cli.py status
```

`daily` is the whole loop. It processes replies *before* sending, so anyone who
wrote back overnight drops out instead of getting the next step anyway. A
screenshot or IMAP failure is logged and skipped; a send failure stops the run.

Individual steps (`audit`, `mockups`, `replies`, `send`, `suppress`) still exist
for when something needs poking at by hand.

`send` refuses to run outside the configured window, and while any config value
still says `TODO`. `--dry-run` prints the exact emails and sends nothing.

## Automating it

The pipeline is a plain CLI, so scheduling is the OS's job.

**macOS / Linux** — `crontab -e`, then one line. Twice on each sending day,
inside the window, so a run that finds nothing due gets a second chance:

```cron
0 9,14 * * 2,3,4  /full/path/to/outreach/run-daily.sh
```

`run-daily.sh` handles cron's minimal PATH and appends to `logs/daily-<date>.log`.
On macOS, Terminal (or `cron`) needs Full Disk Access or the job dies silently.

**Windows** — Task Scheduler, "Start a program": `python3`, arguments
`src/cli.py daily`, "Start in" set to the `outreach` folder.

### Or: GitHub Actions (no laptop required)

`.github/workflows/outreach.yml` runs the whole thing on GitHub's machines on
the same Tue/Wed/Thu schedule, so nothing depends on your computer being awake.

**The repository must be private first.** The campaign database holds prospects'
names and email addresses, and the workflow commits it back so state survives
between runs. On a public repo that publishes their contact details. The
workflow checks this itself and refuses to run until you flip it — Settings →
General → Danger Zone → Change visibility.

Then: Settings → Secrets and variables → Actions → New repository secret,
named `GMAIL_APP_PASSWORD`.

Test it before trusting it: Actions → outreach → Run workflow, leaving
"Print the emails without sending" ticked. That runs the full pipeline and
prints the emails without sending any. Untick it when you're ready.

Two things to get right before you automate:

1. **Run it by hand for the first week.** The ramp is at 5/day then, so it costs
   almost nothing to watch — and the first time you see the real copy go to a
   real plumber is the time to change your mind about it, not after 200 sends.
2. **This machine has to be awake.** Cron does not run on a sleeping laptop.
   If that is a problem, a $5/month VPS or a Raspberry Pi is the fix — the whole
   pipeline is stdlib plus Playwright.

`daily` is safe to run more often than needed: the daily cap, the ramp and the
send window all gate it independently, so an extra invocation sends nothing.

## Lead CSV

```
business,contact_name,email,domain,phone,city,province,review_count
```

`domain` blank means "no website" — those are your best leads, and the audit
scores them highest. `review_count` (from their Google listing) is the
size proxy; `contact_name` blank falls back to "Hi there".

Qualification bars live in `config.toml [qualifying]`: default is audit score
≥ 40 **and** ≥ 15 reviews.

### Where to find leads

Google Maps for `plumber <town>`, across Canadian towns of 10k–150k. The ones
with 40+ reviews and either no website link or a visibly bad one are the list.
Small towns outperform cities: less competition, and the incumbent sites are
older. Get the owner's name off the listing or the site's About page — a real
first name measurably outperforms "there".

## Sending limits, honestly

`daily_cap = 50` is what you asked for, and the config ships with a warm-up ramp
that starts at **5/day** and reaches 50 around week three. Do not skip it. Gmail
does not warn you before it starts filtering; you find out from silence, and a
burned sending reputation is not something you can undo by slowing down later.

A free Gmail account also has a hard ~500 recipients/day limit, so 50 is fine on
paper — the risk is reputational, not numeric. If this starts working, move to a
dedicated domain with SPF/DKIM/DMARC and keep this inbox for replies.

## Trust

Cold email from an unknown name is a trust problem before it's a design problem.
Three things in the copy carry it, and all three are verifiable rather than
claimed:

- **A clickable demo.** `demo_link` turns "some guy emailed me" into "I just
  used a site he built". It is the strongest signal in the message.

  **Host it on your own domain.** Not the `github.io` URL. That URL contains
  the word "Templates", which contradicts an email saying you put a homepage
  together for them — a prospect clocks that without having to steal anything.
  The repo behind it is also public, so the whole project is cloneable.

  On copying generally: every website's front end is copyable and always has
  been. A plumber who can deploy a Next.js export was never going to pay you.
  What you sell is the build, their content and photos, hosting, the Google
  Business Profile wiring, and someone to call when the quote form breaks.
  Showing work is the job — just don't hand over the repo name while you do it.
- **Local.** "I'm based in Regina, SK" plus a real phone number. A tradesperson
  who can phone you is far likelier to believe you exist.
- **Risk reversal.** "You don't pay anything until the site is live and you're
  happy with it." Change this in `templates/step1_preview.txt` if your terms
  differ — it is a commercial promise, so it should be one you'll honour.

Deliberately absent: testimonials, client counts, logos, "trusted by N
businesses". Invented social proof is the fastest way to lose a deal on the
call, and it is trivially checkable. Once you have real clients, a single named
one with a link beats all of it.

## Legal — read this once

Canada is under **CASL**, which is stricter than US CAN-SPAM. Cold B2B email is
legal here under *implied consent*: you may email a business address that is
**conspicuously published** (on their website, their Google listing) without a
statement refusing unsolicited mail, and your message must be **relevant to
their role**. A plumbing company's published `info@` address, emailed about
their website, fits.

What is required in every message — all three are already wired in:

- **Sender identification** — name and company, in the footer.
- **A real mailing address.** `config.toml` ships with a `TODO` placeholder.
  Replace it. A PO box works.
- **A working unsubscribe**, honoured within 10 business days and valid for 60
  days. `replies` auto-suppresses anyone whose subject says stop/remove/
  unsubscribe, and `List-Unsubscribe` is set on every message.

Penalties are real (up to $1M for an individual), and they are levied for
ignoring unsubscribes far more often than for the first email. The suppression
list is the part to never break: `src/cli.py suppress <email>` is permanent, and
`import` silently drops anyone on it.

Two things this does not do, deliberately: no tracking pixels and no link
shorteners. Both hurt deliverability more than the open-rate data is worth.

## Layout

```
config.toml            all tuning: caps, ramp, window, sequence, bars
templates/step*.txt    the four emails — edit these freely
src/cli.py             commands
src/audit.py           site scoring + the personalized audit sentence
src/personalize.py     stamps the prospect's details into the demo
src/shoot.py           Playwright capture + email image optimization
src/render.py          templating + MIME assembly
src/send.py            SMTP, warm-up ramp, window, pacing
src/db.py              SQLite state + suppression
data/campaign.db       created on first run (gitignored)
```

## Notes for future me

- `src/shoot.py` never calls `img.decode()`. On a `loading="lazy"` image that is
  off-screen it never settles and hangs the capture forever.
- Personalization edits the **live DOM after hydration**. Rewriting the static
  HTML desyncs React and the page screenshots as a blank white rectangle.
- The demo banner is removed by matching `[role="note"]` only — a broader
  selector also matches the `<header>` wrapping it and deletes the whole nav.
