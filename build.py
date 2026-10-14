#!/usr/bin/env python3
"""Builds the static site. Each src/*.html is a page body whose first line is a JSON header:
   {"out": "contact.html", "title": "...", "description": "...", "path": "/contact", "hero": false}
The build wraps it with the shared head, header and footer and expands {{i:name:size}} icon tokens."""
import json, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent
SITE = 'https://fands.io'

ICONS = {
    'up-right': '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
    'right': '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    'down': '<path d="M12 5v14"/><path d="m19 12-7 7-7-7"/>',
    'plus': '<path d="M5 12h14"/><path d="M12 5v14"/>',
    'x': '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    'chevron': '<path d="m6 9 6 6 6-6"/>',
    'pause': '<rect x="14" y="4" width="4" height="16" rx="1"/><rect x="6" y="4" width="4" height="16" rx="1"/>',
    'play': '<polygon points="6 3 20 12 6 21 6 3"/>',
    'file': '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
}

def icon(m):
    name, size = m.group(1), m.group(2) or '20'
    cls = f' class="{m.group(3)}"' if m.group(3) else ''
    return (f'<svg{cls} width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')

MARK = ('<svg viewBox="0 0 100 100" aria-hidden="true"><rect class="s" y="38" width="62" height="62"/>'
        '<rect class="s" x="38" width="62" height="62"/><rect class="o" x="38" y="38" width="24" height="24"/></svg>')

HEADER = '''<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <a href="/" aria-label="Fands, home" class="brand-logo"><span class="wm">{mark}Fands</span></a>
  <nav class="desktop-nav" aria-label="Main navigation"><a href="/#workflows">Systems</a><a href="/#approach">Approach</a><a href="/#services">Engagements</a><a href="/insights">Field notes</a></nav>
  <div class="header-actions"><a class="header-contact" href="/contact">Let’s talk {{{{i:up-right:16}}}}</a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-menu" aria-label="Open navigation"><span class="ico-plus">{{{{i:plus:19}}}}</span><span class="ico-x" hidden>{{{{i:x:19}}}}</span></button></div>
</header>
<nav id="site-menu" class="menu-panel" aria-label="Expanded navigation" hidden>
  <a href="/#workflows">Systems {{{{i:up-right:28}}}}</a><a href="/#approach">Approach {{{{i:up-right:28}}}}</a><a href="/#services">Engagements {{{{i:up-right:28}}}}</a><a href="/insights">Field notes {{{{i:up-right:28}}}}</a><a href="/contact">Start a conversation {{{{i:up-right:28}}}}</a>
  <p>Useful intelligence.<br>Built into the way you work.</p>
</nav>'''.format(mark=MARK)

FOOTER = '''<footer class="site-footer">
  <div class="footer-top"><p>Useful intelligence.<br>Built into the way you work.</p><div><a href="/insights">Field notes {{{{i:up-right:16}}}}</a><a href="/contact">Start a conversation {{{{i:up-right:16}}}}</a><a href="mailto:hello@fands.io">hello@fands.io {{{{i:up-right:16}}}}</a><a href="/privacy">Privacy {{{{i:up-right:16}}}}</a></div></div>
  <div class="footer-word" aria-hidden="true">Fands<span>{mark}</span></div>
  <div class="footer-bottom"><span>© 2026 Fands</span><span>Built to work. Measured to matter.</span><a href="#main">Back to top ↑</a></div>
</footer>'''.format(mark=MARK)

SCHEMA = {
    "@context": "https://schema.org", "@type": "ProfessionalService", "@id": SITE + "/#org", "name": "Fands",
    "url": SITE + "/", "logo": SITE + "/brand/icon-512.png", "image": SITE + "/brand/og.png", "email": "hello@fands.io",
    "slogan": "From friction to flow.",
    "description": "Fands designs, builds and runs AI workflows for consulting and specialist service firms, starting with one handoff, a measured baseline and a named owner.",
    "knowsAbout": ["AI workflow automation", "client intake automation", "project kickoff automation", "process mapping", "AI governance and human review"],
    "makesOffer": [
        {"@type": "Offer", "name": "Workflow Diagnostic", "price": "2500", "priceCurrency": "USD", "description": "Process map, baseline plan, feasibility review and pilot scope in five business days."},
        {"@type": "Offer", "name": "Workflow Pilot", "priceSpecification": {"@type": "PriceSpecification", "minPrice": "12000", "priceCurrency": "USD"}, "description": "One workflow, up to three integrations, testing, training and an outcome review in four to six weeks."},
        {"@type": "Offer", "name": "System Care", "priceSpecification": {"@type": "UnitPriceSpecification", "minPrice": "1500", "priceCurrency": "USD", "unitText": "MONTH"}, "description": "Up to three supported workflows, six service hours and a monthly review."}]}

HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#080b10">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Instrument+Sans:wght@600&display=swap">
<link rel="stylesheet" href="/assets/site.css?v={v}">
<link rel="icon" href="/brand/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/brand/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" href="/brand/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Fands">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://fands.io/brand/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="https://fands.io/brand/og.png">
{extra}</head>
<body>
'''

SCULPTURE = '''<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.186.1/examples/jsm/"}}</script>
<script type="module" src="/assets/sculpture.js?v={v}"></script>
'''

TAIL = '''<script src="/assets/site.js?v={v}"></script>
{sculpture}<script>window.va=window.va||function(){{(window.vaq=window.vaq||[]).push(arguments)}};</script>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
'''

def main():
    import hashlib
    v = hashlib.sha1(b''.join((ROOT / 'assets' / f).read_bytes() for f in ('site.css', 'site.js', 'sculpture.js'))).hexdigest()[:8]
    for src in sorted((ROOT / 'src').glob('*.html')):
        first, body = src.read_text().split('\n', 1)
        meta = json.loads(first)
        extra = ''
        if meta.get('schema'):
            extra = '<script type="application/ld+json">' + json.dumps(SCHEMA, separators=(',', ':')) + '</script>\n'
        html = (HEAD.format(title=meta['title'], description=meta['description'], url=SITE + meta['path'], v=v, extra=extra)
                + HEADER + '\n' + body.strip() + '\n' + FOOTER + '\n'
                + TAIL.format(v=v, sculpture=SCULPTURE.replace('{v}', v) if meta.get('hero') else ''))
        html = re.sub(r'\{\{i:([a-z-]+)(?::(\d+))?(?::([a-z-]+))?\}\}', icon, html)
        out = ROOT / meta['out']
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html)
        print(f'built {meta["out"]} ({len(html):,} bytes)')

if __name__ == '__main__':
    main()
