#!/usr/bin/env python3
"""BlueLine Plumbing static-site build.

Injects shared header/footer partials, data-generates the city + service pages
and the sitemap, and INLINES css+js into every page so each file is fully
self-contained: renders correctly via file://, on a subpath (GitHub Pages
/repo/), or at a domain root. Internal links are kept relative.

Run:  python3 build.py        ->  writes ./dist/
"""
import os, re, html, datetime, pathlib, shutil

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / "site"
DIST = ROOT / "dist"
CSS  = (SITE / "assets/styles.css").read_text()
JS   = (SITE / "assets/app.js").read_text()

# ----------------------------------------------------------------------------
# BUSINESS DATA  (rename the whole site by editing BIZ)
# ----------------------------------------------------------------------------
BIZ = {
    "name": "BlueLine Plumbing",
    "domain": "https://bluelineplumbing.ca",   # canonical root
    "phone_display": "(604) 555-0188",
    "phone_tel": "+16045550188",
    "email": "hello@bluelineplumbing.ca",
    "address": "1200 Trades Way, Burnaby, BC V5C 0A1",  # PLACEHOLDER
    "licence": "LIC #PL-000000 (PLACEHOLDER)",
    "rating": "4.9",
    "reviews": "612",
    "region": "Greater Vancouver",
    "hours": "Mon–Sun · 24/7 emergency service",
    "year": datetime.date.today().year,
}

# Inline SVG icon set (24x24, currentColor). No emoji icons anywhere.
ICON = {
 "wrench":'<path fill="currentColor" d="M22 7.3a5.5 5.5 0 0 1-7 5.3l-7.6 7.6a2.1 2.1 0 0 1-3-3l7.6-7.6A5.5 5.5 0 0 1 18 2.4l-2.9 2.9 1.6 1.6L19.6 4A5.5 5.5 0 0 1 22 7.3Z"/>',
 "drop":'<path fill="currentColor" d="M12 2s7 7.6 7 12a7 7 0 0 1-14 0c0-4.4 7-12 7-12Z"/>',
 "flame":'<path fill="currentColor" d="M12 2c1 3-2 4-2 7a2 2 0 0 0 4 0c2 1 3 3 3 5a5 5 0 0 1-10 0c0-4 3-6 5-12Z"/>',
 "bolt":'<path fill="currentColor" d="M13 2 4 14h6l-1 8 9-12h-6l1-8Z"/>',
 "search":'<path fill="none" stroke="currentColor" stroke-width="2" d="M10 4a6 6 0 1 1 0 12 6 6 0 0 1 0-12Zm5 11 5 5"/>',
 "bath":'<path fill="currentColor" d="M4 11V6a2 2 0 0 1 4 0M3 11h18v2a5 5 0 0 1-5 5H8a5 5 0 0 1-5-5v-2Zm3 9 1-2m11 2-1-2"/>',
 "shield":'<path fill="currentColor" d="M12 2 4 5v6c0 5 3.4 8.4 8 11 4.6-2.6 8-6 8-11V5l-8-3Zm-1 13-3-3 1.4-1.4L11 12.2l3.6-3.6L16 10l-5 5Z"/>',
 "clock":'<path fill="none" stroke="currentColor" stroke-width="2" d="M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18Zm0 4v5l3 2"/>',
 "dollar":'<path fill="none" stroke="currentColor" stroke-width="2" d="M12 2v20M16 6.5C16 5 14.2 4 12 4S8 5 8 6.8 9.8 9.5 12 10s4 1.2 4 3-1.8 3-4 3-4-1-4-2.5"/>',
 "phone":'<path fill="currentColor" d="M6.6 2.5 9 3l1 4-2 1.5a12 12 0 0 0 5 5L14 11l4 1 .5 2.4a2 2 0 0 1-2 2.6A14 14 0 0 1 4 4.5a2 2 0 0 1 2.6-2Z"/>',
 "pin":'<path fill="currentColor" d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7Zm0 9.5A2.5 2.5 0 1 1 12 6a2.5 2.5 0 0 1 0 5.5Z"/>',
 "star":'<path fill="currentColor" d="m12 2 2.9 6 6.6.6-5 4.3 1.5 6.4L12 16l-5.9 3.3L7.5 13 2.5 8.6 9 8 12 2Z"/>',
 "check":'<path fill="none" stroke="currentColor" stroke-width="2.4" d="m4 12 5 5 11-11"/>',
 "calendar":'<path fill="none" stroke="currentColor" stroke-width="2" d="M4 6h16v15H4zM4 9h16M8 3v4M16 3v4"/>',
 "users":'<path fill="currentColor" d="M8 11a3 3 0 1 0 0-6 3 3 0 0 0 0 6Zm8 0a3 3 0 1 0 0-6 3 3 0 0 0 0 6ZM2 19a6 6 0 0 1 12 0Zm12.5 0a6 6 0 0 1 7.5-5.8A6 6 0 0 0 14.5 19Z"/>',
 "chart":'<path fill="none" stroke="currentColor" stroke-width="2" d="M4 20V4M4 20h16M8 16v-5M12 16V8M16 16v-8"/>',
 "doc":'<path fill="none" stroke="currentColor" stroke-width="2" d="M6 2h8l4 4v16H6zM14 2v4h4M9 13h6M9 17h6"/>',
 "gear":'<path fill="currentColor" d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Zm9 4-2-1 .3-2.2-2-1.2-1.6 1.5-2-.8L12 3l-1.7 2.3-2 .8L6.7 4.6l-2 1.2L5 8 3 9v4l2 1-.3 2.2 2 1.2 1.6-1.5 2 .8L12 21l1.7-2.3 2-.8 1.6 1.2 2-1.2L19 16l2-1Z"/>',
 "truck":'<path fill="none" stroke="currentColor" stroke-width="2" d="M2 5h11v11H2zM13 9h5l3 3v4h-8M6.5 18a1.5 1.5 0 1 0 0 .1M18 18a1.5 1.5 0 1 0 0 .1"/>',
 "menu":'<path fill="none" stroke="currentColor" stroke-width="2" d="M4 7h16M4 12h16M4 17h16"/>',
 "logo":'<path fill="currentColor" d="M12 2s6 6.5 6 11a6 6 0 0 1-12 0c0-1.7.9-3.7 2-5.5C9.5 10 11 11 11 13a2 2 0 0 0 2-2c0-2.5-3-4-1-9Z"/>',
 "mail":'<path fill="none" stroke="currentColor" stroke-width="2" d="M3 5h18v14H3zM3 6l9 7 9-7"/>',
 "home":'<path fill="none" stroke="currentColor" stroke-width="2" d="M4 11 12 4l8 7M6 10v10h12V10"/>',
 "card":'<path fill="none" stroke="currentColor" stroke-width="2" d="M3 6h18v12H3zM3 10h18"/>',
 "lock":'<path fill="none" stroke="currentColor" stroke-width="2" d="M6 11h12v9H6zM8 11V8a4 4 0 0 1 8 0v3"/>',
 "gift":'<path fill="none" stroke="currentColor" stroke-width="2" d="M4 11h16v9H4zM4 7h16v4H4zM12 7v13M12 7a3 3 0 1 1 3-3M12 7a3 3 0 1 0-3-3"/>',
}
def svg(name, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} viewBox="0 0 24 24" aria-hidden="true">{ICON[name]}</svg>'

# Pexels photos (real, free commercial licence). data-cdn = CDN fallback when
# the self-hosted file is absent; see scripts/fetch_images.py + IMAGE_CREDITS.md.
IMG = {
 "hero":      ("family-kitchen.jpg",   "https://images.pexels.com/photos/3935320/pexels-photo-3935320.jpeg?auto=compress&cs=tinysrgb&w=1600", "A happy family together in a bright modern kitchen"),
 "sink":      ("kitchen-sink.jpg",     "https://images.pexels.com/photos/6419128/pexels-photo-6419128.jpeg?auto=compress&cs=tinysrgb&w=900",  "Modern stainless kitchen sink and tap"),
 "boiler":    ("hot-water.jpg",        "https://images.pexels.com/photos/3964736/pexels-photo-3964736.jpeg?auto=compress&cs=tinysrgb&w=900",  "Wall-mounted hot water heating unit"),
 "pipe":      ("pipe-repair.jpg",      "https://images.pexels.com/photos/8487376/pexels-photo-8487376.jpeg?auto=compress&cs=tinysrgb&w=900",  "Plumber repairing pipework under a sink"),
 "flame":     ("gas-flame.jpg",        "https://images.pexels.com/photos/6024314/pexels-photo-6024314.jpeg?auto=compress&cs=tinysrgb&w=900",  "Blue gas flame on a burner"),
 "tap":       ("dripping-tap.jpg",     "https://images.pexels.com/photos/1463917/pexels-photo-1463917.jpeg?auto=compress&cs=tinysrgb&w=900",  "Water dripping from a tap"),
 "bathroom":  ("finished-bath.jpg",    "https://images.pexels.com/photos/6585757/pexels-photo-6585757.jpeg?auto=compress&cs=tinysrgb&w=900",  "Clean finished modern bathroom"),
 "tech":      ("technician.jpg",       "https://images.pexels.com/photos/8487371/pexels-photo-8487371.jpeg?auto=compress&cs=tinysrgb&w=900",  "Smiling plumbing technician with tools"),
 "handshake": ("handshake.jpg",        "https://images.pexels.com/photos/4246119/pexels-photo-4246119.jpeg?auto=compress&cs=tinysrgb&w=900",  "Tradesperson shaking hands with a happy customer"),
 "drain":     ("blocked-drain.jpg",    "https://images.pexels.com/photos/6419122/pexels-photo-6419122.jpeg?auto=compress&cs=tinysrgb&w=900",  "Clearing a blocked drain"),
 "city":      ("vancouver.jpg",        "https://images.pexels.com/photos/2382681/pexels-photo-2382681.jpeg?auto=compress&cs=tinysrgb&w=1200", "Greater Vancouver skyline"),
}
def img(key, cls="", sizes="(max-width:640px) 100vw, 600px", lazy=True, w=900, h=560):
    fn, cdn, alt = IMG[key]
    ld = 'loading="lazy" decoding="async" ' if lazy else ""
    return (f'<img src="images/{fn}" data-cdn="{cdn}" alt="{alt}" '
            f'width="{w}" height="{h}" {ld}class="{cls}">')

# ----------------------------------------------------------------------------
SERVICES = [
 dict(slug="blocked-drains", name="Blocked Drains", icon="drop", photo="drain",
      tag="Fast drain clearing, camera diagnostics & root removal",
      price="from $189",
      blurb="Slow, gurgling or backed-up drains cleared the same day with high-pressure water jetting and CCTV diagnostics.",
      includes=["CCTV camera inspection to find the exact blockage","High-pressure hydro-jet clearing","Root cutting and removal","Drain-flow test and clean-up","Upfront fixed price before we start"],
      faqs=[("How fast can you clear a blocked drain?","Most blockages are cleared in a single visit, usually within an hour of arriving."),
            ("Will you damage my pipes?","No — hydro-jetting cleans the pipe wall without the scoring that old mechanical augers cause. We camera-check first."),
            ("Do you fix recurring blockages?","Yes. Our camera survey finds the root cause — collapsed pipe, tree roots, or grease — so we fix it once, not monthly.")]),
 dict(slug="hot-water", name="Hot Water", icon="drop", photo="boiler",
      tag="Repairs, replacements & tankless upgrades",
      price="from $320",
      blurb="No hot water? We repair, replace and upgrade tank and tankless systems across Greater Vancouver, often same-day.",
      includes=["Diagnosis of gas, electric & tankless units","Same-day repair where parts allow","Energy-efficient tankless upgrades","Permits and code-compliant install","Old unit removal and recycling"],
      faqs=[("Should I repair or replace my hot water tank?","If your tank is over 10 years old or leaking from the body, replacement is usually the better value. We'll give you both numbers."),
            ("Do you install tankless systems?","Yes — gas and electric tankless, fully permitted, with manufacturer-backed warranties."),
            ("Can you come the same day?","For no-hot-water calls we prioritise same-day attendance, subject to parts availability.")]),
 dict(slug="emergency", name="24/7 Emergency", icon="bolt", photo="pipe",
      tag="Genuine round-the-clock response, 60-minute target",
      price="from $149 call-out",
      blurb="Burst pipe, major leak or sewage backup? A licensed plumber answers any hour, with a 60-minute response target across the Lower Mainland.",
      includes=["Live phone answer 24 hours, 7 days","60-minute response target","Water shut-off and damage limitation","Make-safe plus permanent repair options","Transparent after-hours pricing quoted upfront"],
      faqs=[("Is this a real 24/7 line or an answering service?","A real licensed plumber is on call every night and weekend — not just a message taker."),
            ("What should I do while I wait?","Shut off your main water valve and, for gas smells, leave the property and call us from outside."),
            ("Do you charge more at night?","After-hours work carries a higher rate, always quoted and agreed before we begin.")]),
 dict(slug="gas-fitting", name="Gas Fitting", icon="flame", photo="flame",
      tag="Licensed gas work, leak checks & appliance hook-ups",
      price="from $160",
      blurb="Certified gas fitting for stoves, fireplaces, BBQs and heating — installed safely, permitted and leak-tested.",
      includes=["Licensed gas-fitter on every job","Leak detection and pressure testing","Appliance connection and certification","New gas line runs and extensions","Permits arranged on your behalf"],
      faqs=[("Are your gas fitters licensed?","Yes — all gas work is performed by a certified gas fitter and permitted where required by FortisBC and BC code."),
            ("I smell gas — what now?","Leave the building, don't switch anything on or off, and call us from outside immediately."),
            ("Can you connect my gas range or BBQ?","Yes, including new line runs, shut-off valves, and a certified leak test.")]),
 dict(slug="leak-detection", name="Leak Detection", icon="search", photo="tap",
      tag="Non-invasive detection that finds hidden leaks",
      price="from $210",
      blurb="High water bill or damp patch? We pinpoint hidden leaks with acoustic and thermal tools — no guesswork, minimal cutting.",
      includes=["Acoustic and thermal imaging survey","Pinpoint location before any cutting","Slab, wall and underground leaks","Full written findings and repair quote","Repair carried out the same visit where possible"],
      faqs=[("How do you find a leak without tearing up walls?","Acoustic sensors and thermal cameras locate the leak to within centimetres, so we open only where needed."),
            ("My water bill spiked — could it be a leak?","Often, yes. A hidden leak can waste thousands of litres. We can confirm with a meter test."),
            ("Do you repair what you find?","Yes — we quote the repair on the spot and, where access allows, fix it the same visit.")]),
 dict(slug="bathroom-renovations", name="Bathroom Renovations", icon="bath", photo="bathroom",
      tag="Full bathroom plumbing, from rough-in to fixtures",
      price="from $6,500",
      blurb="Renovating? We handle the complete plumbing scope — rough-in, fixtures, and final fit — coordinated to your schedule.",
      includes=["Design consultation and fixture advice","Complete rough-in and waterproofing prep","Toilet, vanity, shower and bath install","Permits and inspection coordination","Workmanship guarantee on all plumbing"],
      faqs=[("Do you handle the whole bathroom?","We cover the full plumbing scope and coordinate with your tiler and electrician, or your own contractor."),
            ("How long does a bathroom take?","Plumbing rough-in and fit-off typically spans the project over 2–4 weeks depending on scope."),
            ("Is the work guaranteed?","Yes — all plumbing workmanship is covered by our 25-year guarantee.")]),
]
SERVICE_BY = {s["slug"]: s for s in SERVICES}

CITIES = [
 dict(slug="vancouver", name="Vancouver", blurb="From Kitsilano character homes to downtown high-rises, our Vancouver crews know the city's older cast-iron stacks and strata requirements inside out.", nbhd=["Kitsilano","Mount Pleasant","Kerrisdale","Downtown","East Van"]),
 dict(slug="burnaby", name="Burnaby", blurb="Burnaby's mix of post-war homes and new towers means everything from clay-pipe drains to modern tankless installs — all in a day's work for our local team.", nbhd=["Metrotown","Brentwood","Capitol Hill","Burnaby Heights"]),
 dict(slug="richmond", name="Richmond", blurb="Richmond's flat, low water-table lots make drainage and sump work a specialty. We service homes and businesses across the city, fast.", nbhd=["Steveston","Brighouse","Hamilton","Broadmoor"]),
 dict(slug="surrey", name="Surrey", blurb="Surrey is growing fast and so are its plumbing needs — new builds, suites, and emergency call-outs across every town centre.", nbhd=["Guildford","Newton","Cloverdale","South Surrey","Fleetwood"]),
 dict(slug="coquitlam", name="Coquitlam", blurb="From the Tri-Cities' hillside homes to Burke Mountain new builds, our Coquitlam plumbers handle pressure, drainage and hot water with ease.", nbhd=["Burke Mountain","Maillardville","Austin Heights","Westwood Plateau"]),
 dict(slug="north-vancouver", name="North Vancouver", blurb="North Shore homes face hard winters and steep lots. We specialise in drainage, frozen-pipe repair and hot water for the North Van community.", nbhd=["Lonsdale","Lynn Valley","Deep Cove","Edgemont"]),
]

TESTIMONIALS = [
 ("Burst pipe at 11pm and a plumber was at our door in under an hour. Calm, tidy, and the price was exactly what they quoted on the phone.","Sarah M.","Kitsilano, Vancouver"),
 ("Booked online for a blocked drain, got same-day service and a camera video showing exactly what was wrong. No upsell, just honest work.","Daniel K.","Metrotown, Burnaby"),
 ("They replaced our ancient hot water tank with a tankless unit. Permitted, spotless, and they hauled the old one away. Couldn't be happier.","Priya R.","Steveston, Richmond"),
 ("Found a hidden slab leak that two other companies missed. Fixed it the same day with barely any mess. Genuinely impressed.","Marcus T.","Guildford, Surrey"),
 ("Our whole bathroom reno plumbing was handled start to finish. Clear pricing, on schedule, and the 25-year guarantee gives real peace of mind.","Emily and Sam","Burke Mountain, Coquitlam"),
 ("Smelled gas near our fireplace, called the emergency line and a licensed gas fitter sorted it safely that night. Cannot recommend enough.","Jordan W.","Lynn Valley, North Vancouver"),
]

BLOG = [
 dict(slug="how-to-unclog-a-drain", title="How to unclog a drain (and when to call a pro)",
      date="2026-05-12", tag="Guides", read="6 min",
      excerpt="A practical, safe, step-by-step guide to clearing a blocked drain at home — plus the warning signs that mean it's time to call a licensed plumber.",
      body=[("Start with the simplest fix","Before reaching for chemicals, try boiling water down the drain in two or three stages, letting it work for a few seconds between pours. For kitchen sinks, grease is the usual culprit and hot water alone often shifts a partial clog."),
            ("The baking soda and vinegar method","Pour half a cup of baking soda, then half a cup of white vinegar. Cover the drain for 10–15 minutes, then flush with boiling water. It's gentler on your pipes than caustic drain cleaners, which we don't recommend — they can damage older pipes and are dangerous if they back up."),
            ("Use a plunger correctly","Block the overflow opening with a damp cloth, ensure there's enough water to cover the plunger cup, and use firm, steady strokes. A flat-bottom sink plunger seals better than a toilet plunger for sinks."),
            ("Clean the P-trap","Place a bucket underneath, unscrew the curved trap below the sink, and clear any debris. This catches the majority of kitchen and bathroom sink clogs."),
            ("When to call a plumber","If multiple drains back up at once, you hear gurgling from other fixtures, water rises in the toilet when you run the sink, or the blockage keeps returning — stop. These point to a main-line or sewer issue that needs a camera inspection. Our 24/7 team can clear it the same day.")]),
 dict(slug="spring-plumbing-checklist", title="Your spring plumbing checklist for BC homes",
      date="2026-03-20", tag="Seasonal", read="5 min",
      excerpt="As the Lower Mainland thaws, a 20-minute spring check can prevent the most common — and expensive — plumbing failures of the year.",
      body=[("Check outdoor taps and hose bibs","Winter freeze-thaw is hard on outdoor taps. Turn each one on and place a thumb over the opening — if you can stop the flow, there may be an internal split. Check for drips at the wall."),
            ("Test your sump pump","Before the spring rains, pour a bucket of water into the sump pit and confirm the pump kicks in and drains. In low-lying areas like Richmond this is essential."),
            ("Inspect water heater","Look for rust, moisture, or pooling around the base. Flushing the tank once a year clears sediment and extends its life — we can do this during a maintenance visit."),
            ("Look for slow drains now","A drain that's sluggish in spring will be fully blocked by summer entertaining season. Clear it early."),
            ("Know your main shut-off","Every adult in the home should know where the main water valve is and that it turns freely. In an emergency, those seconds matter.")]),
]

# ----------------------------------------------------------------------------
# PARTIALS
# ----------------------------------------------------------------------------
NAV_SERVICES = "".join(f'<a href="service-{s["slug"]}.html">{s["name"]}</a>' for s in SERVICES)
NAV_CITIES   = "".join(f'<a href="area-{c["slug"]}.html">{c["name"]}</a>' for c in CITIES)

def header(active=""):
    def cur(p): return ' aria-current="page"' if p==active else ''
    return f'''
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap">
  <div class="tb-left">
    <span class="tb-badge">{svg("shield")} Licensed &amp; insured</span>
    <span class="tb-badge">{svg("clock")} {BIZ["hours"]}</span>
    <span class="tb-badge">{svg("pin")} Serving {BIZ["region"]}</span>
  </div>
  <a href="login.html">Staff login</a>
</div></div>
<header class="site-header"><div class="wrap">
  <a class="brand" href="index.html" aria-label="{BIZ["name"]} home">
    <span class="mark">{svg("logo")}</span>{BIZ["name"]}</a>
  <button class="nav-toggle" aria-label="Open menu" aria-expanded="false" aria-controls="nav">{svg("menu")}</button>
  <nav class="nav" id="nav" aria-label="Primary">
    <a href="index.html"{cur("home")}>Home</a>
    <span class="has-dd"><a href="services.html"{cur("services")}>Services</a>
      <span class="dd">{NAV_SERVICES}</span></span>
    <a href="pricing.html"{cur("pricing")}>Pricing</a>
    <span class="has-dd"><a href="service-areas.html"{cur("areas")}>Service areas</a>
      <span class="dd">{NAV_CITIES}</span></span>
    <a href="reviews.html"{cur("reviews")}>Reviews</a>
    <a href="blog.html"{cur("blog")}>Blog</a>
    <a href="about.html"{cur("about")}>About</a>
    <a href="contact.html"{cur("contact")}>Contact</a>
    <div class="header-cta" style="margin-top:8px">
      <a class="btn btn--primary" href="book.html">Book online</a></div>
  </nav>
  <div class="header-cta">
    <a class="phone" href="tel:{BIZ["phone_tel"]}">{svg("phone")} {BIZ["phone_display"]}</a>
    <a class="btn btn--primary" href="book.html">Book online</a>
  </div>
</div></header>'''

def trustbar():
    return f'''<div class="trustbar"><div class="wrap">
  <span class="ti">{svg("star")} {BIZ["rating"]}★ from {BIZ["reviews"]} reviews</span>
  <span class="ti">{svg("clock")} 60-minute emergency response</span>
  <span class="ti">{svg("shield")} 25-year workmanship guarantee</span>
  <span class="ti">{svg("dollar")} Upfront fixed pricing</span>
</div></div>'''

def footer():
    cols = "".join(f'<li><a href="service-{s["slug"]}.html">{s["name"]}</a></li>' for s in SERVICES)
    areas = "".join(f'<li><a href="area-{c["slug"]}.html">{c["name"]}</a></li>' for c in CITIES)
    return f'''
<footer class="site-footer"><div class="wrap">
  <div class="footer-grid">
    <div>
      <a class="brand" href="index.html" style="color:#fff">{svg("logo")} {BIZ["name"]}</a>
      <p style="color:#c7d6ee;margin-top:12px">Licensed, insured plumbers serving {BIZ["region"]} with genuine 24/7 emergency service and upfront fixed pricing.</p>
      <p style="color:#fff;font-weight:700"><a href="tel:{BIZ["phone_tel"]}">{BIZ["phone_display"]}</a><br>
      <a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a></p>
      <p style="color:#9fb6d8;font-size:.85rem">{BIZ["address"]}<br>{BIZ["licence"]}</p>
    </div>
    <div><h4>Services</h4><ul>{cols}</ul></div>
    <div><h4>Service areas</h4><ul>{areas}</ul></div>
    <div><h4>Company</h4><ul>
      <li><a href="about.html">About us</a></li>
      <li><a href="pricing.html">Pricing</a></li>
      <li><a href="reviews.html">Reviews</a></li>
      <li><a href="blog.html">Blog</a></li>
      <li><a href="book.html">Book online</a></li>
      <li><a href="pay.html">Pay my bill</a></li>
      <li><a href="portal.html">Warranty portal</a></li>
      <li><a href="refer.html">Refer a friend</a></li>
      <li><a href="contact.html">Contact</a></li>
      <li><a href="login.html">Staff login</a></li>
    </ul></div>
  </div>
  <div class="footer-bottom">
    <span>© {BIZ["year"]} {BIZ["name"]}. All rights reserved. {BIZ["licence"]}</span>
    <span>
      <a href="privacy.html">Privacy</a> ·
      <a href="terms.html">Terms</a> ·
      <a href="accessibility.html">Accessibility</a>
    </span>
  </div>
</div></footer>
<div class="toast" id="toast" role="status" aria-live="polite">{svg("check")}<span></span></div>
<div class="cookie" id="cookie" role="dialog" aria-label="Cookie consent" style="display:none">
  <p>We use only essential cookies to make this site work. With your consent we'd also use analytics to improve it. No non-essential cookies are set until you accept. See our <a href="privacy.html">Privacy Policy</a>.</p>
  <div class="row">
    <button class="btn btn--secondary" data-consent="essential">Essential only</button>
    <button class="btn btn--primary" data-consent="all">Accept all</button>
  </div>
</div>'''

# ----------------------------------------------------------------------------
def page(slug, title, desc, body, active="", jsonld="", og_img="city", admin=False):
    """Assemble a fully self-contained HTML file (inlined CSS + JS)."""
    canonical = f'{BIZ["domain"]}/{slug}'
    og = IMG.get(og_img, IMG["city"])[1]
    ld = f'<script type="application/ld+json">{jsonld}</script>' if jsonld else ""
    chrome = "" if admin else header(active) + (trustbar() if active=="home" else "")
    foot = "" if admin else footer()
    return f'''<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{og}">
<meta property="og:locale" content="en_CA">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0A2540">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="manifest" href="site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style>
{ld}
</head>
<body>
{chrome}
<main id="main"{' class="admin"' if admin else ''}>
{body}
</main>
{foot}
<script>{JS}</script>
</body>
</html>'''

# ---- reusable section builders ---------------------------------------------
def service_cards(exclude=None, limit=None):
    items = [s for s in SERVICES if s["slug"]!=exclude]
    if limit: items = items[:limit]
    out=[]
    for s in items:
        out.append(f'''<a class="card card--link" href="service-{s["slug"]}.html">
  <div class="ph">{img(s["photo"],w=600,h=375)}<span class="badge">{svg(s["icon"])}</span></div>
  <div class="body"><h3>{s["name"]}</h3><p>{s["tag"]}</p>
  <span class="more">{s["price"]} {svg("bolt")}</span></div></a>''')
    return f'<div class="grid grid-3">{"".join(out)}</div>'

def testimonial_grid(n=6):
    out=[]
    for q,who,where in TESTIMONIALS[:n]:
        out.append(f'''<figure class="tcard">
  <div class="stars" aria-label="5 out of 5 stars">★★★★★</div>
  <blockquote>“{q}”</blockquote>
  <figcaption><span class="who">{who}</span><br><span class="where">{where}</span></figcaption>
</figure>''')
    return f'<div class="grid grid-3">{"".join(out)}</div>'

def faq_block(faqs):
    items="".join(f'<details{" open" if i==0 else ""}><summary>{q}</summary><div class="a">{a}</div></details>'
                  for i,(q,a) in enumerate(faqs))
    return f'<div class="faq">{items}</div>'

def faq_jsonld(faqs):
    q=",".join('{"@type":"Question","name":%r,"acceptedAnswer":{"@type":"Answer","text":%r}}'%(html.unescape(a),html.unescape(b)) for a,b in faqs)
    return '{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[%s]}'%q

def cta_band(title="Need a plumber today?", text="Book online in 60 seconds or call our 24/7 line. Upfront fixed pricing, every time."):
    return f'''<section class="ctaband"><div class="wrap">
  <h2>{title}</h2><p class="lead">{text}</p>
  <div class="hero-cta">
    <a class="btn btn--lg btn--ghost" href="book.html">{svg("calendar")} Book a plumber</a>
    <a class="btn btn--lg btn--ghost" href="tel:{BIZ["phone_tel"]}">{svg("phone")} {BIZ["phone_display"]}</a>
  </div></div></section>'''

def area_chips():
    chips="".join(f'<a class="chip" href="area-{c["slug"]}.html">{svg("pin")}{c["name"]}</a>' for c in CITIES)
    return f'<div class="chips">{chips}</div>'

LOCALBUSINESS_LD = ('{"@context":"https://schema.org","@type":"Plumber","name":"%s",'
 '"image":"%s","telephone":"%s","email":"%s","url":"%s","priceRange":"$$",'
 '"address":{"@type":"PostalAddress","streetAddress":"1200 Trades Way","addressLocality":"Burnaby","addressRegion":"BC","postalCode":"V5C 0A1","addressCountry":"CA"},'
 '"areaServed":["Vancouver","Burnaby","Richmond","Surrey","Coquitlam","North Vancouver"],'
 '"openingHours":"Mo-Su 00:00-23:59",'
 '"aggregateRating":{"@type":"AggregateRating","ratingValue":"%s","reviewCount":"%s"}}'
 ) % (BIZ["name"], IMG["hero"][1], BIZ["phone_tel"], BIZ["email"], BIZ["domain"], BIZ["rating"], BIZ["reviews"])

# ============================================================================
# PAGE BODIES
# ============================================================================
def home_body():
    why=[("shield","Licensed &amp; insured","Every plumber is licensed, bonded and insured. Your home and your peace of mind are covered on every job."),
         ("clock","Genuine 24/7 service","A real plumber answers any hour — not an answering machine — with a 60-minute emergency response target."),
         ("dollar","Upfront fixed pricing","You approve the price before we start. No hourly surprises, no after-the-fact add-ons."),
         ("star","25-year guarantee","Our workmanship is backed for 25 years. If something we fixed fails, we make it right.")]
    whyhtml="".join(f'<div class="why"><div class="ic">{svg(i)}</div><div><h3>{t}</h3><p>{d}</p></div></div>' for i,t,d in why)
    steps=[("Book or call","Tell us what's wrong online or on the phone. We'll confirm a time that suits you, often same-day."),
           ("Upfront quote","Your plumber assesses the job and gives you a fixed price before any work begins."),
           ("We fix it right","Licensed, tidy, guaranteed work — done once, done properly, with respect for your home."),
           ("Guaranteed &amp; clean","We test everything, clean up, and back the workmanship for 25 years.")]
    stepshtml="".join(f'<div class="step"><h3>{t}</h3><p style="color:var(--muted)">{d}</p></div>' for t,d in steps)
    feat=SERVICE_BY["emergency"]
    return f'''
<section class="hero">
  {img("hero","hero-bg",lazy=False,w=1600,h=900)}
  <div class="wrap"><div class="hero-glass">
    <p class="eyebrow" style="color:#bcd2ff">{BIZ["region"]} · Licensed plumbers</p>
    <h1>Fixed fast. <span class="accent">Done right.</span></h1>
    <p>Burst pipe, blocked drain or no hot water — a licensed {BIZ["name"]} plumber is on the way, with upfront fixed pricing and a 25-year guarantee.</p>
    <div class="hero-cta">
      <a class="btn btn--lg btn--primary" href="book.html">{svg("calendar")} Book a plumber</a>
      <a class="btn btn--lg btn--ghost" href="tel:{BIZ["phone_tel"]}">{svg("phone")} {BIZ["phone_display"]}</a>
    </div>
    <p class="hero-trust"><span class="stars">★</span> {BIZ["rating"]} <span class="dot">·</span> {BIZ["reviews"]} reviews <span class="dot">·</span> Licensed &amp; insured <span class="dot">·</span> 24/7</p>
  </div></div>
</section>

<section class="section"><div class="wrap center">
  <p class="eyebrow">What we do</p>
  <h2>Plumbing services across {BIZ["region"]}</h2>
  <p class="lead">From a dripping tap to a full bathroom renovation — one licensed team, upfront pricing, every job guaranteed.</p>
  <div style="height:34px"></div>
  {service_cards()}
</div></section>

<section class="section" style="background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)">
  <div class="wrap"><div class="grid grid-2" style="align-items:center;gap:48px">
    <div>
      <p class="eyebrow">Why {BIZ["name"]}</p>
      <h2>The plumber your neighbours already trust</h2>
      <p class="lead">We built {BIZ["name"]} on the things homeowners actually want: someone who turns up, tells you the price first, does clean work, and stands behind it.</p>
      <div class="grid" style="gap:22px;margin-top:18px">{whyhtml}</div>
    </div>
    <div>{img("tech",w=600,h=700)}</div>
  </div></div>
</section>

<section class="section"><div class="wrap">
  <div class="center"><p class="eyebrow">How it works</p><h2>Four simple steps</h2></div>
  <div style="height:34px"></div>
  <div class="grid grid-4 steps">{stepshtml}</div>
</div></section>

<section class="section stats"><div class="wrap">
  <div class="grid grid-4">
    <div class="stat"><div class="n">{BIZ["rating"]}★</div><div class="l">{BIZ["reviews"]} verified reviews</div></div>
    <div class="stat"><div class="n">60<span style="font-size:1.4rem">min</span></div><div class="l">Emergency response target</div></div>
    <div class="stat"><div class="n">25<span style="font-size:1.4rem">yr</span></div><div class="l">Workmanship guarantee</div></div>
    <div class="stat"><div class="n">24/7</div><div class="l">Real plumbers on call</div></div>
  </div>
</div></section>

<section class="section" style="background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)">
  <div class="wrap"><div class="grid grid-2" style="align-items:center;gap:48px">
    <div>{img(feat["photo"],w=600,h=420)}</div>
    <div>
      <p class="eyebrow">Featured · {feat["name"]}</p>
      <h2>A burst pipe can't wait. Neither do we.</h2>
      <p class="lead">{feat["blurb"]}</p>
      <ul class="prose" style="margin:18px 0">{"".join(f"<li>{x}</li>" for x in feat["includes"][:4])}</ul>
      <a class="btn btn--primary" href="service-{feat["slug"]}.html">Explore emergency service {svg("bolt")}</a>
    </div>
  </div></div>
</section>

<section class="section"><div class="wrap">
  <div class="center"><p class="eyebrow">Reviews</p><h2>{BIZ["rating"]}★ from {BIZ["reviews"]} happy customers</h2></div>
  <div style="height:34px"></div>
  {testimonial_grid(3)}
  <div class="center" style="margin-top:28px"><a class="btn btn--secondary" href="reviews.html">Read all reviews {svg("star")}</a></div>
</div></section>

<section class="section" style="background:#fff;border-top:1px solid var(--line)"><div class="wrap center">
  <p class="eyebrow">Service areas</p><h2>Proudly serving the Lower Mainland</h2>
  <p class="lead">Local crews in every community we serve.</p>
  <div style="height:24px"></div>
  <div style="display:flex;justify-content:center">{area_chips()}</div>
</div></section>

<section class="section"><div class="wrap" style="max-width:820px">
  <div class="center"><p class="eyebrow">FAQ</p><h2>Questions, answered</h2></div>
  <div style="height:28px"></div>
  {faq_block([("Do you really answer 24/7?","Yes — a licensed plumber answers our emergency line at any hour, with a 60-minute response target across Greater Vancouver."),
              ("How does upfront fixed pricing work?","We assess the job and give you a fixed price before any work starts. You approve it first — no hourly surprises."),
              ("Are you licensed and insured?","Fully. Every plumber is licensed, bonded and insured, and all gas work is done by a certified gas fitter."),
              ("What area do you cover?","Vancouver, Burnaby, Richmond, Surrey, Coquitlam, North Vancouver and the surrounding Lower Mainland."),
              ("What's covered by the 25-year guarantee?","Our workmanship. If something we installed or repaired fails due to our work, we return and make it right.")])}
</div></section>

{cta_band()}'''

def service_detail_body(s):
    crumb=f'<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / <a href="services.html">Services</a> / {s["name"]}</div></div>'
    inc="".join(f"<li>{x}</li>" for x in s["includes"])
    return f'''{crumb}
<section class="hero" style="min-height:460px">
  {img(s["photo"],"hero-bg",lazy=False,w=1600,h=720)}
  <div class="wrap"><div class="hero-glass">
    <p class="eyebrow" style="color:#bcd2ff">{s["name"]} · {BIZ["region"]}</p>
    <h1>{s["name"]}</h1>
    <p>{s["tag"]}.</p>
    <div class="hero-cta">
      <a class="btn btn--lg btn--primary" href="book.html">{svg("calendar")} Book this service</a>
      <a class="btn btn--lg btn--ghost" href="tel:{BIZ["phone_tel"]}">{svg("phone")} {BIZ["phone_display"]}</a>
    </div>
    <p class="hero-trust"><span class="stars">★</span> {BIZ["rating"]} · {s["price"]} · Licensed · 24/7</p>
  </div></div>
</section>

<section class="section"><div class="wrap"><div class="grid grid-2" style="gap:48px;align-items:center">
  <div>
    <p class="eyebrow">What's included</p>
    <h2>{s["name"]}, done properly</h2>
    <p class="lead">{s["blurb"]}</p>
    <ul class="prose" style="margin-top:18px">{inc}</ul>
    <a class="btn btn--primary" style="margin-top:8px" href="book.html">Get a fixed quote {svg("dollar")}</a>
  </div>
  <div>{img(s["photo"],w=600,h=480)}</div>
</div></div></section>

<section class="section" style="background:#fff;border-top:1px solid var(--line)"><div class="wrap" style="max-width:820px">
  <div class="center"><p class="eyebrow">FAQ</p><h2>{s["name"]} — common questions</h2></div>
  <div style="height:28px"></div>{faq_block(s["faqs"])}
</div></section>

<section class="section"><div class="wrap">
  <div class="center"><p class="eyebrow">Other services</p><h2>We also handle</h2></div>
  <div style="height:30px"></div>{service_cards(exclude=s["slug"])}
</div></section>

{cta_band(title=f"Need {s['name'].lower()}?", text="Book online or call our 24/7 line for upfront fixed pricing.")}'''

def service_detail_ld(s):
    return ('{"@context":"https://schema.org","@type":"Service","serviceType":%r,'
            '"provider":{"@type":"Plumber","name":%r,"telephone":%r},'
            '"areaServed":"Greater Vancouver","description":%r}'
            ) % (s["name"], BIZ["name"], BIZ["phone_tel"], html.unescape(s["blurb"]))

def services_overview_body():
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / Services</div></div>
<section class="section--tight"><div class="wrap center">
  <p class="eyebrow">Our services</p>
  <h1>Plumbing services across {BIZ["region"]}</h1>
  <p class="lead">Licensed, insured, upfront-priced and guaranteed for 25 years. Choose a service to learn more.</p>
</div></section>
<section class="section--tight"><div class="wrap">{service_cards()}</div></section>
<section class="section"><div class="wrap center">
  <p class="eyebrow">Service areas</p><h2>Where we work</h2>
  <div style="height:18px"></div><div style="display:flex;justify-content:center">{area_chips()}</div>
</div></section>
{cta_band()}'''

def city_body(c):
    local_services="".join(
      f'<a class="card card--link" href="service-{s["slug"]}.html"><div class="ph">{img(s["photo"],w=600,h=375)}<span class="badge">{svg(s["icon"])}</span></div><div class="body"><h3>{s["name"]} in {c["name"]}</h3><p>{s["tag"]}</p><span class="more">{s["price"]} {svg("bolt")}</span></div></a>'
      for s in SERVICES)
    nbhd="".join(f'<span class="chip">{svg("pin")}{n}</span>' for n in c["nbhd"])
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / <a href="service-areas.html">Service areas</a> / {c["name"]}</div></div>
<section class="hero" style="min-height:440px">
  {img("city","hero-bg",lazy=False,w=1600,h=700)}
  <div class="wrap"><div class="hero-glass">
    <p class="eyebrow" style="color:#bcd2ff">Local plumbers · {c["name"]}, BC</p>
    <h1>Plumbers in {c["name"]}</h1>
    <p>{c["blurb"]}</p>
    <div class="hero-cta">
      <a class="btn btn--lg btn--primary" href="book.html">{svg("calendar")} Book a {c["name"]} plumber</a>
      <a class="btn btn--lg btn--ghost" href="tel:{BIZ["phone_tel"]}">{svg("phone")} {BIZ["phone_display"]}</a>
    </div>
    <p class="hero-trust"><span class="stars">★</span> {BIZ["rating"]} · {BIZ["reviews"]} reviews · 60-min response · 24/7</p>
  </div></div>
</section>
<section class="section"><div class="wrap">
  <div class="grid grid-2" style="gap:48px;align-items:center">
    <div><p class="eyebrow">Local &amp; licensed</p>
      <h2>Your {c["name"]} plumbing team</h2>
      <p class="lead">{c["blurb"]} Whatever the job, we bring upfront fixed pricing, tidy work and a 25-year workmanship guarantee.</p>
      <p style="margin-top:16px;font-weight:600;color:var(--navy)">Neighbourhoods we serve:</p>
      <div class="chips" style="margin-top:10px">{nbhd}</div>
    </div>
    <div>{img("handshake",w=600,h=460)}</div>
  </div>
</div></section>
<section class="section" style="background:#fff;border-top:1px solid var(--line)"><div class="wrap">
  <div class="center"><p class="eyebrow">Services in {c["name"]}</p><h2>What we fix locally</h2></div>
  <div style="height:30px"></div><div class="grid grid-3">{local_services}</div>
</div></section>
<section class="section"><div class="wrap">
  <div class="center"><p class="eyebrow">Reviews</p><h2>Trusted across {BIZ["region"]}</h2></div>
  <div style="height:30px"></div>{testimonial_grid(3)}
</div></section>
{cta_band(title=f"Need a plumber in {c['name']}?")}'''

def city_ld(c):
    return ('{"@context":"https://schema.org","@type":"Plumber","name":%r,'
            '"telephone":%r,"areaServed":{"@type":"City","name":%r},'
            '"aggregateRating":{"@type":"AggregateRating","ratingValue":%r,"reviewCount":%r}}'
            ) % (f'{BIZ["name"]} — {c["name"]}', BIZ["phone_tel"], c["name"], BIZ["rating"], BIZ["reviews"])

def areas_body():
    cards="".join(
      f'<a class="card card--link" href="area-{c["slug"]}.html"><div class="ph">{img("city",w=600,h=375)}<span class="badge">{svg("pin")}</span></div><div class="body"><h3>{c["name"]}</h3><p>{c["blurb"][:110]}…</p><span class="more">View {c["name"]} {svg("bolt")}</span></div></a>'
      for c in CITIES)
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / Service areas</div></div>
<section class="section--tight"><div class="wrap center">
  <p class="eyebrow">Service areas</p><h1>Plumbers across the Lower Mainland</h1>
  <p class="lead">Local crews, same-day service and 24/7 emergency cover in every community we serve.</p>
</div></section>
<section class="section--tight"><div class="wrap"><div class="grid grid-3">{cards}</div></div></section>
{cta_band()}'''

def about_body():
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / About</div></div>
<section class="section--tight"><div class="wrap" style="max-width:820px">
  <p class="eyebrow">About us</p><h1>Plumbing you can actually trust</h1>
  <p class="lead">{BIZ["name"]} is a licensed, insured plumbing company serving {BIZ["region"]}. We started with one belief: homeowners deserve a plumber who shows up on time, tells them the price first, and stands behind the work.</p>
</div></section>
<section class="section--tight"><div class="wrap">{img("tech",w=1200,h=520,lazy=False)}</div></section>
<section class="section"><div class="wrap prose" style="max-width:760px">
  <h2>Our story</h2>
  <p>What began as a single van is now a team of licensed plumbers and certified gas fitters covering Vancouver, Burnaby, Richmond, Surrey, Coquitlam and the North Shore. We've kept the same promise the whole way: do honest work, charge a fair fixed price, and treat every home like our own.</p>
  <h2>What we stand for</h2>
  <ul>
    <li><strong>Upfront fixed pricing.</strong> You approve the price before we start — no hourly meter running.</li>
    <li><strong>Genuine 24/7 service.</strong> A real plumber answers, any hour, with a 60-minute response target.</li>
    <li><strong>Licensed &amp; insured.</strong> Fully covered, with all gas work by certified gas fitters.</li>
    <li><strong>25-year guarantee.</strong> We back our workmanship for the long haul.</li>
  </ul>
  <h2>Licensed, insured &amp; local</h2>
  <p>We're a fully licensed BC plumbing contractor ({BIZ["licence"]}), insured for your protection, and proudly local. When you call, you reach a team that lives and works in the same communities we serve.</p>
</div></section>
<section class="section" style="background:#fff;border-top:1px solid var(--line)"><div class="wrap">
  <div class="center"><p class="eyebrow">The team</p><h2>People who care about your home</h2></div>
  <div style="height:30px"></div>{testimonial_grid(3)}
</div></section>
{cta_band()}'''

def contact_body():
    opts="".join(f'<option value="{s["slug"]}">{s["name"]}</option>' for s in SERVICES)
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / Contact</div></div>
<section class="section"><div class="wrap"><div class="grid grid-2" style="gap:48px;align-items:start">
  <div>
    <p class="eyebrow">Contact</p><h1>Get in touch</h1>
    <p class="lead">Call us 24/7 for emergencies, or send a message and we'll reply quickly during business hours.</p>
    <div class="grid" style="gap:18px;margin-top:24px">
      <div class="why"><div class="ic">{svg("phone")}</div><div><h3>Phone</h3><p><a href="tel:{BIZ["phone_tel"]}">{BIZ["phone_display"]}</a> · 24/7 emergency line</p></div></div>
      <div class="why"><div class="ic">{svg("mail")}</div><div><h3>Email</h3><p><a href="mailto:{BIZ["email"]}">{BIZ["email"]}</a></p></div></div>
      <div class="why"><div class="ic">{svg("pin")}</div><div><h3>Address</h3><p>{BIZ["address"]}</p></div></div>
      <div class="why"><div class="ic">{svg("clock")}</div><div><h3>Hours</h3><p>{BIZ["hours"]}</p></div></div>
    </div>
  </div>
  <div class="formcard">
    <h3>Send us a message</h3>
    <form data-validate data-success="Thanks — we'll be in touch shortly." name="contact" method="POST">
      <div class="hp" aria-hidden="true"><label>Leave this empty<input type="text" name="company" tabindex="-1" autocomplete="off"></label></div>
      <div class="field"><label for="c-name">Full name</label><input id="c-name" name="name" required><div class="err">Please enter your name.</div></div>
      <div class="grid grid-2" style="gap:14px">
        <div class="field"><label for="c-email">Email</label><input id="c-email" name="email" type="email" required><div class="err">Enter a valid email.</div></div>
        <div class="field"><label for="c-phone">Phone</label><input id="c-phone" name="phone" data-tel required><div class="err">Enter a valid phone number.</div></div>
      </div>
      <div class="field"><label for="c-svc">Service needed</label><select id="c-svc" name="service"><option value="">Choose…</option>{opts}<option value="other">Other</option></select></div>
      <div class="field"><label for="c-msg">How can we help?</label><textarea id="c-msg" name="message" required></textarea><div class="err">Please add a short message.</div></div>
      <label class="consent"><input type="checkbox" name="consent" required> I agree to be contacted about my enquiry and accept the <a href="privacy.html">Privacy Policy</a>. You can unsubscribe anytime (CASL).</label>
      <div style="height:14px"></div>
      <button class="btn btn--primary btn--block" type="submit">Send message {svg("mail")}</button>
    </form>
  </div>
</div></div></section>'''

def pricing_body():
    rows=[("Standard service call (first hour)","$149"),("Blocked drain clearing","from $189"),
          ("Tap / mixer replacement","from $165"),("Toilet repair","from $179"),
          ("Hot water tank replacement","from $1,650"),("Tankless hot water install","from $3,200"),
          ("Gas appliance connection","from $160"),("Leak detection survey","from $210"),
          ("After-hours emergency call-out","from $239")]
    rowhtml="".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a,b in rows)
    svc_opts="".join(f'<option value="{k}">{n}</option>' for k,n in
        [("drains","Blocked drains"),("hotwater","Hot water"),("emergency","Emergency call-out"),
         ("gas","Gas fitting"),("leak","Leak detection"),("reno","Bathroom renovation")])
    tiers=[("Call-out","$149","Standard hours diagnostic visit",["Licensed plumber to your door","Full diagnosis","Fixed quote for any work","Credited toward the repair"],False),
           ("Fixed repair","Quoted","Most common repairs",["Upfront fixed price","Parts &amp; labour included","Tidy, guaranteed work","25-year workmanship guarantee"],True),
           ("Care plan","$19/mo","Annual maintenance &amp; priority",["Yearly plumbing health check","Priority emergency booking","10% off all repairs","No after-hours surcharge"],False)]
    tierhtml="".join(
      f'<div class="tier{" feat" if f else ""}">{"<p class=eyebrow>Most popular</p>" if f else ""}<h3>{n}</h3><div class="price">{p}</div><p style="color:var(--muted)">{d}</p><ul>{"".join(f"<li>{x}</li>" for x in items)}</ul><a class="btn {"btn--primary" if f else "btn--secondary"} btn--block" href="book.html">Choose</a></div>'
      for n,p,d,items,f in tiers)
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / Pricing</div></div>
<section class="section--tight"><div class="wrap center">
  <p class="eyebrow">Pricing</p><h1>Upfront, fixed, honest pricing</h1>
  <p class="lead">No hourly surprises. You approve a fixed price before any work begins. Prices in CAD, taxes extra.</p>
</div></section>
<section class="section--tight"><div class="wrap"><div class="grid grid-3">{tierhtml}</div></div></section>
<section class="section" style="background:#fff;border-top:1px solid var(--line)"><div class="wrap"><div class="grid grid-2" style="gap:48px;align-items:start">
  <div>
    <p class="eyebrow">Instant estimate</p><h2>Quote estimator</h2>
    <p class="lead">A rough guide only — your fixed price is confirmed on site, free of charge.</p>
    <form id="estimator" class="formcard" style="margin-top:18px">
      <div class="field"><label for="e-svc">Service</label><select id="e-svc" name="svc">{svc_opts}</select></div>
      <div class="field"><label for="e-urg">When</label><select id="e-urg" name="urg">
        <option value="standard">Standard (business hours)</option>
        <option value="weekend">Weekend</option>
        <option value="emergency">Emergency / after-hours</option></select></div>
      <div id="est-out" style="background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:20px;text-align:center">
        <div style="color:var(--muted);font-size:.85rem;text-transform:uppercase;letter-spacing:.08em">Estimated range</div>
        <div style="font-family:'Instrument Serif',serif;font-size:2.4rem;color:var(--navy)"><span class="lo">$0</span> – <span class="hi">$0</span></div>
      </div>
      <div style="height:14px"></div>
      <a class="btn btn--primary btn--block" href="book.html">Book &amp; get exact price {svg("calendar")}</a>
    </form>
  </div>
  <div>
    <p class="eyebrow">Typical prices</p><h2>What jobs cost</h2>
    <p class="lead">A guide to common jobs. Every quote is fixed and confirmed before we start.</p>
    <div style="height:18px"></div>
    <table class="pricetable"><thead><tr><th>Job</th><th>Typical price (CAD)</th></tr></thead><tbody>{rowhtml}</tbody></table>
  </div>
</div></div></section>
{cta_band()}'''

def book_body():
    opts="".join(f'<option value="{s["slug"]}">{s["name"]}</option>' for s in SERVICES)
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / Book online</div></div>
<section class="section"><div class="wrap"><div class="grid grid-2" style="gap:48px;align-items:start">
  <div>
    <p class="eyebrow">Book online</p><h1>Book a plumber in 60 seconds</h1>
    <p class="lead">Tell us what you need and a preferred time. We'll confirm by phone or text, usually within the hour during business hours.</p>
    <div class="grid" style="gap:16px;margin-top:22px">
      <div class="why"><div class="ic">{svg("check")}</div><div><h3>Upfront fixed price</h3><p>Confirmed before any work starts.</p></div></div>
      <div class="why"><div class="ic">{svg("clock")}</div><div><h3>Fast scheduling</h3><p>Same-day slots for urgent jobs.</p></div></div>
      <div class="why"><div class="ic">{svg("shield")}</div><div><h3>Guaranteed work</h3><p>Backed for 25 years.</p></div></div>
    </div>
  </div>
  <div class="formcard">
    <h3>Request your booking</h3>
    <form data-validate data-success="Booking request received — we'll confirm shortly!" name="booking" method="POST">
      <div class="hp" aria-hidden="true"><label>Leave empty<input type="text" name="company" tabindex="-1" autocomplete="off"></label></div>
      <div class="field"><label for="b-name">Full name</label><input id="b-name" name="name" required><div class="err">Please enter your name.</div></div>
      <div class="grid grid-2" style="gap:14px">
        <div class="field"><label for="b-phone">Phone</label><input id="b-phone" name="phone" data-tel required><div class="err">Enter a valid phone.</div></div>
        <div class="field"><label for="b-email">Email</label><input id="b-email" name="email" type="email" required><div class="err">Enter a valid email.</div></div>
      </div>
      <div class="field"><label for="b-svc">Service</label><select id="b-svc" name="service" required><option value="">Choose…</option>{opts}</select><div class="err">Please choose a service.</div></div>
      <div class="grid grid-2" style="gap:14px">
        <div class="field"><label for="b-date">Preferred date</label><input id="b-date" name="date" type="date"></div>
        <div class="field"><label for="b-time">Preferred time</label><select id="b-time" name="time"><option>Morning</option><option>Afternoon</option><option>Evening</option><option>As soon as possible</option></select></div>
      </div>
      <div class="field"><label for="b-addr">Service address</label><input id="b-addr" name="address" required><div class="err">Please enter the address.</div></div>
      <div class="field"><label for="b-notes">Notes (optional)</label><textarea id="b-notes" name="notes"></textarea></div>
      <label class="consent"><input type="checkbox" name="consent" required> I agree to the <a href="privacy.html">Privacy Policy</a> and to be contacted about this booking (CASL).</label>
      <div style="height:14px"></div>
      <button class="btn btn--primary btn--block" type="submit">Request booking {svg("calendar")}</button>
    </form>
  </div>
</div></div></section>'''

def pay_body():
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / Pay my bill</div></div>
<section class="section"><div class="wrap" style="max-width:560px">
  <div class="formcard">
    <p class="eyebrow">Secure payment</p><h1>Pay my bill</h1>
    <p class="lead">Enter your invoice number to pay securely. Payments are processed by our PCI-compliant provider — no card details are ever stored on this site.</p>
    <form data-validate data-success="Redirecting to secure checkout…" name="pay">
      <div class="field"><label for="p-inv">Invoice number</label><input id="p-inv" name="invoice" required placeholder="INV-00000"><div class="err">Enter your invoice number.</div></div>
      <div class="field"><label for="p-email">Email on invoice</label><input id="p-email" name="email" type="email" required><div class="err">Enter a valid email.</div></div>
      <button class="btn btn--primary btn--block" type="submit">{svg("lock")} Continue to secure checkout</button>
    </form>
    <p style="font-size:.85rem;color:var(--muted);margin-top:16px">{svg("lock","")} You'll be redirected to our hosted payment provider (Stripe/Square). {BIZ["name"]} never sees or stores your full card number.</p>
  </div>
</div></section>'''

def portal_body():
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / Warranty portal</div></div>
<section class="section"><div class="wrap"><div class="grid grid-2" style="gap:48px;align-items:start">
  <div>
    <p class="eyebrow">Customer portal</p><h1>Warranty &amp; maintenance records</h1>
    <p class="lead">Sign in to view your service history, download invoices, and check what's covered under your 25-year workmanship guarantee.</p>
    <ul class="prose" style="margin-top:16px">
      <li>Full service &amp; maintenance history</li>
      <li>Warranty certificates and coverage dates</li>
      <li>Downloadable invoices and receipts</li>
      <li>Book a covered repair in one click</li>
    </ul>
  </div>
  <div class="formcard">
    <h3>Sign in</h3>
    <form id="loginForm" data-next="portal-records.html" data-validate>
      <div class="hp" aria-hidden="true"><label>Leave empty<input type="text" name="company" tabindex="-1"></label></div>
      <div class="field"><label for="po-email">Email</label><input id="po-email" name="email" type="email" required><div class="err">Enter your email.</div></div>
      <div class="field"><label for="po-pass">Password</label><input id="po-pass" name="password" type="password" required><div class="err">Enter your password.</div></div>
      <label class="consent"><input type="checkbox" name="remember"> Remember me</label>
      <div style="height:14px"></div>
      <button class="btn btn--primary btn--block" type="submit">Sign in</button>
      <p style="text-align:center;margin-top:12px"><a href="#">Forgot password?</a></p>
    </form>
    <p style="font-size:.82rem;color:var(--muted);margin-top:8px">Demo only — no real account is required. See SECURITY.md for the production auth plan.</p>
  </div>
</div></div></section>'''

def portal_records_body():
    rows=[("2026-05-02","Blocked drain — kitchen","Covered","INV-04821"),
          ("2025-11-18","Hot water tank replacement","Covered (25yr)","INV-04122"),
          ("2025-06-30","Tap replacement — ensuite","Covered","INV-03788")]
    rh="".join(f'<tr><td>{d}</td><td>{j}</td><td><span class="pill green">{c}</span></td><td><a href="pay.html">{i}</a></td></tr>' for d,j,c,i in rows)
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / <a href="portal.html">Portal</a> / Records</div></div>
<section class="section"><div class="wrap">
  <p class="eyebrow">Your records</p><h1>Service &amp; warranty history</h1>
  <p class="lead">Demo data shown. In production this is loaded securely for the signed-in customer only.</p>
  <div style="height:24px"></div>
  <div class="panel"><h3>Maintenance records</h3>
    <table class="dtable"><thead><tr><th>Date</th><th>Job</th><th>Warranty</th><th>Invoice</th></tr></thead><tbody>{rh}</tbody></table>
  </div>
</div></section>'''

def reviews_body():
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / Reviews</div></div>
<section class="section--tight"><div class="wrap center">
  <p class="eyebrow">Reviews</p><h1>{BIZ["rating"]}★ from {BIZ["reviews"]} reviews</h1>
  <p class="lead">Real feedback from homeowners across {BIZ["region"]}. Verified across Google and our own follow-ups.</p>
</div></section>
<section class="section--tight"><div class="wrap">{testimonial_grid(6)}</div></section>
{cta_band(title="Join 600+ happy customers")}'''

def refer_body():
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / Refer a friend</div></div>
<section class="section"><div class="wrap"><div class="grid grid-2" style="gap:48px;align-items:center">
  <div>
    <p class="eyebrow">Refer &amp; earn</p><h1>Give $50, get $50</h1>
    <p class="lead">Love our work? Refer a friend or neighbour. When they book their first job, you both get a $50 credit toward your next service. Loyalty members earn double.</p>
    <div class="grid grid-3" style="margin:22px 0">
      <div class="kpi"><div class="n">$50</div><div class="l">You earn</div></div>
      <div class="kpi"><div class="n">$50</div><div class="l">They save</div></div>
      <div class="kpi"><div class="n">2×</div><div class="l">Loyalty bonus</div></div>
    </div>
  </div>
  <div class="formcard">
    <h3>Send a referral</h3>
    <form data-validate data-success="Referral sent — thank you!" name="referral">
      <div class="hp" aria-hidden="true"><label>Leave empty<input type="text" name="company" tabindex="-1"></label></div>
      <div class="field"><label for="r-name">Your name</label><input id="r-name" name="name" required><div class="err">Enter your name.</div></div>
      <div class="field"><label for="r-email">Your email</label><input id="r-email" name="email" type="email" required><div class="err">Enter a valid email.</div></div>
      <div class="field"><label for="r-fname">Friend's name</label><input id="r-fname" name="friend" required><div class="err">Enter their name.</div></div>
      <div class="field"><label for="r-femail">Friend's email</label><input id="r-femail" name="friend_email" type="email" required><div class="err">Enter a valid email.</div></div>
      <label class="consent"><input type="checkbox" name="consent" required> My friend is happy to be contacted, and I accept the <a href="privacy.html">Privacy Policy</a> (CASL).</label>
      <div style="height:14px"></div>
      <button class="btn btn--primary btn--block" type="submit">Send referral {svg("gift")}</button>
    </form>
  </div>
</div></div></section>'''

def blog_index_body():
    cards="".join(
      f'<a class="card card--link" href="post-{p["slug"]}.html"><div class="ph">{img("sink" if "drain" in p["slug"] else "tap",w=600,h=375)}<span class="badge">{svg("doc")}</span></div><div class="body"><p class="eyebrow">{p["tag"]} · {p["read"]}</p><h3>{p["title"]}</h3><p>{p["excerpt"]}</p><span class="more">Read article {svg("bolt")}</span></div></a>'
      for p in BLOG)
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / Blog</div></div>
<section class="section--tight"><div class="wrap center">
  <p class="eyebrow">Blog</p><h1>Plumbing tips &amp; guides</h1>
  <p class="lead">Practical advice from our licensed plumbers — how-tos, seasonal checklists, and when to call a pro.</p>
</div></section>
<section class="section--tight"><div class="wrap"><div class="grid grid-3">{cards}</div></div></section>
{cta_band()}'''

def blog_post_body(p):
    secs="".join(f"<h2>{t}</h2><p>{b}</p>" for t,b in p["body"])
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / <a href="blog.html">Blog</a> / {p["tag"]}</div></div>
<section class="section--tight"><div class="wrap" style="max-width:760px">
  <p class="eyebrow">{p["tag"]} · {p["read"]} read · {p["date"]}</p>
  <h1>{p["title"]}</h1>
  <p class="lead">{p["excerpt"]}</p>
</div></section>
<section class="section--tight"><div class="wrap" style="max-width:1000px">{img("sink" if "drain" in p["slug"] else "tap",w=1000,h=480,lazy=False)}</div></section>
<section class="section"><div class="wrap prose" style="max-width:760px">{secs}
  <div style="height:20px"></div>
  <div class="formcard" style="background:var(--surface)"><h3>Need a hand from a pro?</h3>
  <p>Our licensed plumbers are available 24/7 across {BIZ["region"]} with upfront fixed pricing.</p>
  <a class="btn btn--primary" href="book.html">Book a plumber {svg("calendar")}</a></div>
</div></section>'''

def blog_post_ld(p):
    return ('{"@context":"https://schema.org","@type":"Article","headline":%r,'
            '"datePublished":%r,"author":{"@type":"Organization","name":%r},'
            '"publisher":{"@type":"Organization","name":%r}}'
            ) % (html.unescape(p["title"]), p["date"], BIZ["name"], BIZ["name"])

def legal_body(title, intro, sections):
    secs="".join(f"<h2>{t}</h2>{b}" for t,b in sections)
    return f'''<div class="wrap"><div class="crumb"><a href="index.html">Home</a> / {title}</div></div>
<section class="section"><div class="wrap prose" style="max-width:760px">
  <p class="eyebrow">Legal</p><h1>{title}</h1>
  <p class="lead">{intro}</p><div style="height:10px"></div>{secs}
  <p style="color:var(--muted);font-size:.88rem;margin-top:24px">Last updated {datetime.date.today():%B %Y}. This is placeholder content — have it reviewed by legal counsel before publishing.</p>
</div></section>'''

def notfound_body():
    return f'''<section class="section center" style="padding:110px 0"><div class="wrap" style="max-width:560px">
  <p class="eyebrow">404</p><h1>This page sprung a leak</h1>
  <p class="lead">We couldn't find that page. Let's get you back to dry land.</p>
  <div style="height:20px"></div>
  <div class="hero-cta" style="justify-content:center">
    <a class="btn btn--primary" href="index.html">{svg("home")} Back home</a>
    <a class="btn btn--secondary" href="contact.html">Contact us</a>
  </div>
</div></section>'''

# ============================================================================
# ADMIN
# ============================================================================
ADMIN_NAV=[("dashboard","Dashboard","chart"),("bookings","Bookings","calendar"),
           ("customers","Customers","users"),("schedule","Schedule","truck"),
           ("team","Team","users"),("invoices","Invoices","doc"),("settings","Settings","gear")]
def admin_shell(active, title, body):
    def navlink(s,n,i):
        cur=' aria-current="page"' if s==active else ''
        return f'<a href="{s}.html"{cur}>{svg(i)}{n}</a>'
    nav="".join(navlink(s,n,i) for s,n,i in ADMIN_NAV)
    return f'''
<aside class="admin-side">
  <a class="brand" href="index.html">{svg("logo")} {BIZ["name"]}</a>
  <nav aria-label="Admin">{nav}</nav>
  <div style="margin-top:18px;border-top:1px solid rgba(255,255,255,.12);padding-top:12px">
    <a href="index.html">{svg("home")} View website</a>
    <a href="login.html">{svg("lock")} Sign out</a>
  </div>
</aside>
<div class="admin-main">
  <div class="demo-banner">Demo environment — sample data only. Production requires authentication &amp; a live backend (see SECURITY.md).</div>
  <div class="admin-top"><h1 style="font-size:1.8rem;margin:0">{title}</h1>
    <div class="header-cta"><span class="chip">{svg("users")} Demo Admin</span><a class="btn btn--secondary" href="login.html">Sign out</a></div></div>
  <div class="admin-body">{body}</div>
</div>'''

def admin_dashboard():
    leads=[("Sarah M.","Blocked drain","Kitsilano","New","amber"),("Daniel K.","Hot water","Metrotown","Quoted","blue"),
           ("Priya R.","Emergency","Steveston","Booked","green"),("Marcus T.","Leak detection","Guildford","New","amber")]
    lh="".join(f'<tr><td>{n}</td><td>{j}</td><td>{a}</td><td><span class="pill {c}">{s}</span></td></tr>' for n,j,a,s,c in leads)
    sched=[("08:00","Mike R.","Hot water install","Burnaby"),("10:30","Aisha P.","Drain camera","Vancouver"),
           ("13:00","Tom L.","Gas inspection","Richmond"),("15:30","Mike R.","Emergency leak","Surrey")]
    sh="".join(f'<tr><td>{t}</td><td>{tech}</td><td>{j}</td><td>{a}</td></tr>' for t,tech,j,a in sched)
    bars=[("Mon",60),("Tue",78),("Wed",55),("Thu",90),("Fri",100),("Sat",72),("Sun",40)]
    bh="".join(f'<div class="bar" style="height:{v}%"><span>{d}</span></div>' for d,v in bars)
    return admin_shell("dashboard","Dashboard",f'''
<div class="grid grid-4">
  <div class="kpi"><div class="l">Revenue (mo.)</div><div class="n">$84.2k</div><div class="d up">▲ 12.4%</div></div>
  <div class="kpi"><div class="l">Jobs completed</div><div class="n">218</div><div class="d up">▲ 6.1%</div></div>
  <div class="kpi"><div class="l">New leads</div><div class="n">47</div><div class="d up">▲ 9.0%</div></div>
  <div class="kpi"><div class="l">Avg. rating</div><div class="n">4.9★</div><div class="d up">▲ 0.1</div></div>
</div>
<div style="height:22px"></div>
<div class="grid grid-2" style="gap:22px;align-items:start">
  <div class="panel"><h3>Revenue — last 7 days</h3><div class="pad"><div class="bars">{bh}</div></div></div>
  <div class="panel"><h3>Today's schedule</h3><table class="dtable"><thead><tr><th>Time</th><th>Tech</th><th>Job</th><th>Area</th></tr></thead><tbody>{sh}</tbody></table></div>
</div>
<div style="height:22px"></div>
<div class="panel"><h3>Recent leads</h3><table class="dtable"><thead><tr><th>Customer</th><th>Service</th><th>Area</th><th>Status</th></tr></thead><tbody>{lh}</tbody></table></div>''')

def admin_table_page(active,title,head,rows,intro,extra=""):
    th="".join(f"<th>{h}</th>" for h in head)
    tr="".join("<tr>"+"".join(f"<td>{c}</td>" for c in r)+"</tr>" for r in rows)
    return admin_shell(active,title,f'''<p class="lead">{intro}</p><div style="height:18px"></div>
{extra}<div class="panel"><table class="dtable"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>''')

def admin_bookings():
    rows=[["#B-1042","Sarah M.","Blocked drain","Today 14:00","Kitsilano",'<span class="pill amber">Pending</span>'],
          ["#B-1041","Daniel K.","Hot water","Tomorrow 09:00","Metrotown",'<span class="pill green">Confirmed</span>'],
          ["#B-1040","Priya R.","Emergency","Today 16:30","Steveston",'<span class="pill blue">Dispatched</span>'],
          ["#B-1039","Marcus T.","Leak detection","Fri 11:00","Guildford",'<span class="pill gray">Quote sent</span>']]
    return admin_table_page("bookings","Bookings",["Ref","Customer","Service","When","Area","Status"],rows,"Incoming and scheduled bookings. Lists are pagination-ready in production.")

def admin_customers():
    rows=[["Sarah M.","sarah@example.com","Kitsilano","7","$3,210"],["Daniel K.","daniel@example.com","Metrotown","3","$1,480"],
          ["Priya R.","priya@example.com","Steveston","5","$4,920"],["Marcus T.","marcus@example.com","Guildford","2","$640"]]
    return admin_table_page("customers","Customers (CRM)",["Name","Email","Area","Jobs","Lifetime value"],rows,"Customer relationship records. Production enforces row-level access — staff see only permitted records (no IDOR).")

def admin_schedule():
    rows=[["08:00","Mike R.","Hot water install","Burnaby",'<span class="pill green">On site</span>'],
          ["10:30","Aisha P.","Drain camera","Vancouver",'<span class="pill blue">En route</span>'],
          ["13:00","Tom L.","Gas inspection","Richmond",'<span class="pill gray">Scheduled</span>'],
          ["15:30","Mike R.","Emergency leak","Surrey",'<span class="pill amber">Unassigned</span>']]
    return admin_table_page("schedule","Schedule &amp; dispatch",["Time","Technician","Job","Area","Status"],rows,"Technician dispatch board for today. Drag-and-drop assignment is a backend feature.")

def admin_team():
    rows=[["Mike Reyes","mike@bluelineplumbing.ca","Technician",'<span class="pill green">Active</span>'],
          ["Aisha Patel","aisha@bluelineplumbing.ca","Technician",'<span class="pill green">Active</span>'],
          ["Tom Lee","tom@bluelineplumbing.ca","Office",'<span class="pill green">Active</span>'],
          ["Dana Cole","dana@bluelineplumbing.ca","Admin",'<span class="pill green">Active</span>']]
    form='''<div class="panel" style="margin-bottom:22px"><h3>Add employee</h3><div class="pad">
<form data-validate data-success="Employee invited (demo).">
  <div class="grid grid-2" style="gap:14px">
    <div class="field"><label for="t-name">Full name</label><input id="t-name" name="name" required><div class="err">Required.</div></div>
    <div class="field"><label for="t-email">Work email</label><input id="t-email" name="email" type="email" required><div class="err">Valid email required.</div></div>
  </div>
  <div class="field"><label for="t-role">Access level</label><select id="t-role" name="role">
    <option value="technician">Technician — sees own jobs &amp; schedule</option>
    <option value="office">Office — bookings, customers, invoices</option>
    <option value="admin">Admin — full access incl. team &amp; settings</option></select></div>
  <button class="btn btn--primary" type="submit">Send invite</button>
  <p style="font-size:.82rem;color:var(--muted);margin-top:8px">Access levels map to what each person sees after login. Enforced server-side in production (RBAC).</p>
</form></div></div>'''
    return admin_table_page("team","Team",["Name","Email","Access level","Status"],rows,"Employee roster and access levels.",extra=form)

def admin_invoices():
    rows=[["INV-04821","Sarah M.","$289","2026-05-02",'<span class="pill green">Paid</span>'],
          ["INV-04820","Daniel K.","$1,650","2026-05-01",'<span class="pill amber">Sent</span>'],
          ["INV-04819","Priya R.","$3,200","2026-04-28",'<span class="pill green">Paid</span>'],
          ["INV-04818","Marcus T.","$210","2026-04-27",'<span class="pill gray">Draft</span>']]
    note='<div class="panel" style="margin-bottom:22px"><div class="pad"><strong>QuickBooks sync:</strong> connected (demo). Paid invoices push to QuickBooks Online nightly via OAuth. <a href="settings.html">Manage integration →</a></div></div>'
    return admin_table_page("invoices","Invoices",["Invoice","Customer","Amount","Date","Status"],rows,"Invoice register with QuickBooks sync.",extra=note)

def admin_settings():
    def tog(on): return f'<button class="toggle" role="switch" aria-checked="{str(on).lower()}" aria-label="toggle"></button>'
    return admin_shell("settings","Settings",f'''
<div class="grid grid-2" style="gap:22px;align-items:start">
  <div class="panel"><h3>Business details</h3><div class="pad">
    <div class="field"><label>Business name</label><input value="{BIZ['name']}"></div>
    <div class="field"><label>Phone</label><input value="{BIZ['phone_display']}"></div>
    <div class="field"><label>Email</label><input value="{BIZ['email']}"></div>
    <div class="field"><label>Address</label><input value="{BIZ['address']}"></div>
    <button class="btn btn--primary">Save changes</button>
  </div></div>
  <div>
    <div class="panel" style="margin-bottom:22px"><h3>Notifications</h3><div class="pad">
      <div class="setrow"><span>New booking email</span>{tog(True)}</div>
      <div class="setrow"><span>SMS on emergency lead</span>{tog(True)}</div>
      <div class="setrow"><span>Daily summary digest</span>{tog(False)}</div>
      <div class="setrow" style="border-bottom:0"><span>Review request after job</span>{tog(True)}</div>
    </div></div>
    <div class="panel"><h3>Integrations</h3><div class="pad">
      <div class="setrow"><span>QuickBooks Online</span><span class="pill green">Connected</span></div>
      <div class="setrow"><span>Stripe payments</span><span class="pill green">Connected</span></div>
      <div class="setrow"><span>Google Business Profile</span><span class="pill gray">Not set up</span></div>
      <div class="setrow" style="border-bottom:0"><span>hCaptcha / Turnstile</span><span class="pill amber">Needs key</span></div>
    </div></div>
  </div>
</div>''')

def login_body():
    return f'''<div class="auth-wrap"><div class="auth-card">
  <a class="brand" href="index.html" style="margin-bottom:18px">{svg("logo")} {BIZ["name"]}</a>
  <h1 style="font-size:2rem">Staff sign in</h1>
  <p style="color:var(--muted)">Sign in with your work email to access the admin dashboard.</p>
  <form id="loginForm" data-next="dashboard.html" data-validate style="margin-top:18px">
    <div class="hp" aria-hidden="true"><label>Leave empty<input type="text" name="company" tabindex="-1"></label></div>
    <div class="field"><label for="l-email">Work email</label><input id="l-email" name="email" type="email" required autocomplete="username"><div class="err">Enter your work email.</div></div>
    <div class="field"><label for="l-pass">Password</label><input id="l-pass" name="password" type="password" required autocomplete="current-password"><div class="err">Enter your password.</div></div>
    <label class="consent"><input type="checkbox" name="remember"> Remember me on this device</label>
    <div style="height:14px"></div>
    <button class="btn btn--primary btn--block" type="submit">Sign in {svg("lock")}</button>
    <p style="text-align:center;margin-top:12px"><a href="#">Forgot password?</a></p>
  </form>
  <p style="font-size:.8rem;color:var(--muted);margin-top:14px">Demo only — any credentials open the dashboard. Production uses hashed passwords, sessions &amp; rate-limiting (SECURITY.md).</p>
</div></div>'''

# ============================================================================
# STATIC FILES
# ============================================================================
def favicon_svg():
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">'
            '<rect width="24" height="24" rx="5" fill="#1E5BD6"/>'
            '<path fill="#fff" d="M12 4s5 5.4 5 9a5 5 0 0 1-10 0c0-1.4.7-3 1.6-4.5C9.7 9.7 11 10.4 11 12a1.5 1.5 0 0 0 1.5-1.5c0-2-2.3-3.2-.5-6.5Z"/></svg>')

def manifest():
    return ('{"name":"%s","short_name":"BlueLine","start_url":"./index.html",'
            '"display":"standalone","background_color":"#F7F9FC","theme_color":"#0A2540",'
            '"icons":[{"src":"favicon.svg","sizes":"any","type":"image/svg+xml"}]}') % BIZ["name"]

def sitemap(pages):
    today=datetime.date.today().isoformat()
    admin_prefixes=("dashboard","bookings","customers","schedule","team","invoices","settings","login","portal-records")
    urls="".join(f'<url><loc>{BIZ["domain"]}/{p}</loc><lastmod>{today}</lastmod></url>'
                 for p in pages if not p.startswith(admin_prefixes))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+urls+'</urlset>')

def robots():
    return ("User-agent: *\nAllow: /\n"
            "Disallow: /dashboard.html\nDisallow: /bookings.html\nDisallow: /customers.html\n"
            "Disallow: /schedule.html\nDisallow: /team.html\nDisallow: /invoices.html\n"
            "Disallow: /settings.html\nDisallow: /login.html\nDisallow: /portal-records.html\n"
            "Disallow: /admin/\n\n"
            f"Sitemap: {BIZ['domain']}/sitemap.xml\n")

# ============================================================================
# BUILD
# ============================================================================
def main():
    if DIST.exists(): shutil.rmtree(DIST)
    DIST.mkdir()
    (DIST/"images").mkdir()
    pages={}  # filename -> (title,desc,bodyfn,active,jsonld,og)

    def add(fn,title,desc,body,active="",jsonld="",og="city"):
        pages[fn]=page(fn,title,desc,body,active,jsonld,og)

    N=BIZ["name"]
    add("index.html", f"{N} — Licensed Plumbers in {BIZ['region']} | 24/7 Emergency",
        f"Licensed, insured plumbers serving {BIZ['region']}. 24/7 emergency service, upfront fixed pricing, 25-year guarantee. {BIZ['rating']}★ from {BIZ['reviews']} reviews. Book online or call {BIZ['phone_display']}.",
        home_body(),"home",LOCALBUSINESS_LD,"hero")
    add("services.html", f"Plumbing Services in {BIZ['region']} | {N}",
        f"Blocked drains, hot water, 24/7 emergency, gas fitting, leak detection and bathroom renovations across {BIZ['region']}.",
        services_overview_body(),"services")
    for s in SERVICES:
        add(f"service-{s['slug']}.html", f"{s['name']} in {BIZ['region']} | {N}",
            f"{s['tag']}. {html.unescape(s['blurb'])} Upfront fixed pricing, licensed plumbers, {s['price']}.",
            service_detail_body(s),"services",
            f'[{service_detail_ld(s)},{faq_jsonld(s["faqs"])}]', s["photo"])
    add("service-areas.html", f"Service Areas | Plumbers across the Lower Mainland | {N}",
        f"{N} serves Vancouver, Burnaby, Richmond, Surrey, Coquitlam and North Vancouver with 24/7 plumbing.",
        areas_body(),"areas")
    for c in CITIES:
        add(f"area-{c['slug']}.html", f"Plumbers in {c['name']}, BC | {N}",
            f"Licensed plumbers in {c['name']}. 24/7 emergency service, upfront fixed pricing, 60-minute response. {html.unescape(c['blurb'])[:90]}",
            city_body(c),"areas",city_ld(c),"city")
    add("about.html", f"About {N} | Licensed &amp; Insured Plumbers",
        f"{N} is a licensed, insured plumbing company serving {BIZ['region']} with honest, guaranteed work.",
        about_body(),"about","",  "tech")
    add("contact.html", f"Contact {N} | 24/7 Plumbing",
        f"Call {BIZ['phone_display']} for 24/7 emergencies or send a message. {N} serves {BIZ['region']}.",
        contact_body(),"contact")
    add("pricing.html", f"Pricing &amp; Quote Estimator | {N}",
        "Upfront fixed plumbing prices in CAD, a quote estimator and a typical-price table. No hourly surprises.",
        pricing_body(),"pricing")
    add("book.html", f"Book a Plumber Online | {N}",
        "Book a licensed plumber online in 60 seconds. Same-day slots, upfront fixed pricing, 25-year guarantee.",
        book_body(),"book")
    add("pay.html", f"Pay My Bill | {N}",
        "Pay your plumbing invoice securely. PCI-compliant hosted checkout — no card details stored on site.",
        pay_body())
    add("portal.html", f"Warranty &amp; Maintenance Portal | {N}",
        "Sign in to view your plumbing service history, warranty coverage and invoices.",
        portal_body())
    add("portal-records.html", f"Your Records | {N}", "Customer service and warranty records.",
        portal_records_body())
    add("reviews.html", f"Reviews — {BIZ['rating']}★ from {BIZ['reviews']} | {N}",
        f"Read {BIZ['reviews']} verified reviews for {N}. Rated {BIZ['rating']}★ across {BIZ['region']}.",
        reviews_body(),"reviews")
    add("refer.html", f"Refer a Friend &amp; Loyalty Program | {N}",
        "Give $50, get $50. Refer a friend to BlueLine Plumbing and earn credit toward your next service.",
        refer_body())
    add("blog.html", f"Plumbing Tips &amp; Guides | {N} Blog",
        "Practical plumbing advice from licensed plumbers — how-tos, seasonal checklists and more.",
        blog_index_body(),"blog")
    for p in BLOG:
        add(f"post-{p['slug']}.html", f"{p['title']} | {N}", p["excerpt"],
            blog_post_body(p),"blog",blog_post_ld(p))
    # legal
    add("privacy.html","Privacy Policy | "+N,"How "+N+" collects, uses and protects your personal information under PIPEDA and CASL.",
        legal_body("Privacy Policy",
          f"{N} respects your privacy. This policy explains how we handle personal information in accordance with Canada's PIPEDA and CASL.",
          [("Information we collect","<p>We collect the information you give us — name, contact details, service address and job details — to provide plumbing services and respond to enquiries.</p>"),
           ("How we use it","<p>To schedule and deliver services, send invoices, and (with your consent) send service reminders and offers. Under CASL we only send commercial electronic messages with your consent, and every message includes an unsubscribe link.</p>"),
           ("Cookies","<p>We use only essential cookies by default. Non-essential analytics cookies are set only after you accept via our cookie banner.</p>"),
           ("Your rights (PIPEDA)","<p>You may request access to, correction of, or deletion of your personal information at any time by emailing "+BIZ['email']+". We retain records only as long as needed for service and legal obligations.</p>"),
           ("Contact","<p>Privacy questions? Email "+BIZ['email']+" or call "+BIZ['phone_display']+".</p>")]))
    add("terms.html","Terms of Service | "+N,"The terms governing use of "+N+" services and website.",
        legal_body("Terms of Service","These terms govern your use of our website and services.",
          [("Services","<p>We provide licensed plumbing services across "+BIZ['region']+". Quotes are fixed once confirmed in writing.</p>"),
           ("Workmanship guarantee","<p>Our 25-year workmanship guarantee covers defects in our installation or repair work. It does not cover pre-existing conditions, misuse, or third-party work.</p>"),
           ("Payment","<p>Payment is due on completion unless otherwise agreed. Payments are processed by a PCI-compliant provider.</p>"),
           ("Liability","<p>Nothing in these terms limits liability that cannot be limited by law.</p>")]))
    add("accessibility.html","Accessibility Statement | "+N,N+" is committed to WCAG 2.1 AA accessibility.",
        legal_body("Accessibility Statement","We are committed to making this website accessible to everyone, targeting WCAG 2.1 AA.",
          [("Our commitment","<p>This site is built with semantic HTML, keyboard navigation, visible focus states, sufficient colour contrast, descriptive alt text and labelled forms.</p>"),
           ("Feedback","<p>If you encounter any barrier, please call "+BIZ['phone_display']+" or email "+BIZ['email']+" and we'll help and put it right.</p>")]))
    add("404.html","Page not found | "+N,"The page you were looking for could not be found.",notfound_body())
    # admin (auth-gated in production; excluded from sitemap/robots)
    pages["login.html"]=page("login.html","Staff Login | "+N,"Sign in to the "+N+" admin dashboard.",login_body(),admin=False)
    for fn,b in [("dashboard.html",admin_dashboard()),("bookings.html",admin_bookings()),
                 ("customers.html",admin_customers()),("schedule.html",admin_schedule()),
                 ("team.html",admin_team()),("invoices.html",admin_invoices()),("settings.html",admin_settings())]:
        title=fn.replace(".html","").title()
        pages[fn]=page(fn,f"{title} | {N} Admin","Admin — demo.",b,admin=True)

    # write pages
    for fn,htmlstr in pages.items():
        (DIST/fn).write_text(htmlstr)
    # static
    (DIST/"favicon.svg").write_text(favicon_svg())
    (DIST/"site.webmanifest").write_text(manifest())
    (DIST/"sitemap.xml").write_text(sitemap(list(pages)))
    (DIST/"robots.txt").write_text(robots())
    # copy hosting/security config + image placeholders note
    for f in ["_headers","netlify.toml",".htaccess","IMAGE_CREDITS.md"]:
        src=ROOT/f
        if src.exists(): shutil.copy(src,DIST/f)
    (DIST/"images/README.txt").write_text("Run scripts/fetch_images.py to self-host photos here.\nUntil then, pages fall back to the Pexels CDN automatically (see data-cdn).\n")
    print(f"Built {len(pages)} pages + sitemap/robots/manifest/favicon -> {DIST}")

if __name__=="__main__":
    main()
