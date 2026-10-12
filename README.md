# Fands — website

Static site for Fands, the West Hollywood AI agency, live at https://fands.io. One page, no build dependencies.

> We build and deploy AI systems that create measurable outcomes for your business.

## Files
- `index.html` — the site. Open it directly or host it on any static host (Vercel, Netlify, GitHub Pages).
- `page.html` — the page body without the html/head/body wrapper; this is what the Claude artifact publishes. Edit this file, then run `./build.sh` to regenerate `index.html`.
- `img/` — photography (Unsplash, free licence), resized to 1600px.
- `build.sh` — wraps `page.html` into `index.html`.

## How it works
- The hero and the pinned "What we measure" section run on Three.js (loaded from cdnjs, pinned to 0.160.0). 32,000 particles morph from noise into a bar chart, a bookings grid and a rising line as you scroll.
- Fonts: Instrument Sans and IBM Plex Mono from Google Fonts.
- The contact form is handled on the page only; wire it to a form service or email before launch.
- Respects `prefers-reduced-motion`; works at phone width.

## Before launch, replace
- Street address, phone, social links (all marked "placeholder" on the page). The hello@fands.io mailbox still needs to be created.
- The pilot numbers (71%, 38/wk, 9 hrs) are labelled targets. Swap in real case studies as pilots complete.
