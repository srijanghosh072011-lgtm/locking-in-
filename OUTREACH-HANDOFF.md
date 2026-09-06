# Ghosh Designs Outreach Handoff

**Operations handoff — cold outreach.**

The complete state of the cold-outreach operation: the email engine, the SMS
channel, every bug found and fixed, and what is waiting to be done. Written so
that a person or an AI session with zero prior context can pick this up and keep
going.

| | |
|---|---|
| **Owner** | Srijan Ghosh, Ghosh Designs, Regina SK |
| **State as of** | 2026-09-04, 18:22 Regina |
| **Source** | Live campaign database, not memory |

| Leads | Emails sent | Replies | Clients | Texts sent | Calls made |
|---:|---:|---:|---:|---:|---:|
| 61 | 218 | 3 | 0 | 1 | 0 |

## Contents

- [00 — Read first](#00--read-first)
- [01 — The email automation](#01--the-email-automation)
- [02 — Cold SMS](#02--cold-sms)
- [03 — Open items](#03--open-items)
- [04 — Reference](#04--reference)

---

## 00 — Read first

Five things that matter more than anything else in this document.

### 01. Greg at Rusty Pipes replied on Sept 1. Nobody has read it. — *Unread*

Caught by the IMAP watcher and pulled from the sequence, but the reply itself is
sitting in Gmail. It is the only live thread in the entire operation.

### 02. Step 4 says "before September." It is September. — *Before Mon 07:23*

13 leads receive that email Monday and Tuesday with a deadline that has already
passed. `offer_free.txt` has the same line.

### 03. The email list runs dry on Tuesday. — *Mon–Tue*

~46 sends Monday, ~4 Tuesday, then 58 of 61 leads are finished and every run
after that sends zero.

### 04. 20 of 21 SMS leads have never been texted. — *Not started*

One text has gone out, to Austin's Plumbing on Aug 20. No follow-up.

### 05. Nobody has ever been phoned. — *Not started*

Roughly 60 numbers between the email database and the SMS sheet. Cold calling
was the original reason for wanting a portfolio piece.

### The honest summary

The machine works. It is well built, the bugs found in it were real bugs fixed
properly, and it costs nothing to run. It has also produced zero clients from
218 emails and one text — three replies, two of them rejections. About a 1.4%
reply rate and a 0% close rate.

The email channel has had a fair test and the answer is mostly no. The untested
channels are SMS and the phone, and the phone has never been tried at all.

---

## 01 — The email automation

A Python program that runs on GitHub's machines four times each weekday morning.
Nothing depends on a laptop being awake.

For each plumbing company in a database it screenshots a homepage mockup built
for that specific business, emails it to them with a short personal note,
follows up four more times over roughly sixteen days, watches the inbox over
IMAP and drops anyone who replies, then commits the updated database back to the
repo so the next run knows what happened.

### Where everything lives

| Repo | Branch | What it is |
|---|---|---|
| `email-automation-` | `main` | The engine. Code, config, templates, lead database |
| `plumbing-Templates-` | `claude/site-replica-seo-aeo-phglx9` | The demo site. Built output in `docs/` |
| `idk` | `gh-pages` | The agency site, ghoshdesigns.ca |
| `locking-in-` | `claude/ghosh-designs-outreach-ovuq7t` | This handoff |

> **The engine repo must stay private.**
> Every workflow has a guard step called "Refuse to run while this repository is
> public" that hard-fails the run if it ever goes public. The repo holds the
> lead database and 62 mockup images.

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
        ├── cli.py         (797)    # command surface + orchestration
        ├── audit.py       (241)    # scores their existing site
        ├── db.py          (151)    # SQLite + suppression
        ├── personalize.py  (98)    # name/company token handling
        ├── places.py      (111)    # Google Places lookup
        ├── render.py      (203)    # template -> MIME message
        ├── send.py         (67)    # SMTP connection
        ├── serve.py        (65)    # local static server for screenshots
        └── shoot.py       (179)    # Playwright screenshot + Pillow optimize
```

Python 3.11, standard library wherever possible — `tomllib`, `sqlite3`,
`smtplib`, `imaplib`, `zoneinfo`. The only third-party dependencies are
Playwright for screenshots and Pillow for image optimization.

### Identity and infrastructure

| | |
|---|---|
| From | `srijan@ghoshdesigns.ca` |
| Reply-To | `srijan.ghosh072011@gmail.com` |
| Bcc (silent) | `srijan.ghosh072011@gmail.com` |
| SMTP | `smtp-relay.brevo.com:587` · user `b424bf001@smtp-brevo.com` |
| SMTP password | Actions secret `SMTP_PASSWORD` — not available locally |
| IMAP | `imap.gmail.com` · user `srijan.ghosh072011@gmail.com` |
| IMAP password | Actions secret `IMAP_PASSWORD` |
| Phone in emails | (639) 777-1017 |
| Mailing address | 2812 25th Ave, Regina, SK S4S 1K6 |
| Demo link | https://demo.ghoshdesigns.ca |
| Agency site | https://ghoshdesigns.ca |
| GA4 property | G-LQPHPNP2QT |

**Why Brevo and not Gmail.** Gmail SMTP is routinely blocked from datacenter IPs
like GitHub Actions runners, and it reports that block as `BadCredentials` —
indistinguishable from a wrong password. Brevo is a transactional relay built
for exactly this.

**Why From and Reply-To differ.** The From address sits on the authenticated
domain so SPF, DKIM and DMARC align and the mail lands. Replies go to the Gmail
inbox that actually gets read.

**Why it sends plain text.** `plain_text_only = true` and
`list_unsubscribe_header = false`. Inline images plus HTML plus a
List-Unsubscribe header together are what push cold mail into Gmail's Promotions
tab. The mockup rides along as an attachment instead.

**A preflight warning that is a false alarm.** The check step prints
`[XX] app password looks like 16 chars — got 90`. That check was written for
Gmail App Passwords, which are 16 characters. Brevo SMTP keys are long. It does
not block the run and can be ignored.

### The sequence

Five steps. Delays are days since the previous step reached that lead.

| Step | Template | Delay | Subject line |
|---|---|---|---|
| 1 | `step1_preview` | 0 | made you a homepage for {business} |
| 2 | `step2_bump` | 3 d | re: made you a homepage for {business} |
| 3 | `step3_proof` | 4 d | three things worth checking on your site |
| 4 | `step4_price` | 4 d | what it actually costs |
| 5 | `step5_close` | 5 d | last one from me |

Step 4 sits before step 5 deliberately. Step 5 promises to stop emailing, so
nothing may follow it. Price had to come first — nobody had ever been told what
this costs, and silence on price is a common reason a warm prospect goes quiet.

A sixth template, `offer_free`, is not part of the sequence. It is sent by hand
through the offer workflow.

**Template tokens.** `{{first_name}}`, `{{business}}`, `{{sender_email}}`,
`{{website}}`, `{{demo_link?}}`, `{{audit_line?}}`. A token ending in `?` makes
its whole line vanish when the value is empty — which is why leads with no audit
finding do not get a blank gap in the middle of the email.

### The six templates, in full

#### `step1_preview.txt` — 61 sent

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

#### `step2_bump.txt` — 60 sent

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

#### `step3_proof.txt` — 51 sent

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

#### `step4_price.txt` — 38 sent · **contains the stale deadline**

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

#### `step5_close.txt` — 8 sent

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

#### `offer_free.txt` — 4 sent · **contains the stale deadline**

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

### Voice rules — these were fought for

Every one of these came from a specific correction. Anyone editing the copy has
to hold them.

- **No em dashes anywhere.** Verified zero across all six templates. They read as
  AI-written. They were stripped twice, because they got reintroduced once.
- **No invented scenarios.** An early draft had a line about "it's 9 p.m. and
  someone's calling." Cut outright. "No one really says that."
- **Never claim it takes weeks.** A build is one to two days at most. A draft
  that said "two weeks" had invented that number.
- **Don't argue against the product.** A line reading "plenty of people never
  needed a website" was removed. It talked the prospect out of buying.
- **Never claim something untrue about their site.** Step 3 originally said
  "worth checking yours against that" — sent to twelve businesses with no
  website at all.
- **Contact details in every email.** Name, company, city, email, website.
- **Watch the line wrap.** Long business names blew past the wrap at 102
  characters. Breaks were moved to sit after `{{business}}`; worst case is now
  85.
- **Watch punctuation against tokens.** Business names ending in "Inc." produced
  `Inc..` The sentence was restructured so no period follows the token.

### Pricing

| | Build | Monthly |
|---|---|---|
| Old | $2,500 | $450 |
| **Current** | **$1,500** | **$250** |

Nothing is owed until the site is live and they are happy with it. The $250/month
covers hosting and any changes they want, done the same day they ask.

**What the retainer does not include.** No monthly report. No Google Business
Profile management. Both were corrected explicitly — do not re-add them.

ghoshdesigns.ca was updated to match, and "Live in days, not months" replaced the
old timeline claim in sixteen places.

### The three workflows

#### `outreach.yml` — the scheduled campaign

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

Four runs, and never on the hour. GitHub delays scheduled runs under load and
the top of the hour is the most congested minute. One run once slipped 5h36m and
landed at 18:36 Regina, outside the send window, sending nothing. Extra runs cost
nothing because the daily cap means the second run of a day sends zero.

Saskatchewan does not observe daylight saving, so UTC−6 holds year round and the
cron never needs a seasonal adjustment.

Steps in order: checkout at `ref: main` → public-repo guard → setup-python →
install → fetch demo template → preflight doctor → `cli.py daily` →
`cli.py status` → persist state with a rebase-and-retry push.

#### `offer.yml` — manual one-off sends

A `workflow_dispatch` with `template`, `to` and `dry_run` inputs. No Playwright,
no campaign run, no state commit. Same concurrency group so it cannot collide
with the schedule.

It exists because `SMTP_PASSWORD` only lives as an Actions secret. Sending from a
dev container is impossible — it fails with `RuntimeError: No SMTP password`.
Every manual send has to go through a runner.

> **A real gap.** Because `offer.yml` writes no state, its sends are invisible to
> the database and to the sequence logic. See the free-offer note in the state
> section below.

#### `find-leads.yml` — manual lead scraper

Runs the configured queries against the configured cities through the Google
Places API (New), keeps whatever clears `min_review_count`, looks up each one's
published email, and commits to `leads.csv`. The schedule picks it up on its own.
Needs the `GOOGLE_PLACES_API_KEY` secret.

Currently pointed at Saskatchewan only: Regina, Moose Jaw, Swift Current,
Yorkton, Prince Albert, North Battleford, Estevan, Weyburn. Queries are
`plumber` and `plumbing and heating contractor`.

### Sending controls

```toml
daily_cap         = 50
warmup            = [5,5,8,8,12,15,18,22,26,30,34,38,42,46,50]
min_gap_seconds   = 30
max_gap_seconds   = 90
timezone          = "America/Regina"
send_window_start = 7
send_window_end   = 18
send_days         = [1,2,3,4,5]   # weekdays only
```

The warm-up ramp indexes on sending days, not calendar days. Thirteen sending
days have elapsed, so the current allowance is 46/day, reaching the cap of 50 on
day fifteen.

Both qualifying bars are effectively off: `min_audit_score = 0` and
`min_review_count = 0`. The offer is "I made you a homepage," which stands up
whether or not their current site is bad, and the audit sentence only appears
when there is something true to say. The research sheet is the size filter now.

### The audit scoring system

`audit.py` fetches each lead's existing site and scores how badly they need a new
one, 0–100. The score picks the sentence that gets dropped into `{{audit_line}}`.
It never raises — a failure just returns a safe default.

| Flag | Points | Meaning |
|---|---:|---|
| `no_site` | 60 | No website at all |
| `not_mobile` | 25 | No viewport meta, does not adapt to phones |
| `no_https` | 15 | Still on http, Chrome shows "Not secure" |
| `table_layout` | 12 | Laid out with HTML tables, i.e. very old code |
| `slow` | 12 | Slow to respond |
| `no_title` | 10 | Missing the title tag Google reads |
| `tiny` | 10 | Almost no content on the page |
| `no_description` | 8 | Missing meta description |
| `stale` | 8 | Footer copyright year is old |
| `blocked` | 40 | Site refused the fetch; scored as a neutral middle |
| `unverified` | 40 | Could not be checked |

Current distribution across all 61 leads: 23 blocked, 16 unverified, 12 no_site,
5 clean, and 5 with specific findings. The heavy blocked/unverified share is why
the review-count bar was dropped to zero — the audit simply cannot see most of
these sites, so it cannot be used as a filter.

#### The six audit sentences

1. "You don't have a website yet, so every search for a plumber around here sends
   that job to someone else."
2. "Your site's still on http, so Chrome puts a 'Not secure' warning on it before
   anyone reads a word."
3. "Your site's missing the basic titles and descriptions Google reads, so you're
   not showing up for searches you should own."
4. "Your site's built on really old code under the hood, which is why it looks
   dated next to the other guys in town."
5. "The footer on your site still says 2020, which makes it look like nobody's
   touched it in a while."
6. "Had a look at your current site, there's a fair bit of room to turn more of
   the people landing on it into phone calls."

### Every bug found and fixed

The most valuable part of this document. Each one of these cost real sends.

#### `SMTPServerDisconnected` on the second send of every run

**Symptom.** Every run mailed exactly one lead, then crashed. Runs #22, #23, #24.

**Cause.** One SMTP connection was opened and held across the pacing sleep. The
gap was 4–15 minutes at the time. SMTP servers hang up idle sessions long before
that, so the connection was dead by the second `send_message`.

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

#### Twelve businesses emailed step 1 twice

**Symptom.** On Aug 20, run #56 mailed the same twelve leads a second time, about
ninety minutes after an earlier run had already sent them.

**Cause.** `actions/checkout` defaults to `github.sha` — the commit `main` pointed
at when the run was *created*, not when it *started*. The concurrency group
correctly made #56 wait. But when it finally started it checked out the pre-wait
commit, a database from before the earlier run's twelve sends. It read "already
sent today 0," found the same twelve due, and sent them again.

The concurrency group was doing its job. The checkout was undoing it.

```yaml
- uses: actions/checkout@v4
  with:
    ref: main          # read the state the run ahead of us just wrote
```

Plus a rebase-and-retry loop replacing the bare `git push`. #56's push was
rejected, which is why `main` holds no record of the duplicates. Without the
retry, a lost push means those leads get mailed again the next day.

#### A bare "stop" was not detected as an opt-out

**Symptom.** Russell at Thomson Plumbing replied with exactly `stop`. The campaign
did not treat it as an unsubscribe. The footer of every email says "Reply STOP."

**Cause.** The opt-out regex only matched phrases like "stop emailing" or "stop
sending." A bare one-word reply matched nothing.

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

Checking only the first non-empty line matters — quoted reply text below a
signature would otherwise trigger false positives. Twelve cases were verified
both ways.

#### One decline reaching the same company at three addresses

**Symptom.** London Mechanical declined politely from one address. Two other
addresses at the same company were still in the sequence.

```python
SHARED_DOMAINS = {"gmail.com", "hotmail.com", "outlook.com", ...,
                  "telus.net", "shaw.ca", "sasktel.net", "mts.net", "ody.ca", ...}

def company_domain(email: str) -> str:
    d = email.strip().lower().rpartition("@")[2]
    return "" if d in SHARED_DOMAINS else d
```

`suppress()` now also writes an `"@" + domain` key and skips every lead at that
domain; `is_suppressed()` checks both. The `SHARED_DOMAINS` set is essential —
without it, one Gmail user opting out would suppress every Gmail lead on the
list.

#### IMAP would have failed silently

**Symptom.** None yet. Caught before the secret was even added.

**Cause.** `[imap] user` was blank, and blank falls back to `smtp.user` — the
Brevo relay username. Logging into Gmail with a Brevo username can only ever
fail, and it would have failed quietly, so replies would never have been detected
and people who said no would have kept getting mail.

#### GitHub Actions quota exhausted, Aug 24 – Sept 1

**Symptom.** Every scheduled run failing in about two seconds with no steps and no
runner assigned. Eight days of zero sends.

**Cause.** The pacing gaps were 240–900 seconds. A 34-email day therefore held a
runner open for 5 hours 20 minutes doing nothing but sleeping, and Actions
minutes on a private repo are billable against the 2,000/month free tier.

**Fix.** Gaps cut to 30–90 seconds. The same 34 sends now take about 33 minutes
instead of 314. A full 50-email day is roughly 50 minutes instead of eight hours.
Deliverability comes from domain authentication, a warm-up ramp and honest
content, not from whether two messages are one minute or ten minutes apart.

#### Why offer sends log as `kind='offer'`

Not a bug, a constraint worth knowing. `last_step()` reads only `'sent'` rows and
computes the next step as `last[0] + 1`. An offer row has `step=None`, so logging
one as `'sent'` would crash the next scheduled run with a `TypeError`.

### Campaign state

| Status | Count | Meaning |
|---|---:|---|
| `active` | 50 | Still in the sequence |
| `done` | 8 | Finished all five steps |
| `skipped` | 2 | Suppressed, pulled out |
| `replied` | 1 | Wrote back, left the sequence |

| Step | Sent | | Day | Sent |
|---|---:|---|---|---:|
| 1 | 61 | | Aug 10 | 5 |
| 2 | 60 | | Aug 11 | 8 |
| 3 | 51 | | Aug 12 | 8 |
| 4 | 38 | | Aug 13 | 12 |
| 5 | 8 | | Aug 14 | 15 |
| **Total** | **218** | | Aug 17 | 18 |
| | | | Aug 18 | 22 |
| | | | Aug 19 | 8 |
| | | | Aug 20 | 12 |
| | | | Aug 21 | 18 |
| | | | Aug 24 | 34 |
| | | | Sep 1 | 42 |
| | | | Sep 2 | 16 |
| | | | **Total** | **218** |

The Aug 24 → Sept 1 gap is the Actions quota outage.

#### What is queued next

All 50 active leads come due across Sept 5–6, which are Saturday and Sunday.
`send_days` is weekdays only, so nothing sends over the weekend and the whole
backlog lands at once.

| Day | Sends | What |
|---|---:|---|
| Mon Sept 7 | ~46 | 30 × step 5, 9 × step 4, 7 × step 3 |
| Tue Sept 8 | ~4 | step 4, the remainder |
| Wed onward | 0 | Nothing left to send |

> **After Tuesday the email channel is finished.**
> Thirty of Monday's sends are step 5, the breakup email, which promises to stop
> emailing. Nothing may follow it. 58 of 61 leads will be done, and every
> scheduled run after that sends zero until new leads are imported.

### The three replies, ever

| Who | When | What they said | Status |
|---|---|---|---|
| London Mechanical (Mary-Lynn) | Aug 13 | "Not anything we do, but thank you." | Suppressed, whole domain |
| Russell, Thomson Plumbing | Aug 17 | `stop` | Suppressed, whole domain |
| Greg Iwankow, Rusty Pipes | Sept 1 | **Unread** | Out of sequence, not suppressed |

### Suppression list

```
lonmech@ody.ca                  replied, not a fit, declined politely 2026-08-13
lynn@londonmechanical.ca        same company as lonmech@ody.ca
mary-lynn@londonmechanical.ca   replied to decline 2026-08-13
@londonmechanical.ca            whole domain
russell@thomsonplumbing.ca      replied STOP 2026-08-17
@thomsonplumbing.ca             whole domain
```

Note that `lonmech@ody.ca` correctly got no domain-level suppression — `ody.ca`
is a shared ISP domain and sits in `SHARED_DOMAINS`.

### The free-offer send, an untracked event

On Aug 20, `offer.yml` run #2 sent `offer_free` to exactly four addresses. Run #1
was the dry run. Run #2 took 32 minutes for four sends because the gaps were still
486–796 seconds at that point.

| Email | Business | City |
|---|---|---|
| info@neumannplumbing.ca | Neumann Plumbing | Edmonton AB |
| admin@theplumbineers.com | Plumbineers Plumbing & Heating | Red Deer AB |
| info@nickelplumbing.com | Nickel Plumbing & Heating | Saskatoon SK |
| bobby2213@hotmail.com | Favoured Plumbing & Heating | Moncton NB |

Two things follow from this. It went to four leads, not to every non-replier — if
the intent was the whole non-replying list, that never happened. And the database
has no record of it, because `offer.yml` does not commit state. All four
continued through the normal sequence and are now at step 4, so each received a
"free site" offer on Aug 20 and a "$1,500 to build it" email afterwards, with
nothing connecting the two. None of them replied.

### All 50 active leads

Every one of these has a phone number that has never been dialled. Rows marked
**†** also appear on the SMS list — do not run both channels at the same
business.

| ID | Business | City | Pr | Phone | Step |
|---:|---|---|---|---|---:|
| 14 | Neumann Plumbing | Edmonton | AB | 780-429-0295 | 4 |
| 12 | Simpson Plumbing | Lethbridge | AB | 403-328-3584 | 4 |
| 59 | Berger's Plumbing & Company | Medicine Hat | AB | 403-528-2082 | 2 |
| 45 | KAT Plumbing & Gas Fitting | Medicine Hat | AB | — | 3 |
| 13 | Plumbineers Plumbing & Heating | Red Deer | AB | 403-302-7606 | 4 |
| 47 | Kris Howe's Plumbing & Gas | Wetaskiwin | AB | 780-361-8645 | 3 |
| 32 | Armacom Plumbing | Abbotsford | BC | 604-329-4009 | 4 |
| 36 | Fairfield Island Plumbing & Heating | Chilliwack | BC | 604-793-9395 | 4 |
| 28 | Dean's Plumbing & Heating | Cranbrook | BC | 250-489-1803 | 4 |
| 60 | **† Bugaboo Plumbing Company** | Golden | BC | 250-439-9119 | 2 |
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
| 55 | **† All Hours Plumbing & Heating** | Sydney | NS | 902-564-1852 | 2 |
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
| 51 | **† Smitty's Plumbing** | Simcoe | ON | 519-428-6250 | 3 |
| 39 | Complete Plumbing | St. Catharines | ON | — | 4 |
| 61 | **† Water Tight Plumbing & Heating** | Charlottetown | PE | 902-621-0667 | 2 |
| 41 | Super Service Plumbing & Heating | Prince Albert | SK | 306-960-0082 | 3 |
| 23 | Able Plumbing & Heating | Regina | SK | 306-569-0047 | 4 |
| 24 | Nickel Plumbing & Heating Ltd. | Saskatoon | SK | 306-653-1899 | 4 |
| 49 | Swift Plumbing and Heating | Swift Current | SK | 306-778-2830 | 3 |

### Where the leads came from

Thirteen research spreadsheets sit in Google Drive, built in waves through
August. The progression is worth knowing, because it shows what was already
tried.

| Date | Sheet | What it was |
|---|---|---|
| Aug 5 | Canada-Wide, then v2 verified | First pass, then re-checked |
| Aug 8 | Canada-Wide (50 total) | The core email list |
| Aug 19 | Quality-Audited (Canada Only) | Filtered for real addresses |
| Aug 19 | Batch 2, 3, 4 | Top-ups from social search |
| Aug 19 | Social Media, v2, Instagram sets | Instagram and Facebook sourcing |
| Aug 23 | Text-Friendly (Small/Solo Operators) | The SMS list. Section 02 |

### CASL compliance

Canada's Anti-Spam Legislation. This is cold business-to-business email to
Canadian companies, so it matters.

- **Consent basis:** implied consent through conspicuous publication. These are
  business addresses published publicly for the purpose of being contacted, and
  the message is relevant to that business.
- **Mailing address:** mandatory in every commercial email, present in config and
  rendered into every send. `send` refuses to run while any sender or template
  value still contains the string `TODO`.
- **Unsubscribe:** every footer says "Reply STOP." The IMAP watcher suppresses on
  detection, well inside the ten business days the law allows.
- Suppression is permanent and stored in the committed database.

### Analytics

GA4 is live on the demo site, property `G-LQPHPNP2QT`, configured in
`templates/regina-plumbing/lib/client.config.ts`. The build succeeds, the tag
reaches the built output, and the consent defaults plus the gtag loader land in
the same JS chunk in source order, so nothing is stored before consent. Consent
Mode v2 with a banner, for PIPEDA.

Custom events `phone_call_click` and `generate_lead` are wired up. GA4's enhanced
measurement does not capture `tel:` taps, so phone clicks needed explicit
instrumentation.

Still to do, both clicks in the GA4 web interface rather than code: accept the
consent banner on the live demo and confirm the hit appears in Realtime, then
mark both custom events as key events under Admin → Events. If Realtime shows
nothing, try a different browser — ad blockers block the GA script.

### Things deliberately refused

Recorded so they do not get quietly reintroduced.

| Proposed | Why it was refused |
|---|---|
| Prompt injection in emails, to manipulate recipients' AI tools | Deceptive, and it would poison the relationship the moment it was noticed |
| Faster or incentivized Google reviews in exchange for the free build | Violates Google's review policy. Risks the plumber's own profile, not just yours |
| Fake scarcity caps, "only 3 spots left" | Not true |
| Fake discount badges | Not true |

The honesty is load-bearing. The whole pitch is "I built you a thing, look at
it." It only works coming from someone who is obviously not running a playbook.

---

## 02 — Cold SMS

A different offer from the email campaign, and a better one: the site completely
free, in exchange for a portfolio piece.

> "I'm basically not here… I could just build a website, and I could go away
> after. 'Hi, this is me. I built websites. I'll build you one for free. No
> charge, no bullshit. I just need you guys to be in my portfolio.'"

And on why it is worth doing at a loss:

> "I will do one free one. Cause I have a really solid idea in my head. I feel
> like this will also help me do cold calls much more."

Two rules were set explicitly. Leave the monthly out of it — "I'm just gonna give
them the site." And do not force it — "I don't want to force it on them."

### Why SMS, and the risk that was accepted

SMS gets read. Email from an unknown teenager to a plumbing company mostly does
not, and 218 sends with three replies is the proof.

The blocker: proper A2P messaging is not an option. Twilio and every compliant
provider prohibit cold SMS outright in their acceptable-use policies. There is no
legitimate service that will send this.

Which leaves texting from a personal phone. That was raised, considered, and
accepted:

> "SMS. What am I losing? Private number. It's like I'm too small of a business
> right now, so it won't really matter until it gets bigger."

**What that actually costs, so it is not a surprise later.** The personal number
is disclosed to every recipient, permanently. They can look it up, save it, share
it, or complain about it. Carrier-level spam flagging is possible if enough
people report it, which would affect ordinary personal texting too. And there is
no unsubscribe infrastructure, so opt-outs have to be honoured by hand.

**Mitigations in force:** send few, send slowly, personalize every single one with
a real mockup of their business rather than a blast, stop immediately on any
negative reply, and never text the same person twice.

### The list

Source: the Google Sheet "Plumbing Leads — Text-Friendly (Small/Solo Operators)",
created Aug 23. Selection criterion was businesses where the person answering the
phone is almost certainly the owner. Signals used were tiny Google review counts,
no website, a business named after a person, recent incorporation, and public
evidence the owner handles their own messages.

22 rows. One scratched, one texted, twenty remaining.

| Business | City | Pr | Phone | Rev | Why text-friendly |
|---|---|---|---|---:|---|
| Parker Plumbing Ltd | West Kelowna | BC | 778-392-7203 | — | **Scratched** — already has a good site |
| Bugaboo Plumbing Company | Golden | BC | 250-439-9119 | 1 | Only 1 review, near-certain one-person shop |
| Sewer King | Swift Current | SK | 306-741-0479 | 9 | Owner Les Smid posts from a personal Facebook profile, not a business page |
| Skalicky's Plumbing | Revelstoke | BC | 250-837-6271 | 7 | Tiny review count, big casual IG following, very personal voice |
| All Hours Plumbing & Heating | Sydney | NS | 902-564-1852 | 10 | Registered 2018, small |
| Jaguar Plumbing & Heating | Creston | BC | 250-254-2222 | 10 | Old website domain now dead |
| Vance Plumbing and Heating | New Glasgow | NS | 902-752-3205 | 11 | Very small review count, no website |
| Duffy's Plumbing | Corner Brook | NL | 709-632-4501 | 15 | Small local, no website, has Facebook |
| Smitty's Plumbing | Simcoe | ON | 519-428-6250 | 15 | Named owner-operator Jeff Smith, personal email |
| Cody Mackay Plumbing | Pembroke | ON | 613-281-5232 | 15 | Named after one owner, incorporated 2021, young solo operator |
| E & R Plumbing & Heating | Miramichi | NB | 506-773-4900 | 15 | Small family operation, no website |
| Rusty Pipes Plumbing Repairs | East Selkirk | MB | 204-294-4089 | 14 | Owner Greg Iwankow — **replied to the email Sept 1** |
| Dow's Plumbing & Heating | Charlottetown | PE | 902-314-6262 | 14 | Website domain dead, has Facebook |
| Limestone Mechanical | Canmore | AB | 403-707-7212 | 14 | Small despite active Instagram |
| L. E. Steele Drain Solutions | Charlottetown | PE | 782-772-8188 | 17 | Named owner Geoffrey Steele, registered 2024, brand new |
| Lupien Jean Plumbing | Cornwall | ON | 613-938-5700 | 20 | Named after owner Jean Lupien, no website |
| Water Tight Plumbing & Heating | Charlottetown | PE | 902-621-0667 | 21 | Domain is an expired parked page |
| Clockwork Plumbing & Gas | Camrose | AB | 780-781-7622 | 21 | Named owner Travis Csernyanszki, small |
| Austin's Plumbing | Camrose | AB | 780-781-2795 | 40 | **Texted Aug 20.** Owner said publicly his IG Messenger is unreliable |
| D.P. Drain Plumbing | Toronto | ON | 437-577-2043 | N/A | ~162 IG followers in a Toronto market, one direct line not a dispatch number |
| First Choice Plumbing & Heating | Timmins | ON | 705-267-1115 | 5 | Backup, lower confidence |
| Pembina Valley Plumbing & Heating | Winkler | MB | 204-331-3031 | 7 | Backup, lower confidence |

### Conflicts with the email campaign

Four of these businesses are currently active in the email sequence. Texting them
while they are also being emailed makes the whole thing look like a mass-mailing
operation, which is exactly the impression the copy works to avoid.

| Business | Email ID | Email step | Action |
|---|---:|---|---|
| Bugaboo Plumbing Company | 60 | 2 | Pick one channel |
| All Hours Plumbing & Heating | 55 | 2 | Pick one channel |
| Smitty's Plumbing | 51 | 3 | Pick one channel |
| Water Tight Plumbing & Heating | 61 | 2 | Pick one channel |
| Rusty Pipes Plumbing Repairs | 53 | out | Read Greg's reply first |

**The rule:** pull them from the email sequence before texting, or do not text
them. One channel per business, never both.

### Two to verify before texting

Same town, possibly the same family business under a different name. These read
as distinct businesses, but the surnames and towns line up closely enough to
check first.

- **Cody Mackay Plumbing** (Pembroke ON) against email lead **#58 Brendon Mackay
  Plumbing & Heating**, also Pembroke.
- **Lupien Jean Plumbing** (Cornwall ON) against email leads **#44 Aurele
  St. Jean Plumbing** and **#43 EverFlow Plumbing**, both Cornwall.

### The script

Sent as one single message with the mockup attached. That was an explicit
requirement: "the text should be all in one message."

Constraints it has to satisfy: one message rather than a sequence; no em dashes,
same rule as the email; sounds like a person typing on a phone, not a marketer;
includes the demo link; free, no monthly, no pressure. And no review incentive —
the original idea included asking for a faster Google review in exchange, which
was removed because incentivized reviews violate Google's policy and put the
plumber's own profile at risk.

```
Hey [name], I'm Srijan, I build websites out of Regina. I made a homepage
for [Business] to see how it'd look. Screenshot attached.

I'm doing a few of these free right now because I need real companies in my
portfolio. No charge, nothing monthly, I just want to be able to show it.

Here's a finished one you can click around: demo.ghoshdesigns.ca

If you want yours built out let me know, and if not no worries at all.
```

> **Verify this before reusing it.** The exact wording sent to Austin's on Aug 20
> lived in chat, not in a repo. What is above is reconstructed from the
> constraints. Check the sent messages so text #2 through #21 match text #1.

### Mockups

62 generated screenshots live in `outreach/mockups/*.jpg`, named by slugified
business — for example `rusty-pipes-plumbing-repairs.jpg`. They are produced by
`shoot.py`: Playwright drives Chromium against the demo site served locally by
`serve.py`, with the business's real details substituted in, then Pillow
optimizes to under 250 KB.

Not every SMS lead has one there — that folder covers the email leads. SMS-only
leads had mockups made separately. Check for a file before texting; if there is
none, generate one first. A text without the screenshot has no reason to be read.

**Known unsolved problem:** getting the images onto the phone. Raised more than
once. Options if it recurs: email them to yourself and save from the Gmail app,
or put them in Google Drive or Photos and save from there.

### The sending schedule

Set after high school started. The real constraint is that after school is not
realistic and should not be planned around: up at 7:00, and 8:00 is the latest
anything can go out.

That window turns out to be the best hour on the whole list, because
Saskatchewan does not observe daylight saving.

| Region | Local time at 7:30 am Regina | Verdict |
|---|---|---|
| British Columbia | 6:30 am | Too early |
| Alberta | 7:30 am | Too early |
| Manitoba | 8:30 am | Workable |
| Ontario | 9:30 am | Ideal |
| Maritimes | 10:30 am | Ideal |
| Newfoundland | 11:00 am | Ideal |

So the eastern half of the list fits the morning window perfectly and the western
half needs a weekend.

| When | Who |
|---|---|
| Mon am | Cody Mackay (Pembroke ON) · Lupien Jean (Cornwall ON) · E & R (Miramichi NB) |
| Tue am | D.P. Drain (Toronto ON) · Vance Plumbing (New Glasgow NS) · Duffy's (Corner Brook NL) |
| Wed am | Dow's (Charlottetown PE) · L.E. Steele (Charlottetown PE) · First Choice (Timmins ON) |
| Thu am | Pembina Valley (Winkler MB), which works at 8:30 local |
| Saturday 10 am – 4 pm | Sewer King · Skalicky's · Clockwork · Limestone · Jaguar. Alberta and BC are only 0–1 hours behind, so a midday session covers all of them |
| Held back | Bugaboo, All Hours, Smitty's, Water Tight, Rusty Pipes — pending the channel conflicts above |

Three texts is about ten minutes. If a morning gets away from you, skip it — two
a day still finishes the list inside a week.

---

## 03 — Open items

Everything outstanding, in the order it should be dealt with.

### Before Monday 07:23 Regina

- [ ] **Read Greg Iwankow's reply at Rusty Pipes, dated Sept 1.** The only live
  thread in the operation. The Gmail connector needs re-authorizing before an AI
  session can read it, so check by hand or reconnect Gmail in the claude.ai
  connector settings.
- [ ] **Fix "before September" in `step4_price.txt` and `offer_free.txt`.**
  Thirteen leads receive step 4 on Monday and Tuesday with a deadline that has
  already passed. Delete the sentence or replace it with something true. This is
  exactly the kind of false claim the rest of the copy was cleaned up to remove.

### This week

- [ ] Decide what happens when the list runs dry on Tuesday: import a new batch of
  leads, or stop email and put the time into calls.
- [ ] Start the SMS mornings.
- [ ] Resolve the four channel conflicts, pulling them from email if texting.
- [ ] Check Cody Mackay and Lupien Jean against the Pembroke and Cornwall email
  leads.
- [ ] Confirm a mockup image exists for each of the twenty before texting, and
  solve getting images onto the phone.
- [ ] GA4: accept the banner on the live demo, confirm Realtime shows the hit, mark
  both custom events as key events.
- [ ] Consider a single follow-up to Austin's, texted Aug 20 and never followed up.

### Standing gaps

- **Nobody has ever been phoned.** Roughly sixty numbers across both lists. Cold
  calling was the original reason for wanting a portfolio piece.
- **There is no process for a yes.** Nothing written covers what happens when
  someone actually says yes: what to ask them for, what the build looks like day
  to day, how they pay, or what the first invoice says. Worth writing before it is
  needed rather than during.
- **Reply to Lynn at London Mechanical.** Drafted, never sent. She is suppressed,
  so this is courtesy only, not outreach.
- **`offer.yml` writes no campaign state,** so manual sends are invisible to the
  database and to the sequence logic. Worth fixing if manual sends become routine.
- **The four leads who got the free offer on Aug 20** later received the $1,500
  price email with nothing connecting the two. Worth a sentence if any of them
  ever replies.

---

## 04 — Reference

Commands, schema, runbook, and the vocabulary this project uses.

### CLI commands

All run as `python3 src/cli.py <command>` from the `outreach/` directory.

| Command | What it does |
|---|---|
| `import` | Load leads from CSV |
| `audit` | Score each lead's current site |
| `mockups` | Render a personalized mockup per lead |
| `daily` | audit + mockups + replies + send. This is what the cron runs |
| `send` | Send whatever is due |
| `replies` | Scan the inbox and stop sequences |
| `doctor` | Check everything and say what to fix |
| `status` | Print counts, allowance, window state |
| `fetch-template` | Download the demo site locally |
| `find-leads` | Search Places and build `leads.csv` |
| `find-emails` | Fill blank emails from company sites |
| `offer` | Send one template to named addresses |
| `suppress` | Never contact this address again |

`send` and `daily` both accept `--dry-run` to print the emails without sending,
and `--ignore-window` to send outside the configured hours.

### Database schema

One SQLite file, no server, committed to the repo after every run. From `db.py`:
"The suppression table is the important one. Getting that wrong is what turns
cold outreach into a complaint."

```sql
CREATE TABLE leads (
  id            INTEGER PRIMARY KEY,
  business      TEXT NOT NULL,
  contact_name  TEXT DEFAULT '',
  email         TEXT NOT NULL UNIQUE,
  domain        TEXT DEFAULT '',
  phone         TEXT DEFAULT '',
  city          TEXT DEFAULT '',
  province      TEXT DEFAULT '',
  review_count  INTEGER DEFAULT 0,
  audit_score   INTEGER,
  audit_flags   TEXT DEFAULT '',
  audit_line    TEXT DEFAULT '',
  mockup        TEXT DEFAULT '',
  status        TEXT NOT NULL DEFAULT 'new',   -- new|queued|active|replied|done|skipped
  created_at    TEXT NOT NULL
);

CREATE TABLE events (
  id       INTEGER PRIMARY KEY,
  lead_id  INTEGER NOT NULL REFERENCES leads(id),
  kind     TEXT NOT NULL,          -- sent|replied|bounced|unsubscribed|error
  step     INTEGER,
  at       TEXT NOT NULL,
  detail   TEXT DEFAULT ''
);

CREATE TABLE suppression (
  email   TEXT PRIMARY KEY,        -- or "@domain" for a whole company
  reason  TEXT NOT NULL,
  at      TEXT NOT NULL
);
```

The CSV that feeds `import` has one header row and these columns:

```
business,contact_name,email,domain,phone,city,province,review_count
```

Only `business` and `email` are required. A blank `contact_name` makes the
greeting fall back gracefully rather than saying "Hey ,".

### Runbook

| You want to… | Do this |
|---|---|
| Send a manual one-off email | Actions → `offer` → Run workflow. Set template, comma-separated recipients, dry-run first. Remember it writes no state |
| Add new leads | Edit `outreach/leads.csv` and push, or run `find-leads` after widening the cities in config. The schedule picks up new rows and starts them at step 1 |
| See what happened today | Actions → `outreach` → newest run → the Campaign status step |
| Pause everything | Disable the `outreach` workflow in the Actions tab |
| Pull one lead out | Add their address to the suppression table, or set their status to `skipped` |
| Change the copy | Edit the file in `outreach/templates/` and push to `main`. It takes effect on the next run. Re-read the voice rules first |

### Reading a run log

```
ramp allowance 46/day · already sent today 0 · budget now 46 · due 0
```

"due 0" is usually not a bug. It means no lead has a step whose delay has
elapsed. Between waves this is completely normal. Check the same line's budget
before assuming anything is broken — a budget of 0 means the cap is spent, which
is a different problem from nothing being due.

| Symptom | Likely cause |
|---|---|
| Runs green, nothing sending | Nothing due yet, or the whole list is done |
| Runs failing in ~2 seconds, no steps | Actions minutes exhausted. Check billing |
| `BadCredentials` from SMTP | Usually an IP block, not a bad password |
| Someone got the same email twice | A state commit was lost. Check the persist step pushed |
| Run started outside the window | GitHub delayed the schedule. That is why there are four |
| Someone who said no got another email | Check the suppression table, and whether IMAP is authenticating |

### Glossary

| Term | Meaning |
|---|---|
| SPF / DKIM / DMARC | Three DNS records that together let a receiving server prove mail claiming to be from your domain really is. Without them cold mail goes to spam |
| CASL | Canada's Anti-Spam Legislation. Requires consent, a real mailing address, and a working unsubscribe |
| A2P | Application-to-person messaging, i.e. software sending SMS. Providers prohibit cold outreach over it |
| Warm-up ramp | Slowly increasing daily volume so a new sending domain does not look like a spam cannon on day one |
| Suppression | The permanent do-not-contact list. Checked before every single send |
| Concurrency group | A GitHub Actions setting that stops two runs of the same workflow overlapping |
| Step | One email in the five-message sequence, tracked per lead |
| Due | A lead whose next step's delay has fully elapsed |
| Mockup | The generated homepage screenshot attached to step 1 |
| Consent Mode v2 | Google's system for withholding analytics data until the visitor accepts the banner |

---

*Ghosh Designs · Regina SK · state captured 2026-09-04 from the live campaign
database.*
