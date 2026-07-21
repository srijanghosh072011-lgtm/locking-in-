# Photo & Imagery Guide

The template ships with **self-contained SVG placeholder art** (gold-on-black
duotone) so it renders perfectly with zero external dependencies and no
licensing strings. Every image slot is designed to be swapped for a real photo
in one line. This guide covers **what to use, where to get it, how to generate
it, and the exact specs.**

---

## 1. Image slots & exact specs

| Slot | File to replace | Size (px) | Ratio | Notes |
|------|-----------------|-----------|-------|-------|
| Hero portrait | `assets/img/portrait.svg` | 800 × 1000 | 4:5 | The face of the site. Suit, confident, dark/neutral background. |
| About portrait | *(reuses `portrait.svg`)* | 800 × 1000 | 4:5 | Same person, different crop — see "two-portrait" note below. |
| Insight 1 | `assets/img/insight-1.svg` | 640 × 400 | 16:10 | Blog thumbnail — formation / office. |
| Insight 2 | `assets/img/insight-2.svg` | 640 × 400 | 16:10 | Blog thumbnail — contracts / signing. |
| Insight 3 | `assets/img/insight-3.svg` | 640 × 400 | 16:10 | Blog thumbnail — M&A / handshake. |
| Social preview | `assets/img/og.png` | 1200 × 630 | 1.91:1 | Regenerate after you change the name/brand. |
| Favicon | `assets/img/favicon.svg` | any | 1:1 | Monogram — change the letter in the SVG. |

**How to swap:** either (a) drop your file in `assets/img/` with the **same
name** (e.g. save your photo as `portrait.svg`… or name it `portrait.jpg` and
update the `<img src>` in `index.html`), or (b) just edit the two `src`
attributes. Keep `width`/`height` matching your file's ratio to avoid layout
shift.

> **Two different portraits (recommended):** the hero and About sections both
> point at `portrait.svg` today. For a richer site, use two photos — a clean
> studio cut-out for the hero and a wider "in the office" shot for About. Save
> them as `portrait-hero.jpg` and `portrait-about.jpg` and update the two
> `<img src>` lines.

---

## 2. Art direction — what a good "lawyer" photo looks like

You want the photo to match the template's mood (dark, warm, premium). Aim for:

- **Wardrobe:** dark suit, white/light shirt. Tie optional. No busy patterns.
- **Background:** dark, neutral, or softly blurred office. Avoid bright white
  studio backgrounds — they fight the black theme. A dark or charcoal backdrop
  drops straight in.
- **Lighting:** warm, directional, a little dramatic (a subtle rim light on one
  side echoes the placeholder art). Avoid flat, cold, overexposed lighting.
- **Expression:** calm, confident, approachable — not stiff corporate stock.
- **Crop:** head-and-shoulders or 3/4 body, subject slightly off-center so text
  can breathe beside it.

If the photo has a bright background and you want it to melt into the black
theme, cut it out (remove.bg / Photoshop) and place on transparent → it sits on
the dark frame beautifully.

---

## 3. Real (royalty-free) photo sources — with search terms

All of these are free for commercial use (check each license; Unsplash/Pexels/
Pixabay are generally free, **no attribution required** but appreciated):

**Unsplash** — https://unsplash.com — best quality. Search:
- `businessman portrait dark background`
- `lawyer office`
- `professional man suit studio`
- `confident businesswoman suit` *(if you want a female attorney)*
- `attorney handshake`

**Pexels** — https://pexels.com — big selection, easy download. Search:
- `business portrait dark`
- `lawyer` / `attorney` / `legal`
- `person in suit`

**Pixabay** — https://pixabay.com — search `lawyer`, `businessman`, `office`.

> ⚠️ **Model release matters.** For a real client site, a stranger's stock face
> implying they're *your* attorney is misleading and can breach a stock
> license's "no false endorsement / sensitive use" clause. For a **demo /
> template** it's fine. For a **live lawyer's site, use the real lawyer's
> photo** (a proper headshot session is worth it). This mirrors the
> "replace all placeholder images with real client photos" item in your
> pre-launch playbook.

**Paid, if you want premium + safer licensing:** Adobe Stock, Getty/iStock,
Stocksy (more editorial/authentic looking).

---

## 4. Generate the hero with AI (the hero image *does* look AI-generated)

Your instinct was right — hero images like the reference are very often AI
stock. You can make your own. Paste these into the tool of your choice.

**Midjourney / general (v6+):**
```
editorial portrait of a confident corporate lawyer, mid-40s, tailored dark
charcoal suit, white shirt, standing arms crossed, warm rim lighting on a near-
black background, cinematic, shallow depth of field, shot on 85mm, subtle film
grain, luxury law-firm branding aesthetic, gold-and-black color grade
--ar 4:5 --style raw --v 6
```

**ChatGPT (GPT-image) / DALL·E — prompt:**
```
A premium, photorealistic head-and-shoulders portrait of a professional
attorney in a dark tailored suit against a warm dark (near-black) background,
dramatic side/rim lighting, calm confident expression, editorial magazine
quality, 4:5 vertical. Leave the left side slightly darker for text overlay.
```

**Adobe Firefly** (commercially safe — trained on licensed data, includes
content credentials): use the same wording; set aspect ratio **Portrait (4:5)**,
content type **Photo**, add "warm cinematic lighting, dark background."

**Ideogram / Leonardo:** same prompt, great for realistic faces.

**Tips**
- Generate 4:5 (portrait) and 16:10 (the blog thumbs) to match the slots.
- Ask for a **dark background** so it drops into the theme with no editing.
- Vary "arms crossed" / "seated at a desk" / "walking in a lobby" for the
  About + insight images so they're not all the same pose.
- **Disclose AI imagery** where appropriate and never imply a fake person is a
  real, licensed lawyer on a live site.

---

## 5. Optimize before you ship (from your pre-launch checklist)

- Export **WebP or AVIF**, not giant JPEGs. Target < 200 KB for the portrait.
- Keep `width`/`height` on the `<img>` (already set) to prevent layout shift.
- The hero image already has `fetchpriority="high"` + preload; below-the-fold
  images have `loading="lazy"`.
- Re-generate `og.png` (1200×630) after rebranding — most social platforms do
  **not** render SVG OG images, so a PNG/JPG is required for link previews.
- Write **descriptive alt text** for meaningful images; the decorative blog
  thumbnails intentionally use `alt=""`.
