# Ghosh Designs Outreach Handoff

**Operations handoff — cold outreach.**

The complete state of the cold-outreach operation: the email engine, the SMS
channel, every bug found and fixed, and what is waiting to be done. Written so
that a person or an AI session with zero prior context can pick this up and keep
going.

| | |
|---|---|
| **Owner** | Srijan Ghosh, Ghosh Designs, Regina SK |
| **State as of** | 2026-09-09, after the Sept 7 run |
| **Source** | Live campaign database, not memory |

| Leads | Emails sent | Replies | Clients | Texts sent | Calls made |
|---:|---:|---:|---:|---:|---:|
| 61 | 268 | 3 | 0 | 1 | 0 |

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

### 02. The sequence was rewritten. — *2026-09-09*

Five steps became four, the offer now leads with a free portfolio build, and
the attached mockup is called a mockup rather than a homepage. Read
[the sequence](#the-sequence) before importing new leads or editing copy. The
stale "before September" deadline that prompted this was deleted on Sept 6,
before the Sept 7 run picked it up.

### 03. The email list is dry. — *Happened Sept 7*

The Sept 7 run sent 50 and hit the daily cap. 38 leads are done, 20 are still
in flight, and every scheduled run from here sends close to zero until new
leads are imported. The sequence was rewritten on Sept 9 for that next batch.

### 04. 20 of 21 SMS leads have never been texted. — *Not started*

One text has gone out, to Austin's Plumbing on Aug 20. No follow-up.

### 05. Nobody has ever been phoned. — *Not started*

Roughly 60 numbers between the email database and the SMS sheet. Cold calling
was the original reason for wanting a portfolio piece.

### The honest summary

The machine works. It is well built, the bugs found in it were real bugs fixed
properly, and it costs nothing to run. It has also produced zero clients from
268 emails and one text — three replies, two of them rejections. About a 1.1%
reply rate and a 0% close rate.

The email channel has had a fair test and the answer is mostly no. The untested
channels are SMS and the phone, and the phone has never been tried at all.

---

## 01 — The email automation

A Python program that runs on GitHub's machines four times each weekday morning.
Nothing depends on a laptop being awake.

For each plumbing company in a database it screenshots a homepage mockup built
for that specific business, emails it to them with a short personal note,
follows up three more times over roughly twelve days, watches the inbox over
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
    ├── templates/                  # the five email bodies
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

**Rewritten 2026-09-09.** Four steps, down from five. Delays are days since the
previous step reached that lead.

| Step | Template | Delay | Subject line |
|---|---|---|---|
| 1 | `step1_mockup` | 0 | made you a homepage mockup for {business} |
| 2 | `step2_look` | 3 d | the mockup I made for {business} |
| 3 | `step3_price` | 4 d | what it normally costs |
| 4 | `step4_close` | 5 d | last one from me |

Step 3 sits before step 4 deliberately. Step 4 promises to stop emailing, so
nothing may follow it. Price had to come first — nobody had ever been told what
this costs, and silence on price is a common reason a warm prospect goes quiet.
Price now also anchors what the free build is worth.

A fifth template, `offer_free`, is not part of the sequence. It is sent by hand
through the offer workflow.

#### What changed, and why

The first version sent 218 emails for three replies and no clients. The rewrite
is not a polish pass, it is four structural changes:

- **It is a mockup, not a homepage.** Saying "I made a homepage for your
  company" overclaims: what is attached is a picture of one. Same asset,
  honest word for it.
- **The free portfolio build leads.** There are no clients and no portfolio,
  which is what the last 268 sends tested. One site free for a real company to
  show, first person to accept gets it. The mockup stays the hook and the free
  build is the reason to act, in that order, because leading with "free" from a
  stranger reads as a scam.
- **`step3_proof` is deleted.** It opened by promising "Last one about the
  site" and then two more emails followed it, and it told twelve leads with no
  website what to check on their website.
- **One ask per email.** The demo link moved from step 1 to step 2, where it
  doubles as attachment recovery: step 2 now says outright that step 1 arrived
  as a JPEG, which is a tap-download-open on a phone and easy to miss.

The fake `re:` subject on step 2 is also gone. `render.py` sets a `Message-ID`
but never `In-Reply-To`, so it was the appearance of a reply rather than an
actual thread, which is the same species as the fake scarcity already refused.

Word count went from 411 across five emails to 329 across four, but most of
that is deleting `step3_proof` rather than tightening prose.

**Template tokens.** `{{first_name}}`, `{{business}}`, `{{sender_email}}`,
`{{website}}`, `{{demo_link?}}`, `{{audit_line?}}`. A token ending in `?` makes
its whole line vanish when the value is empty — which is why leads with no audit
finding do not get a blank gap in the middle of the email.

### The five templates, in full

Live copy as of 2026-09-09. Send counts refer to the slot, not this text:
every template except `step4_close` was rewritten on 2026-09-09, so the
numbers below are what went out under the previous wording.

#### `step1_mockup.txt` — 61 sent under the old step 1 copy

```
Subject: made you a homepage mockup for {{business}}
---
Hey {{first_name}},

I'm Srijan, I build websites out of Regina. Rather than email asking if you
wanted one, I made a homepage mockup for {{business}}.
It's attached.

{{audit_line?}}

It's a mockup, not a live site. The layout is the real part, the wording on
it is placeholder.

I'm building my portfolio, so I'm doing one of these free. No charge, nothing
monthly. I just need a real company I can show people, and the first person
to say yes gets it.

Want me to build yours out?

Srijan
Ghosh Designs, Regina SK
{{sender_email}}
{{website}}
```

#### `step2_look.txt` — 60 sent under the old step 2 copy

```
Subject: the mockup I made for {{business}}
---
Hey {{first_name}},

Sent you a homepage mockup for {{business}}
a few days ago. It came through as an attachment, which is easy to miss on
a phone.

Here's a finished site of the same build you can click around:
{{demo_link?}}

Yours would be that, with your name and your towns on it instead.

If the free build is still open when you reply, it's yours.

Srijan
Ghosh Designs, Regina SK
{{sender_email}}
{{website}}
```

#### `step3_price.txt` — 51 sent as the old step 4

```
Subject: what it normally costs
---
Hey {{first_name}},

In case it helps to know what you'd be getting. This normally runs $1,500 to
build, then $250 a month for hosting and any changes you want, done the same
day you ask.

The portfolio one is free, and if nobody has claimed it by the time you
reply, it's yours.

The mockup for {{business}} is still here either way.

Srijan
Ghosh Designs, Regina SK
{{sender_email}}
{{website}}
```

#### `step4_close.txt` — 38 sent as the old step 5, copy unchanged

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

#### `offer_free.txt` — 4 sent, by hand, never tracked

```
Subject: free one

---
Hey {{first_name}},

Bit of a different offer.

I'm building my portfolio and I'm doing one plumbing site completely free.
No charge, no catch. I just need a real company in it that I can show people.

I already made the homepage mockup for {{business}}, so you'd be the quickest
one for me to finish.

First person to say yes gets it. Reply and I'll start today.

Srijan
Ghosh Designs, Regina SK
{{sender_email}}
{{website}}
```

### Voice rules — these were fought for

Every one of these came from a specific correction. Anyone editing the copy has
to hold them.

- **No em dashes anywhere.** Verified zero across all five templates. They read as
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
  `Inc..` This is now handled in code rather than by rule: `fill()` drops the
  value's trailing period when the template already supplies one, so a new
  template cannot reintroduce it. See the bug entry below.
- **Watch the wrap against long tokens too.** The rule that matters is to break
  the line immediately after `{{business}}`. The longest name on the list is 39
  characters, and without that break step 2 rendered a 101-character line.

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

#### `Inc..` in the first line of the email

**Symptom.** Nine leads carry a legal suffix ending in a period: RANT,
Plumbineers, Hello Plumber, E.T. Mechanical, Allen Mechanical, Nickel,
Bertelsen, Premium and Brendon Mackay. Dropped into `I made a homepage for
{{business}}.` they rendered `Premium Plumbing Inc..` All nine got it in steps
1 and 2 before it was caught.

**Cause.** `render.py` substituted `lead["business"]` raw. The rule had been
"restructure the sentence so no period follows the token", which held only for
as long as everyone remembered it, and it was never applied to steps 1 and 2.

```python
v = str(v)
if v.endswith(".") and text[m.end():m.end() + 1] == ".":
    v = v[:-1]
```

Fixed 2026-09-09. Names without a trailing period are untouched, an ellipsis
after a token keeps all three dots, and a mid-sentence token keeps its period.

#### The audit sentence was never wrapped

**Symptom.** Every step 1 ever sent carried one 103-character line in the middle
of an otherwise hand-wrapped plain-text email.

**Cause.** `{{audit_line?}}` sits alone on its own line and the audit sentences
run to 103 characters, so the substituted value was never re-wrapped.
`resolve_optional` now wraps optional values to 78, skipping anything
containing `://` because a line break inside a URL stops it being clickable.

#### There is no bounce detection at all

**Not fixed.** `bounced` appears in the `events` schema comment and nothing in
the codebase ever writes it. `grep -rn "bounce" src/` returns the schema line
and nothing else. So the zero bounces recorded against 268 sends is not a
clean list, it is the absence of a check.

Combined with plain text by choice (no open pixel) and an untracked demo link,
there is no delivery signal of any kind. 268 sends and the honest answer to
"did anyone read these" is that nobody knows. Worth parsing NDRs in the IMAP
pass, since the machinery to scan the inbox already exists.

#### Why offer sends log as `kind='offer'`

Not a bug, a constraint worth knowing. `last_step()` reads only `'sent'` rows and
computes the next step as `last[0] + 1`. An offer row has `step=None`, so logging
one as `'sent'` would crash the next scheduled run with a `TypeError`.

### Campaign state

Read from the database on 2026-09-09, after the Sept 7 run.

| Status | Count | Meaning |
|---|---:|---|
| `done` | 38 | Finished the sequence |
| `active` | 20 | Still in the sequence |
| `skipped` | 2 | Suppressed, pulled out |
| `replied` | 1 | Wrote back, left the sequence |

| Step | Sent | | Day | Sent |
|---|---:|---|---|---:|
| 1 | 61 | | Aug 10 | 5 |
| 2 | 60 | | Aug 11 | 8 |
| 3 | 58 | | Aug 12 | 8 |
| 4 | 51 | | Aug 13 | 12 |
| 5 | 38 | | Aug 14 | 15 |
| **Total** | **268** | | Aug 17 | 18 |
| | | | Aug 18 | 22 |
| | | | Aug 19 | 8 |
| | | | Aug 20 | 12 |
| | | | Aug 21 | 18 |
| | | | Aug 24 | 34 |
| | | | Sep 1 | 42 |
| | | | Sep 2 | 16 |
| | | | Sep 7 | 50 |
| | | | **Total** | **268** |

The Aug 24 → Sept 1 gap is the Actions quota outage. Sept 7 hit the daily cap
of 50, which is why the backlog did not clear in one run.

Step numbers above are the old five-step sequence. Steps 1 and 2 map to the
same slots in the new one, old step 4 is now step 3, and old step 5 is now
step 4.

#### What the sequence change does to the 20 still active

`cli.py:224` marks a lead done when its next step is not in the configured
sequence, so nothing errors. But the cut from five steps to four lands on the
in-flight leads unevenly:

| Where they were | Count | What now happens |
|---|---:|---|
| Finished old step 4 (price) | 13 | Next would be step 5. There is no step 5, so they are marked done and never receive a breakup email |
| Finished old step 3 (proof) | 7 | Next is the new step 4, the breakup. They skip the price email |

The 13 are leads #41 through #54. If they should still get a closing email,
`offer.yml` sends `step4_close` to a named list in one run, which is exactly
what that workflow is for. It writes no state, but these leads are already
marked done, so there is nothing to record.

> **The email channel is finished for this list either way.** 58 of 61 leads
> are done or nearly so, and every scheduled run sends zero until new leads are
> imported.

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

### Now

- [ ] **Read Greg Iwankow's reply at Rusty Pipes, dated Sept 1.** Still the only
  live thread in the operation, and still unread. The Gmail connector needs
  re-authorizing before an AI session can read it, so check by hand or reconnect
  Gmail in the claude.ai connector settings.
- [ ] **Decide on the 13 leads left without a closing email.** The cut from five
  steps to four means leads #41 through #54 are marked done without receiving a
  breakup. `offer.yml` can send `step4_close` to that list in one run.
- [x] ~~**Fix "before September" in the price and free-offer templates.**~~
  Done 2026-09-06, commit `79f7d64`. Both sentences deleted rather than redated,
  so nothing goes stale again. The Sept 7 run picked up the corrected copy.
- [x] ~~**Fix the `Inc..` bug.**~~ Done 2026-09-09, commit `e67944f`. Handled in
  `fill()` rather than by restructuring sentences, so a future template cannot
  reintroduce it.
- [x] ~~**Rewrite the sequence before importing new leads.**~~ Done 2026-09-09,
  commit `a6cbc30`. Four steps, free portfolio build leads, mockup called a
  mockup.

### This week

- [ ] Import the new batch of leads against the rewritten sequence.
- [ ] Decide whether to add bounce detection before that batch goes out. Right
  now there is no delivery signal of any kind, so a second list would be sent as
  blind as the first.
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
- **No delivery signal of any kind.** No bounce detection, no open tracking, no
  click tracking. 268 sends and nobody can say whether any of them were read.
  This is the largest unknown in the operation and it makes every copy decision
  a guess. Cheapest fix is parsing NDRs during the IMAP pass, which already
  scans the inbox.
- **The mockup is still a JPEG attachment.** It is the one thing that proves the
  whole pitch and it sits behind a tap-download-open on a phone, from a stranger.
  Hosting a page per lead was considered and rejected as too expensive. Step 2
  now names the problem outright, which is a mitigation and not a fix.

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
