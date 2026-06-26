#!/usr/bin/env python3
"""
BlueLine Plumbing — static site build.

Why a build step? It keeps one source of truth for the header/footer/<head>
and data-generates the repetitive local-SEO city pages and service pages, so
the site stays consistent and there are no broken links. Output is plain static
HTML (no runtime/JS framework) that any static host can serve.

Usage:  python3 build.py
Serve:  python3 -m http.server 8000   (then open http://localhost:8000)
"""
import os, re, html, pathlib, datetime

ROOT = pathlib.Path(__file__).parent.resolve()
SRC = ROOT / "src"
SITE_URL = "https://www.bluelineplumbing.ca"
DEFAULT_OG = "https://images.pexels.com/photos/6419128/pexels-photo-6419128.jpeg?auto=compress&cs=tinysrgb&w=1200"

HEADER = (ROOT / "partials" / "header.html").read_text(encoding="utf-8")
FOOTER = (ROOT / "partials" / "footer.html").read_text(encoding="utf-8")

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w={w}{extra}"
def pexels(pid, w=900, h=None):
    extra = f"&h={h}&fit=crop" if h else ""
    return PEX.format(id=pid, w=w, extra=extra)

# --------------------------------------------------------------- page shell --
HEAD_TMPL = """<!DOCTYPE html>
<html lang="en-CA">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <meta name="description" content="{description}" />
  <meta name="theme-color" content="#0A2540" />
  <link rel="canonical" href="{site}{canonical}" />
  <meta property="og:type" content="website" />
  <meta property="og:title" content="{title}" />
  <meta property="og:description" content="{description}" />
  <meta property="og:image" content="{ogimage}" />
  <meta property="og:url" content="{site}{canonical}" />
  <meta name="twitter:card" content="summary_large_image" />
  <link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml" />
  <link rel="manifest" href="/site.webmanifest" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Oswald:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="/assets/css/styles.css" />
{extra_head}</head>
<body{bodyclass}>
<a class="skip-link" href="#main">Skip to content</a>
"""

SCRIPT = '<script src="/assets/js/main.js" defer></script>\n'

def parse_frontmatter(text):
    meta, body = {}, text
    m = re.match(r"<!--PAGE\s*(.*?)-->\s*(.*)", text, re.S)
    if m:
        block, body = m.group(1), m.group(2)
        for line in block.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, body

def render(meta, body):
    layout = meta.get("layout", "marketing")
    head = HEAD_TMPL.format(
        title=meta.get("title", "BlueLine Plumbing"),
        description=meta.get("description", ""),
        canonical=meta.get("canonical", "/"),
        site=SITE_URL,
        ogimage=meta.get("ogimage", DEFAULT_OG),
        extra_head=meta.get("extra_head", ""),
        bodyclass=(' class="%s"' % meta["bodyclass"]) if meta.get("bodyclass") else "",
    )
    if layout == "bare":
        return head + body + "\n" + SCRIPT + "</body>\n</html>\n"
    return head + HEADER + "\n" + body + "\n" + FOOTER + "\n</body>\n</html>\n"

def write(out_rel, content):
    out = ROOT / out_rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")
    return out_rel

urls = []

# --------------------------------------------------------- author src pages --
def build_src():
    for path in sorted(SRC.rglob("*.html")):
        rel = path.relative_to(SRC)
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        write(str(rel), render(meta, body))
        if meta.get("canonical"):
            urls.append(meta["canonical"])

# ------------------------------------------------------------- service data --
CHECK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>'
ARROW = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>'

SERVICES = {
  "blocked-drains": {
    "name": "Blocked Drain Clearing", "from": "$149", "img": 6419128,
    "icon": '<path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>',
    "tagline": "Blocked sink, toilet or sewer? Cleared fast — and kept clear.",
    "intro": "A blocked drain never picks a good time. Our plumbers clear blockages at the source with high-pressure water jetting and confirm the fix with a CCTV camera, so you’re not paying for a guess. Most domestic blockages are cleared on the first visit.",
    "points": [
      "High-pressure water jetting that cuts through grease, roots and scale",
      "CCTV drain camera inspections with footage shared to you",
      "Tree-root removal and recurring-blockage solutions",
      "Pipe relining options to avoid digging up your yard",
      "Fixed price quoted before we start — no metered surprises",
    ],
    "faqs": [
      ("How much does it cost to clear a blocked drain?", "Most domestic blockages are cleared from $149. Your plumber confirms a fixed price after a quick look — heavier jetting or root removal is quoted up front before any work."),
      ("Can you tell me why it keeps blocking?", "Yes. Our CCTV camera shows exactly what’s going on inside the pipe — roots, collapse, grease or a belly — and we share the footage so you can see it too."),
      ("Do you offer no-dig repairs?", "Where suitable we use pipe relining to repair pipes from the inside, avoiding the cost and mess of excavating your garden or driveway."),
    ],
  },
  "hot-water": {
    "name": "Hot Water Systems", "from": "$320", "img": 3173206,
    "icon": '<path d="M14 2v6a2 2 0 0 0 .24.97l2.52 4.55A4 4 0 0 1 13.27 20H10.7a4 4 0 0 1-3.49-6.48L9.76 8.97A2 2 0 0 0 10 8V2"/><line x1="8" y1="2" x2="16" y2="2"/>',
    "tagline": "No hot water? We’ll usually have it back the same day.",
    "intro": "Whether it’s a pilot light that won’t hold, a leaking tank or a unit that’s simply had its day, BlueLine repairs and replaces every type of hot water system. We stock the major brands on the van, so most repairs and like-for-like swaps are done same day.",
    "points": [
      "Gas, electric, heat-pump and tankless (continuous-flow) systems",
      "Same-day repairs and replacements in most cases",
      "We handle up to $1,000 in BC efficiency rebates for you",
      "Old unit removed and responsibly recycled at no extra cost",
      "Right-sizing advice so you never run cold again",
    ],
    "faqs": [
      ("My hot water is gone — is it an emergency?", "If you have no hot water at all, call us and we’ll prioritise you, often same day. A leaking tank can cause water damage, so shut off the isolation valve and get in touch right away."),
      ("Should I repair or replace?", "If your system is under ~8 years old, repair is usually worth it. Older than that, a replacement is often cheaper over time and far more efficient. We’ll give you honest numbers both ways."),
      ("Do you handle the rebate paperwork?", "Yes — we’ll tell you which BC and federal rebates you qualify for and handle the paperwork so the discount comes off your price."),
    ],
  },
  "emergency-plumbing": {
    "name": "24/7 Emergency Plumbing", "from": "$180", "img": 6419128,
    "icon": '<path d="M13 2 3 14h7l-1 8 11-12h-7z"/>',
    "tagline": "A real plumber on the line, day or night — at your door within 60 minutes.",
    "intro": "Burst pipe? Sewer backing up? Gas smell? When water (or worse) is where it shouldn’t be, every minute counts. BlueLine runs a genuine 24/7 emergency line, 365 days a year, with fully stocked vans ready to roll across Greater Vancouver.",
    "points": [
      "Answered by a real plumber, not a call centre — any hour",
      "60-minute target response across the Lower Mainland",
      "Burst pipes, blocked sewers, no hot water, gas leaks, flooding",
      "We’ll talk you through shutting off water or gas while we drive",
      "Upfront emergency pricing — quoted before we start",
    ],
    "faqs": [
      ("What should I do right now?", "For a burst pipe, turn off your main water valve (usually at the meter or where the line enters the house). For a gas smell, leave the property and call us from outside. Then phone our 24/7 line and we’ll guide you."),
      ("Do you charge extra at night?", "We quote an upfront price before any work, including after-hours. No vague hourly meters — you approve the number first."),
      ("How fast can you really get here?", "Our target is 60 minutes anywhere in Greater Vancouver, and we keep you updated with live ‘plumber on the way’ texts."),
    ],
  },
  "gas-fitting": {
    "name": "Licensed Gas Fitting", "from": "$180", "img": 6419128,
    "icon": '<path d="M8.5 14.5A4.5 4.5 0 0 0 13 19c2.5 0 4.5-2 4.5-4.5 0-2-1-3.5-2.5-5.5-.5 1-1.5 1.5-2.5 1.5 0-2-1-4-3-5 .5 3-1.5 4.5-2.5 6.5a4.5 4.5 0 0 0 .5 2.5z"/>',
    "tagline": "Safe, certified gas work — cooktops, heaters, BBQ points and leak repairs.",
    "intro": "Gas is not a DIY job. Our licensed gas fitters install, service and certify gas appliances to BC code, and respond fast to suspected gas leaks. Every job is tested and documented so you have proof it’s safe.",
    "points": [
      "Cooktop, oven and heater installation and connection",
      "BBQ and outdoor gas point installation",
      "Gas leak detection and emergency make-safe",
      "Compliance certificates issued on completion",
      "Carbon-monoxide safety checks",
    ],
    "faqs": [
      ("I can smell gas — what do I do?", "Don’t switch anything on or off. Open doors and windows if safe, leave the property, and call our emergency line from outside. We’ll make it safe."),
      ("Do you provide a compliance certificate?", "Yes. Every gas job is tested and certified, and we issue the documentation you need for insurance and resale."),
      ("Can you connect my new cooktop?", "Absolutely — we install and certify gas cooktops, ovens, heaters and outdoor BBQ points."),
    ],
  },
  "leak-detection": {
    "name": "Leak Detection", "from": "$160", "img": 9462224,
    "icon": '<circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "tagline": "Find hidden leaks fast — without jackhammering your home to go looking.",
    "intro": "A spiking water bill or a damp patch usually means a hidden leak. We use acoustic and thermal-imaging equipment to pinpoint leaks inside walls and under slabs precisely, so the repair is small and targeted — not destructive.",
    "points": [
      "Acoustic and thermal-imaging leak location",
      "Non-invasive — we find it before we open anything up",
      "Slab leaks, wall leaks, irrigation and pool lines",
      "Detailed report for your insurance claim",
      "Targeted repair that protects your floors and walls",
    ],
    "faqs": [
      ("How do I know I have a hidden leak?", "Common signs are a jump in your water bill, the meter ticking over with all taps off, damp or warm patches on floors, or a musty smell. If in doubt, we can test for you."),
      ("Will you have to break tiles or concrete?", "Our goal is the opposite — we locate the leak precisely first, so any access is as small and targeted as possible."),
      ("Can you help with my insurance claim?", "Yes, we provide a detailed leak-detection report with images that insurers accept."),
    ],
  },
  "bathroom-renovation": {
    "name": "Bathroom & Kitchen Renovations", "from": "$2,500", "img": 6444979,
    "icon": '<path d="M4 12V5a2 2 0 0 1 2-2 2 2 0 0 1 2 2"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M4 12v3a5 5 0 0 0 5 5h6a5 5 0 0 0 5-5v-3"/><line x1="7" y1="20" x2="6" y2="22"/><line x1="17" y1="20" x2="18" y2="22"/>',
    "tagline": "All the plumbing for your reno — roughed-in on time and waterproofed to last.",
    "intro": "Renovating a bathroom, kitchen or laundry? We handle the complete plumbing scope — rough-in, fixtures, waterproofing sign-off and final fit-off — and coordinate cleanly with your builder, tiler and the rest of the trades so your project stays on schedule.",
    "points": [
      "Full rough-in and fit-off for bathrooms, kitchens and laundries",
      "Fixture supply and install, or fit your chosen tapware",
      "Waterproofing and compliance documentation",
      "Tidy coordination with your builder and tiler",
      "Fixed-price quote with a clear scope and timeline",
    ],
    "faqs": [
      ("Do you supply the fixtures or do I?", "Either works. We can supply quality tapware and fixtures at trade pricing, or install items you’ve chosen yourself."),
      ("How long does the plumbing take?", "For a standard bathroom, rough-in is usually 1–2 days and fit-off another day once tiling is done. We give you a clear timeline up front."),
      ("Do you do the waterproofing?", "We handle the wet-area waterproofing and provide the compliance certificate your reno needs."),
    ],
  },
}

def service_page(slug, s):
    canonical = f"/services/{slug}.html"
    urls.append(canonical)
    faqs_html = "".join(
        f'''<div class="faq-item">
          <button class="faq-q" aria-expanded="false" aria-controls="sf{i}" id="sf{i}-b">{q}
            <span class="ico" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg></span>
          </button>
          <div class="faq-a" id="sf{i}" role="region" aria-labelledby="sf{i}-b"><div class="faq-a-inner"><p>{a}</p></div></div>
        </div>''' for i, (q, a) in enumerate(s["faqs"], 1))
    faq_ld = ",".join(
        '{{"@type":"Question","name":{q},"acceptedAnswer":{{"@type":"Answer","text":{a}}}}}'.format(
            q=_json(q), a=_json(a)) for q, a in s["faqs"])
    points = "".join(f'<li>{CHECK} {p}</li>' for p in s["points"])
    related = "".join(
        f'<a class="chip" href="/services/{k}.html">{v["name"]}</a>'
        for k, v in SERVICES.items() if k != slug)
    body = f'''<main id="main">
  <section class="page-hero on-navy">
    <div class="container">
      <nav class="breadcrumbs" aria-label="Breadcrumb" style="color:var(--slate-400)">
        <ol><li><a href="/index.html" style="color:var(--slate-300)">Home</a></li><li><a href="/services.html" style="color:var(--slate-300)">Services</a></li><li>{s["name"]}</li></ol>
      </nav>
      <span class="eyebrow">Plumbing service</span>
      <h1>{s["name"]}</h1>
      <p class="lead" style="color:var(--slate-300)">{s["tagline"]}</p>
      <div class="btn-row mt-6">
        <a href="/book.html" class="btn btn--primary btn--lg">Book this service</a>
        <a href="tel:+16045550188" class="btn btn--ghost btn--lg">Call (604) 555-0188</a>
      </div>
    </div>
  </section>

  <section class="section section--white">
    <div class="container split">
      <div>
        <span class="eyebrow">Overview</span>
        <h2>What’s included</h2>
        <p class="muted">{s["intro"]}</p>
        <ul class="price-list mt-6" style="max-width:34rem">{points}</ul>
        <p class="mt-6"><strong>From {s["from"]}</strong> · fixed price confirmed before work starts.</p>
        <div class="btn-row mt-6">
          <a href="/book.html" class="btn btn--primary">Book online {ARROW}</a>
          <a href="/pricing.html" class="btn btn--ghost">See pricing</a>
        </div>
      </div>
      <div class="media-card">
        <img data-photo loading="lazy" src="{pexels(s["img"], 900, 1000)}" width="900" height="1000" alt="{s["name"]} by a licensed BlueLine plumber." />
      </div>
    </div>
  </section>

  <section class="section section--alt">
    <div class="container container-narrow">
      <div class="section-head center"><span class="eyebrow">Questions</span><h2>{s["name"]} FAQs</h2></div>
      <div class="faq">{faqs_html}</div>
    </div>
  </section>

  <section class="section section--white">
    <div class="container">
      <div class="section-head center"><span class="eyebrow">Explore</span><h2>Other services</h2></div>
      <div class="cluster" style="justify-content:center">{related}</div>
    </div>
  </section>

  <section class="section section--surface">
    <div class="container">
      <div class="cta-band on-navy">
        <div><span class="eyebrow">Book in minutes</span><h2>Need {s["name"].lower()}?</h2><p>Upfront pricing, licensed plumbers, 24/7 availability.</p></div>
        <div class="cta-actions btn-row"><a href="/book.html" class="btn btn--primary btn--lg">Book online</a><a href="tel:+16045550188" class="btn btn--ghost btn--lg">Call now</a></div>
      </div>
    </div>
  </section>

  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Service","name":{_json(s["name"])},"serviceType":{_json(s["name"])},"provider":{{"@type":"Plumber","name":"BlueLine Plumbing","telephone":"+1-604-555-0188"}},"areaServed":"Greater Vancouver","url":"{SITE_URL}{canonical}"}}
  </script>
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{faq_ld}]}}
  </script>
</main>'''
    meta = {"title": f'{s["name"]} | BlueLine Plumbing Greater Vancouver',
            "description": s["tagline"] + " Licensed, insured, upfront pricing. Book online or call BlueLine Plumbing.",
            "canonical": canonical, "ogimage": pexels(s["img"], 1200)}
    write(f"services/{slug}.html", render(meta, body))

def _json(s):
    import json
    return json.dumps(s, ensure_ascii=False)

# ------------------------------------------------------------- city data ----
CITIES = {
  "vancouver": ("Vancouver", "the West End to Kitsilano, Mount Pleasant and East Van", "older character homes with ageing cast-iron and clay drainage"),
  "burnaby": ("Burnaby", "Metrotown, Brentwood and Burnaby Heights", "a mix of high-rise apartments and post-war family homes"),
  "richmond": ("Richmond", "Steveston, Brighouse and City Centre", "low-lying properties where drainage and sump pumps matter"),
  "surrey": ("Surrey", "Guildford, Fleetwood, Newton and South Surrey", "fast-growing suburbs with both new builds and established homes"),
  "coquitlam": ("Coquitlam", "Burquitlam, Maillardville and the Tri-Cities", "hillside homes where hot-water pressure and drainage need know-how"),
  "north-vancouver": ("North Vancouver", "Lonsdale, Lynn Valley and Deep Cove", "North Shore homes dealing with hard runoff and older pipework"),
}

def city_page(slug, data):
    name, areas, note = data
    canonical = f"/locations/{slug}.html"
    urls.append(canonical)
    svc_cards = "".join(
        f'''<a class="card service-card is-interactive" href="/services/{k}.html">
          <span class="icon-box"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">{v["icon"]}</svg></span>
          <h3>{v["name"]}</h3><p>{v["tagline"]}</p>
          <span class="link-arrow card-link">Learn more {ARROW}</span>
        </a>''' for k, v in list(SERVICES.items())[:6])
    body = f'''<main id="main">
  <section class="page-hero on-navy">
    <div class="container">
      <nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="/index.html" style="color:var(--slate-300)">Home</a></li><li><a href="/areas.html" style="color:var(--slate-300)">Service Areas</a></li><li>{name}</li></ol></nav>
      <span class="eyebrow">Local plumbers</span>
      <h1>Plumber in {name}, BC</h1>
      <p class="lead" style="color:var(--slate-300)">Licensed, insured plumbers covering {areas} — with a 60-minute emergency response and upfront, fixed pricing.</p>
      <div class="btn-row mt-6"><a href="/book.html" class="btn btn--primary btn--lg">Book a {name} plumber</a><a href="tel:+16045550188" class="btn btn--ghost btn--lg">Call (604) 555-0188</a></div>
    </div>
  </section>

  <section class="trustbar"><div class="container">
    <span class="trust-item">{CHECK} Licensed &amp; insured</span>
    <span class="trust-item">{CHECK} 24/7 emergency call-outs in {name}</span>
    <span class="trust-item">{CHECK} 25-year workmanship guarantee</span>
    <span class="trust-item">{CHECK} 4.9★ from 612 reviews</span>
  </div></section>

  <section class="section section--white"><div class="container">
    <div class="section-head"><span class="eyebrow">{name} plumbing</span><h2>Your local {name} plumbing team</h2>
    <p class="muted">BlueLine has plumbers working across {name} every day. We know {note}, so we turn up prepared and fix it properly the first time — whether it’s a blocked drain in {areas.split(",")[0]} or a hot water emergency across town.</p></div>
    <div class="grid grid-3">{svc_cards}</div>
  </div></section>

  <section class="section section--alt"><div class="container split">
    <div><span class="eyebrow">Why locals choose us</span><h2>Fast, fair and local to {name}</h2>
      <div class="stack mt-6">
        <div class="value-card"><span class="num">01</span><div><h4>We’re nearby</h4><p>Local vans mean a faster arrival and a plumber who knows {name}.</p></div></div>
        <div class="value-card"><span class="num">02</span><div><h4>Upfront pricing</h4><p>A fixed price approved before we start — no surprises on the {name} invoice.</p></div></div>
        <div class="value-card"><span class="num">03</span><div><h4>Guaranteed work</h4><p>Every job backed by our 25-year workmanship guarantee.</p></div></div>
      </div>
    </div>
    <div class="media-card"><img data-photo loading="lazy" src="{pexels(8978316, 900, 1000)}" width="900" height="1000" alt="A BlueLine plumber ready to help a {name} homeowner." /></div>
  </div></section>

  <section class="section section--surface"><div class="container">
    <div class="cta-band on-navy"><div><span class="eyebrow">{name}, BC</span><h2>Need a plumber in {name} today?</h2><p>Book online in under a minute or call now — 24/7.</p></div>
    <div class="cta-actions btn-row"><a href="/book.html" class="btn btn--primary btn--lg">Book online</a><a href="tel:+16045550188" class="btn btn--ghost btn--lg">Call now</a></div></div>
  </div></section>

  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Plumber","name":"BlueLine Plumbing — {name}","image":"{DEFAULT_OG}","telephone":"+1-604-555-0188","areaServed":{_json(name)},"url":"{SITE_URL}{canonical}","aggregateRating":{{"@type":"AggregateRating","ratingValue":"4.9","reviewCount":"612"}}}}
  </script>
</main>'''
    meta = {"title": f"Plumber in {name}, BC | BlueLine Plumbing — 24/7 Licensed",
            "description": f"Licensed 24/7 plumbers in {name}, BC. Blocked drains, hot water, gas fitting, leak detection and emergencies. Upfront pricing, 4.9★. Book online.",
            "canonical": canonical}
    write(f"locations/{slug}.html", render(meta, body))

# --------------------------------------------------------------- sitemap ----
def sitemap():
    today = datetime.date.today().isoformat()
    seen, items = set(), []
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        pr = "1.0" if u == "/" or u.endswith("index.html") else "0.8"
        items.append(f"  <url><loc>{SITE_URL}{u}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>")
    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
           + "\n".join(items) + "\n</urlset>\n")
    write("sitemap.xml", xml)

if __name__ == "__main__":
    build_src()
    for slug, s in SERVICES.items():
        service_page(slug, s)
    for slug, d in CITIES.items():
        city_page(slug, d)
    sitemap()
    print(f"Built {len(urls)} pages + sitemap.xml")
