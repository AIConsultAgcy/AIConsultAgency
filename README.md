# Fands — website

Static site for Fands, an AI implementation agency for small and mid-size US businesses, live at https://fands.io and hosted on Vercel.

## Build

Pages are written in `src/` and built into plain HTML at the repo root:

```bash
python build.py
```

Each `src/*.html` starts with a one-line JSON header, for example:

```json
{"out": "services.html", "path": "/services", "title": "AI Services for Small Businesses | Fands", "description": "...", "crumbs": [["Services", "/services"]], "priority": 0.9, "type": "CollectionPage"}
```

Optional keys: `hero` (home page sculpture and intro), `schema`, `noindex`, `og_type`, `type` (schema.org page type).

`build.py` wraps every page with the shared head, header, footer, cookie banner and booking button, expands tokens and writes:

- every page's HTML, with title, description, canonical, Open Graph, Twitter and JSON-LD (Organization, WebPage, breadcrumbs);
- `sitemap.xml` (indexable pages only, `lastmod` from each source file), `robots.txt` and `llms.txt` for AI assistants.

Tokens: `{{i:name:size}}` icons, `{{cal}}` Cal.com popup attributes, `{{closing}}` final call to action, `{{crumbs}}` breadcrumbs, `{{legal-nav}}` legal document switcher.

Edit `src/`, `assets/` or `build.py`, then rebuild. Never edit the generated HTML at the root.

## Pieces

- `assets/site.css`, `assets/site.js`: shared styles and behaviour (menu, demo, forms, consent, analytics events). Asset URLs carry a content hash, so they are cached for a year.
- `assets/sculpture.js`: the Three.js hero ring on the home page.
- `api/lead.js`: Vercel function for the inquiry, Field Notes and privacy-request forms. It filters spam (honeypot, fill time, link spam) and forwards to Google Apps Script via `GOOGLE_APPS_SCRIPT_URL`.
- Analytics: Google Tag Manager `GTM-N3C2TK2J` with Google Consent Mode, plus Vercel Web Analytics. Events pushed to the data layer: `cta_click`, `cal_open`, `outbound_click`, `email_click`, `form_start`, `generate_lead`, `form_error`, `demo_run`, `consent_choice`.
- Booking: Cal.com `fands/intro-call` popup, loaded after the page is idle.

## Before launch

- Have the legal pages (`/privacy`, `/terms`, `/cookies`, `/ai-data-policy`, `/accessibility`, `/privacy-choices`) reviewed by a lawyer.
- Case studies are example engagements; replace them with real, approved client results as projects complete.
