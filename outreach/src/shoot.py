"""Screenshot a site into email-ready images.

Used two ways:
  1. Shoot the Ghosh Designs demo template -> the "This could be yours" image.
  2. Shoot a prospect's existing site -> the "here's what you have now" image,
     which is what makes the before/after comparison land.

Requires playwright (`pip install playwright`). Chromium is already on the box
at /opt/pw-browsers, so do NOT run `playwright install`.
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys

# The pre-installed Chromium may not match the revision this playwright build
# wants, so point at the binary directly instead of letting it resolve.
CHROMIUM = os.environ.get("CHROMIUM_PATH", "/opt/pw-browsers/chromium")

# Reveal-on-scroll animations leave content invisible in a naive screenshot.
# Forcing the end state is more reliable than trying to wait them out.
KILL_ANIMATIONS = """
* , *::before, *::after {
  animation-duration: 0s !important;
  animation-delay: 0s !important;
  transition-duration: 0s !important;
  transition-delay: 0s !important;
}
[class*="reveal"], [data-reveal], .fade-in, .animate-in {
  opacity: 1 !important;
  transform: none !important;
  visibility: visible !important;
  clip-path: none !important;
}
html { scroll-behavior: auto !important; }
"""

PRESETS = {
    "desktop": {"width": 1280, "height": 800, "scale": 2, "mobile": False},
    "mobile": {"width": 390, "height": 844, "scale": 3, "mobile": True},
}


def _host_of(u: str) -> str:
    from urllib.parse import urlparse

    return (urlparse(u).hostname or "").lower()


def _settle(page, full_page: bool) -> None:
    """Trigger lazy-loaded images and scroll-reveal animations, then reset."""
    page.evaluate(
        """async () => {
            const step = Math.floor(window.innerHeight * 0.8);
            // Reveal-on-scroll sections grow the document as they unhide, so
            // re-reading scrollHeight as the loop bound never terminates.
            // Snapshot it, and cap the passes regardless.
            const target = document.body.scrollHeight;
            const maxSteps = 40;
            let y = 0;
            for (let i = 0; i < maxSteps && y < target; i++, y += step) {
                window.scrollTo(0, y);
                await new Promise(r => setTimeout(r, 60));
            }
            window.scrollTo(0, 0);
            await new Promise(r => setTimeout(r, 150));
        }"""
    )
    # Wait for pixels to actually be there, otherwise images render blank.
    # Deliberately NOT img.decode(): on a `loading="lazy"` image that is still
    # off-screen, decode() never settles, which hangs the whole capture.
    page.evaluate(
        """async () => {
            const imgs = Array.from(document.images);
            imgs.forEach(i => { if (i.loading === 'lazy') i.loading = 'eager'; });
            const settled = Promise.all(imgs.filter(i => !i.complete).map(i =>
                new Promise(r => {
                    i.addEventListener('load', r, { once: true });
                    i.addEventListener('error', r, { once: true });
                })
            ));
            // Never let one dead asset stall the shot.
            await Promise.race([settled, new Promise(r => setTimeout(r, 5000))]);
        }"""
    )
    if not full_page:
        page.evaluate("window.scrollTo(0, 0)")


def shoot(
    url: str,
    out: pathlib.Path,
    preset: str = "desktop",
    full_page: bool = False,
    timeout_ms: int = 45000,
    personalize_cfg: dict | None = None,
) -> pathlib.Path:
    from playwright.sync_api import sync_playwright

    cfg = PRESETS[preset]
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        launch = {"args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if pathlib.Path(CHROMIUM).exists():
            launch["executable_path"] = CHROMIUM
        browser = p.chromium.launch(**launch)
        ctx = browser.new_context(
            viewport={"width": cfg["width"], "height": cfg["height"]},
            device_scale_factor=cfg["scale"],
            is_mobile=cfg["mobile"],
            has_touch=cfg["mobile"],
            # A real UA string — some sites serve a broken page to headless.
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
        )
        # Analytics/tag-manager scripts stall behind an egress proxy and the
        # `load` event never fires. They contribute nothing to a screenshot, and
        # prospect sites are full of them, so drop every third-party request.
        allow_host = _host_of(url)

        def _gate(route):
            if _host_of(route.request.url) == allow_host:
                route.continue_()
            else:
                route.abort()

        ctx.route("**/*", _gate)

        page = ctx.new_page()
        try:
            page.goto(url, wait_until="load", timeout=timeout_ms)
        except Exception as e:
            # A prospect's dead/slow site is a data point, not a crash — we still
            # want whatever rendered, because "their site times out" is the pitch.
            print(f"  ! load issue for {url}: {type(e).__name__}", file=sys.stderr)
        page.add_style_tag(content=KILL_ANIMATIONS)
        try:
            page.wait_for_load_state("networkidle", timeout=8000)
        except Exception:
            pass
        _settle(page, full_page)

        if personalize_cfg:
            from personalize import PERSONALIZE_JS

            # After hydration, so React cannot overwrite the substitutions.
            page.evaluate(PERSONALIZE_JS, personalize_cfg)
            page.wait_for_timeout(250)
            if not full_page:
                page.evaluate("window.scrollTo(0, 0)")

        page.screenshot(path=str(out), full_page=full_page)
        browser.close()

    return out


def optimize_for_email(
    src: pathlib.Path, max_kb: int = 250, max_width: int = 1200
) -> pathlib.Path:
    """Downscale + re-encode to JPEG until it fits under max_kb.

    A retina PNG is ~3 MB. Gmail clips messages over 102 KB of *markup*, and a
    multi-megabyte inline image is both a spam signal and a slow render on the
    phone where these get opened. JPEG because this is a photograph.
    """
    from PIL import Image

    out = src.with_suffix(".jpg")
    im = Image.open(src).convert("RGB")
    if im.width > max_width:
        im = im.resize(
            (max_width, round(im.height * max_width / im.width)), Image.LANCZOS
        )

    for quality in (85, 78, 70, 62, 55):
        im.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
        if out.stat().st_size <= max_kb * 1024:
            break

    src.unlink(missing_ok=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Screenshot a site for outreach emails.")
    ap.add_argument("url")
    ap.add_argument("-o", "--out", required=True, type=pathlib.Path)
    ap.add_argument("-p", "--preset", default="desktop", choices=sorted(PRESETS))
    ap.add_argument("--full-page", action="store_true")
    args = ap.parse_args()

    path = shoot(args.url, args.out, args.preset, args.full_page)
    kb = path.stat().st_size / 1024
    print(f"{path}  ({kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
