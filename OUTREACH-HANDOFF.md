# Ghosh Designs — Outreach Handoff

**Owner:** Srijan Ghosh — Ghosh Designs, Regina SK
**Written:** 2026-09-04 (Regina time)
**Purpose:** Complete state of the cold-outreach operation. Written so that a
person or an AI session with zero prior context can pick this up and keep going
without re-deriving anything.

---

## 0. Read this first — the five things that matter right now

| # | Item | Status | Deadline |
|---|---|---|---|
| 1 | **Greg at Rusty Pipes replied on Sept 1. Nobody has read it.** | Unread, 4 days old | Now |
| 2 | **Step 4 email says "before September". It is September.** 13 leads get this Monday | False copy, unfixed | Before Mon 07:23 |
| 3 | **The whole email list finishes Monday/Tuesday.** After that, zero emails | Fuel running out | Mon–Tue |
| 4 | **20 of 21 SMS leads never texted** | Not started | Ongoing |
| 5 | **~40 phone numbers, nobody has ever been called** | Not started | Ongoing |

Results to date: **~218 emails sent, 3 replies, 0 clients.**
Two replies were rejections. One (Greg) is unread and is the only live thread
in the entire operation.

---

# SECTION 1 — THE EMAIL AUTOMATION

## 1.1 What it is

A Python program that runs on GitHub Actions four times each weekday morning.
For each plumbing company in a database it:

1. Screenshots a homepage mockup built for that specific company
2. Emails it to them with a short personal note
3. Follows up four more times over ~16 days
4. Watches the inbox over IMAP and drops anyone who replies
5. Commits the updated database back to the repo so the next run knows what happened

Nothing depends on a laptop being awake. It runs whether or not anyone opens it.

## 1.2 Where everything lives

| Repo | Branch | What it is |
|---|---|---|
| `srijanghosh072011-lgtm/email-automation-` | `main` | The engine. Code, config, templates, lead DB |
| `srijanghosh072011-lgtm/plumbing-Templates-` | `claude/site-replica-seo-aeo-phglx9` | The demo site. Built output in `docs/` |
| `srijanghosh072011-lgtm/idk` | `gh-pages` | The agency site, ghoshdesigns.ca |
| `srijanghosh072011-lgtm/locking-in-` | `claude/email-automation-leads-prgapc` | This handoff |

**The `email-automation-` repo must stay private.** Every workflow has a guard
step called *"Refuse to run while this repository is public"* that hard-fails
the run if it ever goes public. The repo contains the lead database and the
mockup images.

### Repo layout

```
email-automation-/
├── build_leads.py                  # one-off lead builder
├── .github/workflows/
│   ├── outreach.yml                # the scheduled campaign
│   ├── offer.yml                   # manual one-off sends
│   └── find-leads.yml              # manual Google Places scraper
└── outreach/
    ├── config.toml                 # everything tunable, committed, no secrets
    ├── leads.csv                   # input list
    ├── data/campaign.db            # SQLite state, committed after every run
    ├── mockups/                    # 62 generated .jpg screenshots
    ├── templates/                  # the six email bodies
    ├── vendor/plumbing-template/   # fetched demo site, screenshotted against
    └── src/
        ├── cli.py         (797 lines)  command surface + orchestration
        ├── audit.py       (241)        scores their existing site
        ├── db.py          (151)        SQLite + suppression
        ├── personalize.py  (98)        name/company token handling
        ├── places.py      (111)        Google Places lookup
        ├── render.py      (203)        template -> MIME message
        ├── send.py         (67)        SMTP connection
        ├── serve.py        (65)        local static server for screenshots
        └── shoot.py       (179)        Playwright screenshot + Pillow optimize
```

Python 3.11, standard library wherever possible (`tomllib`, `sqlite3`,
`smtplib`, `imaplib`, `zoneinfo`). The only third-party dependencies are
Playwright (screenshots) and Pillow (image optimization).

## 1.3 Identity and infrastructure

| Thing | Value |
|---|---|
| From | `srijan@ghoshdesigns.ca` |
| Reply-To | `srijan.ghosh072011@gmail.com` |
| Bcc (silent, on every send) | `srijan.ghosh072011@gmail.com` |
| SMTP | `smtp-relay.brevo.com:587`, user `b424bf001@smtp-brevo.com` |
| SMTP password | GitHub Actions secret `SMTP_PASSWORD` — **not in the container** |
| IMAP | `imap.gmail.com`, user `srijan.ghosh072011@gmail.com` |
| IMAP password | Actions secret `IMAP_PASSWORD` |
| Phone in emails | (639) 777-1017 |
| Mailing address (CASL) | 2812 25th Ave, Regina, SK S4S 1K6 |
| Demo link | https://demo.ghoshdesigns.ca |
| Agency site | https://ghoshdesigns.ca |
| GA4 measurement ID | `G-LQPHPNP2QT` |

**Why Brevo and not Gmail:** Gmail SMTP is routinely blocked from datacenter
IPs like GitHub Actions runners, and it reports that block as
`BadCredentials` — indistinguishable from a wrong password. Brevo is a
transactional relay built for exactly this.

**Why the split between From and Reply-To:** the From address is on the
authenticated domain so SPF/DKIM/DMARC align and the mail lands. Replies go to
the Gmail inbox that actually gets read.

**Sending is plain text.** `plain_text_only = true`, `list_unsubscribe_header
= false`. Inline images + HTML + a List-Unsubscribe header together are what
push cold mail into Gmail's Promotions tab. The mockup goes as an attachment.

**A note on the preflight warning:** the check step prints
`[XX] app password looks like 16 chars — got 90`. This is a false alarm. That
check was written for Gmail App Passwords, which are 16 characters. Brevo SMTP
keys are long. It does not block the run and can be ignored.

## 1.4 The sequence

Five steps. Delays are days since the previous step to that lead.

| Step | Template | Delay | Subject |
|---|---|---|---|
| 1 | `step1_preview` | 0 | made you a homepage for {business} |
| 2 | `step2_bump` | 3 | re: made you a homepage for {business} |
| 3 | `step3_proof` | 4 | three things worth checking on your site |
| 4 | `step4_price` | 4 | what it actually costs |
| 5 | `step5_close` | 5 | last one from me |

**Step 4 is deliberately before step 5.** Step 5 promises to stop emailing, so
nothing may follow it. Price had to come first — nobody had ever been told what
this costs, and silence on price is a common reason a warm prospect goes quiet.

There is a sixth template, `offer_free`, which is **not** part of the sequence.
It is sent manually via `offer.yml`.

### Template tokens

`{{first_name}}`, `{{business}}`, `{{sender_email}}`, `{{website}}`,
`{{demo_link?}}`, `{{audit_line?}}`. A token ending in `?` makes its whole line
vanish when the value is empty — that is why leads with no audit finding do not
get a blank gap.

`{{audit_line}}` is generated per-lead from the site audit. Example for a lead
with no website: *"You don't have a website yet, so every search for a plumber
around here sends that job to someone else."*

### Full template text

Reproduced exactly so this document survives the repo.

---

**`step1_preview.txt`**

```
Subject: made you a homepage for {{business}}
---
Hey {{first_name}},

I made a homepage for {{business}}. It's attached.

{{audit_line?}}

Figured it'd be easier to build one and show you than to email asking if you
wanted one.

The wording on it is placeholder, the layout is the real part. If you want it
for real I can have it live in a couple of days, and you don't pay until it's
up and you're happy with it.

Here's a finished one you can click around: {{demo_link?}}

Want me to build yours out?

Srijan
Ghosh Designs, Regina SK
{{sender_email}}
{{website}}
```

**`step2_bump.txt`**

```
Subject: re: made you a homepage for {{business}}
---
Hey {{first_name}},

Following up once on the homepage I made for {{business}}.
Still sitting in my folder.

Is it that you don't need a site, or just that it's never made it to the top
of the list? Either's fine, I only ask because I don't want to keep bugging
you if it's the first one.

Srijan
Ghosh Designs, Regina SK
{{sender_email}}
{{website}}
```

**`step3_proof.txt`**

```
Subject: three things worth checking on your site
---
Hey {{first_name}},

Last one about the site. Something useful either way.

Most plumbing sites I look at lose calls in the same three places. The phone
number isn't tappable on a phone, so people give up. There's nothing about
emergency or 24 hour work near the top, so the urgent jobs go to whoever says
it first. And there are no pages for the towns nearby, so you never come up
in those searches.

Worth checking against, if you've got a site. Worth insisting on, if you ever
get one built. Either way it's useful to know, whether or not you ever reply
to me.

Srijan
Ghosh Designs, Regina SK
{{sender_email}}
{{website}}
```

**`step4_price.txt`** — ⚠️ contains the stale "before September" line

```
Subject: what it actually costs

---
Hey {{first_name}},

I never told you what this costs, which might be the reason you haven't
replied.

$1,500 to build it. $250 a month after that covers hosting and any changes you
want, done the same day you ask. You don't pay the $1,500 until the site is
live and you're happy with it.

I can take a few more on before September, then I get slower.

The homepage for {{business}} is still sitting here if you want it.

Srijan
Ghosh Designs, Regina SK
{{sender_email}}
{{website}}
```

**`step5_close.txt`**

```
Subject: last one from me
---
Hey {{first_name}},

I've emailed a few times about a site for {{business}}
and haven't heard back, which is a fine answer. You're busy.

I'll leave it there. Not going to keep emailing you.

If it ever comes up, slow winter or a competitor turning up above you in
searches, just reply to this one.

Good luck out there.

Srijan
Ghosh Designs, Regina SK
{{sender_email}}
{{website}}
```

**`offer_free.txt`** — ⚠️ also contains the stale "before September" line

```
Subject: free one

---
Hey {{first_name}},

Bit of a different offer.

I'm building my portfolio and I'm doing one plumbing site completely free
before September. No charge, no catch. I just need a real company in it that
I can show people.

I already made the homepage for {{business}}, so you'd be the quickest one for
me to finish.

First person to say yes gets it. Reply and I'll start today.

Srijan
Ghosh Designs, Regina SK
{{sender_email}}
{{website}}
```

## 1.5 Voice rules — these were fought for, do not undo them

These came from repeated, specific corrections. Anyone editing the copy must
hold them.

1. **No em dashes. Anywhere.** Verified 0 across all six templates. They read
   as AI-written. They were stripped twice, because they got reintroduced once.
2. **No invented scenarios.** An earlier draft had a line about "it's 9 p.m.
   and someone's calling..." It was cut outright. *"No one really says that."*
3. **Never claim it takes weeks.** A build is one to two days at most. An
   earlier draft said "two weeks" — that number was invented and wrong.
4. **Don't argue against the product.** A line reading "plenty of people never
   needed a website" was removed. It talked the prospect out of buying.
5. **Never claim something untrue about their site.** Step 3 originally said
   "worth checking yours against that" — sent to 12 businesses that have no
   website at all. Now reads *"Worth checking against, if you've got a site.
   Worth insisting on, if you ever get one built."*
6. **Contact info in every email.** Name, company, city, email, website.
7. **Watch the line wrap.** Long business names blew past the wrap at 102
   characters. Line breaks were moved to sit after `{{business}}`. Worst case
   is now 85 characters.
8. **Watch punctuation against tokens.** `{{business}}` values ending in "Inc."
   produced `Inc..` — the sentence was restructured so no period follows the token.

## 1.6 Pricing

| | Build | Monthly |
|---|---|---|
| Old | $2,500 | $450 |
| **Current** | **$1,500** | **$250** |

Payment terms: nothing owed until the site is live and they are happy with it.

**What the $250/month covers:** hosting, and any changes they want, done the
same day they ask.

**What it does NOT cover** — corrected explicitly, do not re-add:
- No monthly report
- No Google Business Profile management

ghoshdesigns.ca was updated to match. "Live in days, not months" replaced the
old timeline claim in 16 places.

## 1.7 The workflows

### `outreach.yml` — the scheduled campaign

```yaml
on:
  schedule:
    - cron: "23 13 * * 1-5"   # 07:23 Regina
    - cron: "23 15 * * 1-5"   # 09:23 Regina
    - cron: "23 17 * * 1-5"   # 11:23 Regina
    - cron: "23 19 * * 1-5"   # 13:23 Regina
  workflow_dispatch:
    inputs: { dry_run, ignore_window }
concurrency:
  group: outreach
  cancel-in-progress: false
```

**Why four runs and why never on the hour.** GitHub delays scheduled runs under
load, and the top of the hour is the most congested minute. One run once slipped
5h36m and landed at 18:36 Regina, outside the send window, sending nothing.
Extra runs cost nothing because the daily cap means the second run of a day
sends zero.

Saskatchewan does not observe DST, so UTC-6 holds year round and the cron never
needs seasonal adjustment.

Steps: checkout (`ref: main`) → public-repo guard → setup-python → install →
fetch demo template → preflight check → `cli.py daily` → `cli.py status` →
persist state (commit + rebase-retry push).

### `offer.yml` — manual one-off sends

`workflow_dispatch` with `template`, `to`, `dry_run` inputs. No Playwright, no
campaign run, no state commit. Same concurrency group so it cannot collide with
the schedule.

**It exists because `SMTP_PASSWORD` only lives as an Actions secret.** Sending
from a dev container is impossible — it fails with `RuntimeError: No SMTP
password`. All manual sends must go through a runner.

**Consequence, and it is a real gap:** because it writes no state, the sends
are invisible to the database. See §1.10.

### `find-leads.yml` — manual lead scraper

Runs the `[places]` queries against the `[places]` cities via the Google Places
API (New), keeps whatever clears `min_review_count`, looks up each one's
published email, and commits to `leads.csv`. The scheduled campaign picks it up
on its own. Needs the `GOOGLE_PLACES_API_KEY` secret.

Currently configured for Saskatchewan cities only: Regina, Moose Jaw, Swift
Current, Yorkton, Prince Albert, North Battleford, Estevan, Weyburn.

## 1.8 Sending controls

```toml
daily_cap        = 50
warmup           = [5,5,8,8,12,15,18,22,26,30,34,38,42,46,50]
min_gap_seconds  = 30
max_gap_seconds  = 90
timezone          = "America/Regina"
send_window_start = 7
send_window_end   = 18
send_days         = [1,2,3,4,5]   # weekdays only
```

The warm-up ramp indexes on *sending days*, not calendar days. 13 sending days
have elapsed, so the current allowance is 46/day, reaching the 50 cap on day 15.

**The gaps used to be 240–900 seconds and that is what broke the campaign.**
See §1.9.

**Qualifying bars** are both effectively off: `min_audit_score = 0`,
`min_review_count = 0`. The offer is "I made you a homepage," which stands up
whether or not their current site is bad, and the audit sentence only appears
when there is something true to say. The research sheet is the size filter now.

## 1.9 Every bug found and fixed

This is the most valuable part of this document. Each of these cost real sends.

### SMTPServerDisconnected on the second send of every run

**Symptom:** every run mailed exactly one lead, then crashed. Runs #22, #23, #24.

**Cause:** one SMTP connection was opened and held across the pacing sleep. The
gap was 4–15 minutes at the time. SMTP servers hang up idle sessions long
before that, so the connection was dead by the second `send_message`.

**Fix** — one connection per message, in `cli.py`:

```python
else:
    # One connection per message, deliberately. The pacing gap below is
    # 4-15 minutes and SMTP servers hang up on idle sessions long before
    # that, so a connection held open across the sleep died with
    # SMTPServerDisconnected on the second send of every run.
    with send_mod.connect(cfg) as srv:
        srv.send_message(msg)
```

All five emails from those runs did deliver. Only the runs failed.

### Twelve businesses emailed step 1 twice (Aug 20)

**Symptom:** run #56 mailed the same twelve leads a second time, ~90 minutes
after an earlier run had already sent them.

**Cause:** `actions/checkout` defaults to `github.sha` — the commit `main`
pointed at when the run was **created**, not when it started. The concurrency
group correctly made #56 wait. But when it finally started it checked out the
pre-wait commit, i.e. a database from before the earlier run's twelve sends. It
read "already sent today 0," found the same twelve due, and sent them again.

*The concurrency group was doing its job. The checkout was undoing it.*

**Fix, two parts:**

```yaml
- uses: actions/checkout@v4
  with:
    ref: main          # read the state the run ahead of us just wrote
```

plus a rebase-and-retry loop replacing the bare `git push`. #56's push was
rejected, which is why `main` has no record of the duplicates. Without the
retry, a lost push means those leads get mailed again the next day.

### A bare "stop" was not detected as an opt-out

**Symptom:** Russell at Thomson Plumbing replied with exactly `stop`. The
campaign did not treat it as an unsubscribe. The email footer says "Reply STOP."

**Cause:** the opt-out regex only matched phrases like "stop emailing" or
"stop sending." A bare one-word reply matched nothing.

**Fix** in `cli.py`:

```python
BARE_OPT_OUT = re.compile(
    r"^\s*(?:please\s+)?(?:stop|unsubscribe|remove(?:\s+me)?)\s*[.!]*\s*$", re.I
)

def wants_out(text: str) -> bool:
    t = (text or "").strip()
    if not t:
        return False
    first = next((l for l in t.splitlines() if l.strip()), "")
    return bool(BARE_OPT_OUT.match(first) or OPT_OUT.search(t))
```

Checking only the first non-empty line matters: quoted reply text below the
signature would otherwise trigger false positives. 12 cases verified both ways.

### One decline reaching the same company at three addresses

**Symptom:** London Mechanical declined politely from one address. Two other
addresses at the same company were still in the sequence.

**Fix** — domain-level suppression in `db.py`:

```python
SHARED_DOMAINS = {"gmail.com", "hotmail.com", "outlook.com", ...,
                  "telus.net", "shaw.ca", "sasktel.net", "mts.net", "ody.ca", ...}

def company_domain(email: str) -> str:
    d = email.strip().lower().rpartition("@")[2]
    return "" if d in SHARED_DOMAINS else d
```

`suppress()` now also writes a `"@" + domain` key and skips every lead at that
domain. `is_suppressed()` checks both. The `SHARED_DOMAINS` set is essential —
without it, one Gmail user opting out would suppress every Gmail lead.

### IMAP would have failed silently

**Symptom:** none yet. Caught before the secret was even added.

**Cause:** `[imap] user` was blank, and blank falls back to `smtp.user` — the
Brevo relay username. Logging into Gmail with a Brevo username can only ever
fail, and it would have failed quietly, so replies would never have been
detected and people who said no would have kept getting mail.

**Fix:** `user = "srijan.ghosh072011@gmail.com"` set explicitly, with a comment
explaining why it can never be left blank.

### GitHub Actions quota exhausted (Aug 24 – Sept 1)

**Symptom:** every scheduled run failing in about 2 seconds with no steps and
no runner assigned. Eight days of zero sends.

**Cause:** `min_gap_seconds`/`max_gap_seconds` were 240–900. A 34-email day
therefore held a runner open for **5 hours 20 minutes** doing nothing but
sleeping. Actions minutes on a private repo are billable against the 2,000/month
free tier.

**Fix:** gaps cut to 30–90 seconds. The same 34 sends now take ~33 minutes
instead of 314. A full 50-email day is roughly 50 minutes instead of eight hours.

Deliverability comes from domain authentication, a warm-up ramp and honest
content — not from whether two messages are one minute or ten minutes apart.

Quota reset at the start of September and runs resumed on Sept 3.

### `cmd_offer` logs `kind='offer'`, never `'sent'`

Not a bug, a deliberate constraint worth knowing. `last_step()` reads only
`'sent'` rows and computes the next step as `last[0] + 1`. An offer row has
`step=None`, so logging one as `'sent'` would crash the next scheduled run with
a `TypeError`.

## 1.10 Campaign state, as of 2026-09-04

### Totals

```
leads          61 total
  active       50
  done          8
  skipped       2
  replied       1
events        220
  sent        218
  replied       2
suppressed      6 entries (4 addresses + 2 whole domains)
sending days   13
allowance      46/day (cap 50)
```

### Sends by step

| Step | Sent |
|---|---|
| 1 | 61 |
| 2 | 60 |
| 3 | 51 |
| 4 | 38 |
| 5 | 8 |

### Sends by day

```
Aug 10   5     Aug 18  22     Aug 24  34
Aug 11   8     Aug 19   8     ---- quota outage ----
Aug 12   8     Aug 20  12     Sep 01  42
Aug 13  12     Aug 21  18     Sep 02  16
Aug 14  15
Aug 17  18
```

### What is queued next

All 50 active leads come due across Sept 5–6, which are **Saturday and Sunday**.
`send_days` is weekdays only, so nothing sends over the weekend and the entire
backlog lands at once:

| Day | Sends | What |
|---|---|---|
| **Mon Sept 7** | ~46 (the daily allowance) | 30× step 5, 9× step 4, 7× step 3 |
| **Tue Sept 8** | ~4 (the remainder) | step 4 |

**After Tuesday the email channel is finished.** 30 of those Monday sends are
step 5, the breakup email, which promises to stop emailing. Nothing may follow
it. 58 of 61 leads will be `done`, and every scheduled run after that will send
zero until new leads are imported.

### The three replies, ever

| Who | When | What | Status |
|---|---|---|---|
| London Mechanical (Mary-Lynn) | Aug 13 | "Not anything we do, but thank you." | Suppressed, whole domain |
| Russell, Thomson Plumbing | Aug 17 | `stop` | Suppressed, whole domain |
| **Greg Iwankow, Rusty Pipes** | **Sept 1** | **UNREAD** | Removed from sequence, **not suppressed** |

### Suppression list

```
lonmech@ody.ca                  replied — not a fit, declined politely 2026-08-13
lynn@londonmechanical.ca        same company as lonmech@ody.ca — declined
mary-lynn@londonmechanical.ca   replied to decline 2026-08-13
@londonmechanical.ca            whole domain
russell@thomsonplumbing.ca      replied STOP 2026-08-17
@thomsonplumbing.ca             whole domain
```

Note `lonmech@ody.ca` did **not** get a domain-level suppression, correctly —
`ody.ca` is a shared ISP domain and is in `SHARED_DOMAINS`.

### The free-offer send — an untracked event

On Aug 20, `offer.yml` run #2 sent `offer_free` to exactly **four** addresses:

| Email | Business | City |
|---|---|---|
| info@neumannplumbing.ca | Neumann Plumbing | Edmonton AB |
| admin@theplumbineers.com | Plumbineers Plumbing & Heating | Red Deer AB |
| info@nickelplumbing.com | Nickel Plumbing & Heating | Saskatoon SK |
| bobby2213@hotmail.com | Favoured Plumbing & Heating | Moncton NB |

Run #1 (17 seconds) was the dry run. Run #2 took 32 minutes for four sends
because the gaps were still 486–796 seconds at that point.

**Two things to know:**

1. It went to four leads, not to every non-replier. If the intent was the
   whole non-replying list, that never happened.
2. **The database has no record of it** (`offer` events: 0) because `offer.yml`
   does not commit state. All four continued through the normal sequence and
   are now at step 4. So those four received a "free site" offer on Aug 20 and
   a "$1,500 to build it" email afterwards, with nothing connecting them.

None of the four replied.

### All 50 active leads

| ID | Business | City | Prov | Phone | Step |
|---|---|---|---|---|---|
| 14 | Neumann Plumbing | Edmonton | AB | 780-429-0295 | 4 |
| 12 | Simpson Plumbing | Lethbridge | AB | 403-328-3584 | 4 |
| 59 | Berger's Plumbing & Company | Medicine Hat | AB | 403-528-2082 | 2 |
| 45 | KAT Plumbing & Gas Fitting | Medicine Hat | AB | — | 3 |
| 13 | Plumbineers Plumbing & Heating | Red Deer | AB | 403-302-7606 | 4 |
| 47 | Kris Howe's Plumbing & Gas | Wetaskiwin | AB | 780-361-8645 | 3 |
| 32 | Armacom Plumbing | Abbotsford | BC | 604-329-4009 | 4 |
| 36 | Fairfield Island Plumbing & Heating | Chilliwack | BC | 604-793-9395 | 4 |
| 28 | Dean's Plumbing & Heating | Cranbrook | BC | 250-489-1803 | 4 |
| 60 | Bugaboo Plumbing Company | Golden | BC | 250-439-9119 | 2 |
| 15 | Kelowna Plumbing Solutions | Kelowna | BC | 778-754-5880 | 4 |
| 20 | Plumber Nanaimo | Nanaimo | BC | 250-797-4273 | 4 |
| 42 | Quality First Plumbing & Heating | Penticton | BC | 250-493-8886 | 3 |
| 25 | Mr Plumbing and Heating | Prince George | BC | 250-565-4743 | 4 |
| 26 | The Family Plumbing and Heating | Prince George | BC | 778-764-1149 | 4 |
| 56 | Palomino Plumbing | Salt Spring Island | BC | 250-719-3623 | 2 |
| 35 | Bertelsen Plumbing Ltd. | Vernon | BC | 250-542-4153 | 4 |
| 57 | 1st Rate Plumbing | Gimli | MB | 204-886-0143 | 2 |
| 52 | T N T Plumbing & Heating | Selkirk | MB | 204-482-4159 | 3 |
| 48 | Premium Plumbing Inc. | Steinbach | MB | 204-905-0887 | 3 |
| 46 | RMB Plumbing and Heating | Steinbach | MB | 204-346-2803 | 3 |
| 17 | E.T. Mechanical Ltd. | Fredericton | NB | 506-444-4663 | 4 |
| 16 | Hello Plumber Inc. | Fredericton | NB | 506-476-8520 | 4 |
| 22 | Maritime Plumbing Services | Fredericton | NB | 506-259-4157 | 4 |
| 11 | EVENFLOW Plumbing & Heating | Moncton | NB | 506-889-3569 | 4 |
| 9 | Favoured Plumbing & Heating Ltd | Moncton | NB | 506-232-0777 | 4 |
| 21 | PRO-TECH Plumbing & Heating | Moncton | NB | 506-232-8900 | 4 |
| 31 | King's Plumbing and Heating Ltd | St. John's | NL | 709-364-6427 | 4 |
| 54 | Glasgow Plumbing and Heating | New Glasgow | NS | 902-301-1167 | 3 |
| 55 | All Hours Plumbing & Heating | Sydney | NS | 902-564-1852 | 2 |
| 34 | Dave The Plumber Plumbing & Heating | Sydney | NS | 902-567-4768 | 4 |
| 29 | ZMP Plumbing & Excavation | Truro | NS | 902-957-3422 | 4 |
| 38 | Arctic Plumbing & Heating | Yellowknife | NT | 867-446-0010 | 4 |
| 37 | Wiseman's Plumbing & Heating | Yellowknife | NT | 867-445-4057 | 4 |
| 19 | Sampson Plumbing and Drain Service | Barrie | ON | 647-285-8667 | 4 |
| 50 | Royal Flush Plumbing Service | Chatham | ON | 519-999-0112 | 3 |
| 44 | Aurele St. Jean Plumbing | Cornwall | ON | 613-932-3434 | 3 |
| 43 | EverFlow Plumbing | Cornwall | ON | 613-360-8528 | 3 |
| 40 | Fabulous Plumbing & Heating Ltd | Guelph | ON | 519-820-4563 | 4 |
| 18 | Allen Mechanical Inc. | Kingston | ON | 613-634-7298 | 4 |
| 33 | Kitchener Waterloo Plumbing | Kitchener | ON | 548-483-5616 | 4 |
| 58 | Brendon Mackay Plumbing & Heating | Pembroke | ON | 613-629-6290 | 2 |
| 30 | Plumbing Possibilities | Peterborough | ON | — | 4 |
| 51 | Smitty's Plumbing | Simcoe | ON | 519-428-6250 | 3 |
| 39 | Complete Plumbing | St. Catharines | ON | — | 4 |
| 61 | Water Tight Plumbing & Heating | Charlottetown | PE | 902-621-0667 | 2 |
| 41 | Super Service Plumbing & Heating | Prince Albert | SK | 306-960-0082 | 3 |
| 23 | Able Plumbing & Heating | Regina | SK | 306-569-0047 | 4 |
| 24 | Nickel Plumbing & Heating Ltd. | Saskatoon | SK | 306-653-1899 | 4 |
| 49 | Swift Plumbing and Heating | Swift Current | SK | 306-778-2830 | 3 |

Every one of these has a phone number that has never been dialled.

## 1.11 CASL compliance

Canada's Anti-Spam Legislation. This is cold B2B email to Canadian businesses,
so it matters.

- **Consent basis:** implied consent via conspicuous publication. These are
  business addresses published publicly for the purpose of being contacted, and
  the message is relevant to that business.
- **Mailing address:** mandatory in every commercial email. Present in config
  and rendered into every send. `cli.py send` **refuses to run** while any
  `[sender]` or `[template]` value still contains the string `TODO`.
- **Unsubscribe:** handled automatically. Every footer says "Reply STOP." The
  IMAP reply-watcher suppresses on detection, well inside the 10 business days
  the law allows.
- **Suppression is permanent** and stored in the committed database.

## 1.12 Analytics

GA4 is live on the demo site, measurement ID `G-LQPHPNP2QT`, configured in
`templates/regina-plumbing/lib/client.config.ts`.

Verified: `npm run build` succeeds, the tag reaches built output, and the
consent defaults plus the gtag loader land in the same JS chunk in source order
so nothing is stored before consent is given. Consent Mode v2, with a banner,
for PIPEDA.

Deployed via run #30 on branch `claude/site-replica-seo-aeo-phglx9`; confirmed
present in the published `docs/`.

**Custom events wired up:** `phone_call_click` and `generate_lead`. GA4's
enhanced measurement does not capture `tel:` taps, so phone clicks needed
explicit instrumentation.

**Still to do (both are clicks in the GA4 web UI, not code):**
- Open demo.ghoshdesigns.ca, accept the banner, confirm it appears in Realtime
- Mark `phone_call_click` and `generate_lead` as **key events** in
  Admin → Events

Note: ad blockers block the GA script. If Realtime shows nothing, try a
different browser before assuming it is broken.

## 1.13 Things deliberately refused

Recorded so they do not get quietly reintroduced.

| Proposed | Why it was refused |
|---|---|
| Prompt injection in emails to manipulate recipient AI tools | Deceptive; would poison the relationship if noticed, and it would be |
| Offering faster/incentivized Google reviews in exchange for the free build | Violates Google's review policy. Risks the client's profile, not just yours |
| Fake scarcity caps ("only 3 spots") | Not true |
| Fake discount badges | Not true |

The honesty here is load-bearing. The whole pitch is "I built you a thing, look
at it" — it only works from someone who is not obviously running a playbook.

## 1.14 How to operate it

**Send a manual one-off email:** Actions → `offer` → Run workflow → set
`template`, `to` (comma-separated), `dry_run`. Always dry-run first. Remember it
writes no state.

**Add new leads:** either edit `outreach/leads.csv` and push, or run the
`find-leads` workflow after widening `[places].cities` in `config.toml`. The
schedule picks up new rows automatically and starts them at step 1.

**Check what happened:** Actions → `outreach` → newest run → the *Campaign
status* step. Or read the `daily` step for the line that looks like
`ramp allowance 46/day · already sent today 0 · budget now 46 · due 0`.

**"due 0" is usually not a bug.** It means no lead has a step whose delay has
elapsed. Between waves this is normal and expected.

**Pause everything:** disable the `outreach` workflow in the Actions tab.

**Pull one lead out of the sequence:** add their address to the suppression
table, or set their `status` to `skipped`.

---

# SECTION 2 — COLD SMS

## 2.1 The idea

Different offer from the email campaign, and a better one.

Text a small solo plumber a screenshot of a homepage built for their business,
and offer to build it **completely free**, in exchange for being allowed to put
them in a portfolio. No monthly fee. No catch.

In his own words:

> *"I'm basically not here... I could just build a website, and I could go away
> after. 'Hi, this is me. I built websites. I'll build you one for free. No
> charge, no bullshit. I just need you guys to be in my portfolio.'"*

And on why it is worth doing at a loss:

> *"I will do one free one. Cause I have a really solid idea in my head. I feel
> like this will also help me do cold calls much more."*

Two rules that were set explicitly:

1. **Leave the monthly out of it.** *"You wait, leave the monthly part. I'm just
   gonna give them the site."*
2. **Do not force it.** *"But I don't want to force it on them."*

## 2.2 Why SMS, and the risk that was accepted

SMS gets read. Email from an unknown teenager to a plumbing company mostly does
not — 218 sends, 3 replies, 0 clients is the proof.

**The blocker:** proper A2P/Twilio-style SMS is not an option. Twilio and every
compliant provider prohibit cold SMS outright in their acceptable-use policies.
There is no legitimate service that will send this.

**Which leaves texting from a personal phone.** That was raised, considered,
and accepted:

> *"SMS. What am I losing? Private number. It's like I'm too small of a business
> right now, so it won't really matter until it gets bigger."*

**What that actually costs, stated plainly so it is not a surprise later:**

- The personal number is disclosed to every recipient, permanently
- Recipients can look it up, save it, share it, or complain about it
- Carrier-level spam flagging is possible if enough people report it, which
  would affect ordinary personal texting too
- There is no unsubscribe infrastructure — opt-outs must be honoured by hand

**Mitigations in force:** send few, send slowly, personalize every single one
(a real mockup of their business, not a blast), stop immediately on any
negative reply, never text the same person twice.

## 2.3 The list

Source: Google Sheet **"Plumbing Leads — Text-Friendly (Small/Solo Operators)"**
(created Aug 23, last modified Aug 24).

Selection criterion: businesses where the person answering the phone is almost
certainly the owner. Signals used were tiny Google review counts, no website,
a business named after a person, recent incorporation, and public evidence the
owner handles their own messages.

22 rows. One scratched, one texted, **20 remaining**.

| # | Business | City | Prov | Phone | Reviews | Why text-friendly |
|---|---|---|---|---|---|---|
| ~~1~~ | ~~Parker Plumbing Ltd~~ | ~~West Kelowna~~ | ~~BC~~ | ~~778-392-7203~~ | ~~~500 IG~~ | **SCRATCHED — already has a really good site** |
| 2 | Bugaboo Plumbing Company | Golden | BC | 250-439-9119 | 1 | Only 1 review; near-certain one-person shop. Named contact breanne@bugabooplumbing.com |
| 3 | Sewer King | Swift Current | SK | 306-741-0479 | 9 | Owner Les Smid posts from a personal Facebook profile, not a business page. No website |
| 4 | Skalicky's Plumbing | Revelstoke | BC | 250-837-6271 | 7 | Tiny review count, big casual IG following. Very personal brand voice. No website |
| 5 | All Hours Plumbing & Heating (2018) | Sydney | NS | 902-564-1852 | 10 | Registered 2018, small. allhours2018@gmail.com |
| 6 | Jaguar Plumbing & Heating | Creston | BC | 250-254-2222 | 10 | Old website domain now dead. Has IG and email |
| 7 | Vance Plumbing and Heating Ltd | New Glasgow | NS | 902-752-3205 | 11 | Very small review count. No website |
| 8 | Duffy's Plumbing | Corner Brook | NL | 709-632-4501 | 15 | Small local. No website, has Facebook |
| 9 | Smitty's Plumbing | Simcoe | ON | 519-428-6250 | 15 | Named owner-operator Jeff Smith. Personal email jeff.smith6@hotmail.com |
| 10 | Cody Mackay Plumbing | Pembroke | ON | 613-281-5232 | 15 | Named after one owner, incorporated 2021. Young solo operator. No website |
| 11 | E & R Plumbing & Heating Ltd | Miramichi | NB | 506-773-4900 | 15 | Small family operation. No website |
| 12 | Rusty Pipes Plumbing Repairs | East Selkirk | MB | 204-294-4089 | 14 | Owner Greg Iwankow, small rural area |
| 13 | Dow's Plumbing & Heating Ltd. | Charlottetown | PE | 902-314-6262 | 14 | Website domain dead. Has Facebook |
| 14 | Limestone Mechanical Ltd | Canmore | AB | 403-707-7212 | 14 | Small despite active IG. No website |
| 15 | L. E. Steele Drain Solutions | Charlottetown | PE | 782-772-8188 | 17 | Named owner Geoffrey Steele, registered 2024. Brand new solo operator |
| 16 | Lupien Jean Plumbing | Cornwall | ON | 613-938-5700 | 20 | Named after owner Jean Lupien. No website |
| 17 | Water Tight Plumbing & Heating | Charlottetown | PE | 902-621-0667 | 21 | Domain is an expired parked page. watertight_ph@hotmail.com |
| 18 | Clockwork Plumbing & Gas | Camrose | AB | 780-781-7622 | 21 | Named owner Travis Csernyanszki, small |
| 19 | **Austin's Plumbing** | Camrose | AB | 780-781-2795 | 40 | **ALREADY TEXTED Aug 20.** Owner posted publicly that his IG Messenger is unreliable and to contact him directly |
| 20 | D.P. Drain Plumbing | Toronto | ON | 437-577-2043 | N/A | ~162 IG followers in a Toronto market. Bio says "Your Real Plumber", one direct line not a dispatch number |
| 21 | First Choice Plumbing & Heating | Timmins | ON | 705-267-1115 | 5 | Backup / lower confidence |
| 22 | Pembina Valley Plumbing & Heating | Winkler | MB | 204-331-3031 | 7 | Backup / lower confidence |

## 2.4 What has actually been sent

**One text. Austin's Plumbing, 780-781-2795, Aug 20.** No reply. No follow-up
was ever sent.

Everything else on this list is untouched.

## 2.5 ⚠️ Conflicts with the email campaign

**Four of these businesses are currently active in the email sequence.** Texting
them while they are also being emailed makes the whole thing look like a
mass-mailing operation, which is exactly the impression the copy works to avoid.

| Business | Email lead ID | Email step |
|---|---|---|
| Bugaboo Plumbing Company | 60 | step 2 |
| All Hours Plumbing & Heating | 55 | step 2 |
| Smitty's Plumbing | 51 | step 3 |
| Water Tight Plumbing & Heating | 61 | step 2 |

**Rule: pull them from the email sequence before texting, or do not text them.**
Pick one channel per business. Do not run both.

**Rusty Pipes (#12) is a special case.** Greg replied to the *email* on Sept 1
and has already left the sequence. **Read that reply before doing anything
else** — do not text a live email thread.

**Two to verify before texting** — same town, possibly the same family business
under a different name:

- Cody Mackay Plumbing (Pembroke ON) vs. email lead #58 *Brendon Mackay
  Plumbing & Heating* (Pembroke ON)
- Lupien Jean Plumbing (Cornwall ON) vs. email leads #44 *Aurele St. Jean
  Plumbing* and #43 *EverFlow Plumbing* (both Cornwall ON)

These read as distinct businesses, but the surnames and towns line up closely
enough to check first.

## 2.6 The script

Sent as **one single message**, with the mockup image attached. This was an
explicit requirement: *"The text should be all in one message."*

Constraints it has to satisfy:
- One message, not a sequence
- No em dashes (same rule as email)
- Sounds like a person typing on a phone, not a marketer
- Includes the demo link — *"add the link to all of the message"*
- Free, no monthly, no pressure
- **No review incentive.** The original idea included asking for a faster Google
  review in exchange. That was removed: incentivized reviews violate Google's
  policy and put the plumber's own profile at risk

Shape:

```
Hey [name], I'm Srijan, I build websites out of Regina. I made a homepage
for [Business] to see how it'd look. Screenshot attached.

I'm doing a few of these free right now because I need real companies in my
portfolio. No charge, nothing monthly, I just want to be able to show it.

Here's a finished one you can click around: demo.ghoshdesigns.ca

If you want yours built out let me know, and if not no worries at all.
```

> ⚠️ **Verify this against what was actually sent to Austin's on Aug 20.** The
> exact wording of the version that went out lived in the chat, not in a repo.
> Reconstructed here from the constraints above. Confirm before reusing, so the
> first text and the next twenty match.

## 2.7 Mockups

62 generated screenshots live in `outreach/mockups/*.jpg`, named by slugified
business name — for example `rusty-pipes-plumbing-repairs.jpg`,
`all-hours-plumbing-heating.jpg`.

Generated by `src/shoot.py`: Playwright drives Chromium against the demo site
served locally by `src/serve.py`, with the business's real details substituted
in, then Pillow optimizes to under `max_image_kb` (250).

**Not every SMS lead has a mockup here** — this folder covers the *email* leads.
SMS-only leads had mockups made separately during the chat. Check for a file
before texting; if there is none, generate one first. A text without the
screenshot has no reason to be read.

**Known problem: getting the images onto the phone.** Raised more than once
(*"I'm so not letting me downloaded images on my phone"*). Never fully solved.
Options if it recurs: email the images to himself and save from the Gmail app,
or put them in Google Drive/Photos and save from there.

## 2.8 The sending schedule

Set after high school started. The real constraint:

> *"In the morning, I'm gonna have to get up at 7:00, and maybe the latest I can
> send it is 8:00."*

After school is not realistic and should not be planned around.

**The 7:30 am Regina window is actually the best hour on this list**, because
Saskatchewan does not observe DST:

| Region | Local time at 7:30 am Regina | Verdict |
|---|---|---|
| BC | 6:30 am | Too early |
| Alberta | 7:30 am | Too early |
| Manitoba | 8:30 am | Workable |
| Ontario | 9:30 am | Ideal |
| Maritimes (NB/NS/PE) | 10:30 am | Ideal |
| Newfoundland | 11:00 am | Ideal |

So the eastern half of the list fits the morning window perfectly. The western
half does not and needs a weekend.

### Plan

**Weekday mornings, three texts each, before leaving:**

| Day | Who |
|---|---|
| Mon | Cody Mackay (Pembroke ON) · Lupien Jean (Cornwall ON) · E & R (Miramichi NB) |
| Tue | D.P. Drain (Toronto ON) · Vance Plumbing (New Glasgow NS) · Duffy's (Corner Brook NL) |
| Wed | Dow's (Charlottetown PE) · L.E. Steele (Charlottetown PE) · First Choice (Timmins ON) |

**Saturday, any time 10 am to 4 pm Regina:** Sewer King, Skalicky's, Clockwork,
Limestone, Jaguar. Alberta and BC are only 0–1 hours behind, so a Saturday
midday session covers all of them.

**Pembina Valley (Winkler MB)** fits a weekday morning at 8:30 am local.

**Held back pending the conflicts in §2.5:** Bugaboo, All Hours, Smitty's,
Water Tight, Rusty Pipes.

If a morning gets away from him, skip it. Two a day still finishes the list.

## 2.9 SMS open items

- [ ] **Read Greg's reply at Rusty Pipes first.** Sept 1, still unread
- [ ] Verify the script against what Austin's actually received Aug 20
- [ ] Decide the channel for the 4 conflicts, and pull them from email if texting
- [ ] Check Cody Mackay / Lupien Jean against the Pembroke and Cornwall email leads
- [ ] Confirm a mockup image exists for each of the 20 before texting
- [ ] Solve getting images onto the phone
- [ ] Consider a single follow-up to Austin's — texted Aug 20, never followed up

---

# SECTION 3 — CONSOLIDATED OPEN ITEMS

## Do before Monday 07:23 Regina

- [ ] **Read Greg Iwankow's reply** (Rusty Pipes, Sept 1). Only live thread in
      the entire operation. Gmail connector needs re-authorization before an AI
      session can read it — check by hand, or reconnect Gmail in claude.ai
      connector settings
- [ ] **Fix "before September"** in `step4_price.txt` and `offer_free.txt`.
      13 leads receive step 4 on Monday and Tuesday with a deadline that has
      already passed. Either delete the sentence or replace it with something
      true. This is exactly the kind of false claim the rest of the copy was
      cleaned up to avoid

## Do this week

- [ ] Decide what happens when the email list runs dry on Tuesday: import a new
      batch of leads, or stop email and put the time into calls
- [ ] Start the SMS mornings (§2.8)
- [ ] GA4: accept the banner on demo.ghoshdesigns.ca, confirm Realtime shows the
      hit, and mark `phone_call_click` and `generate_lead` as key events

## Standing gaps

- [ ] **Nobody has ever been phoned.** ~40 numbers in §1.10, plus 20 in §2.3.
      Cold calling was the original reason for wanting a portfolio piece
- [ ] Reply to Lynn at London Mechanical — drafted, never sent. She is
      suppressed, so this is courtesy only, not outreach
- [ ] `offer.yml` writes no campaign state, so manual sends are invisible to the
      database and to the sequence logic. Worth fixing if manual sends become
      routine
- [ ] The 4 leads who got the free offer on Aug 20 later received the $1,500
      price email with nothing connecting the two. Worth a sentence if any of
      them ever replies

## Honest assessment

The machine works. It is well built, the bugs are real bugs that were found and
fixed properly, and it costs nothing to run.

It has also produced **0 clients from 218 emails and 1 text.** Three replies,
two of them rejections. That is roughly a 1.4% reply rate and a 0% close rate.

The email channel has been given a fair test and the answer is mostly no. The
untested channels are the phone and SMS, and the phone is the one that has never
been tried at all despite being the original point of building a portfolio piece.
Forty numbers are sitting in a database.

The free build is the strongest asset here — it is a genuinely good offer that
costs nothing but time and produces the portfolio piece that makes every future
pitch easier. It has been offered to four people by email and one by text, and
none of them saw it as more than another cold message. It will land far better
spoken than typed.
