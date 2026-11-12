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
    'linkedin': '<path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect width="4" height="12" x="2" y="9"/><circle cx="4" cy="4" r="2"/>',
    'instagram': '<rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>',
    'youtube': '<path d="M2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.56 49.56 0 0 1 16.2 0A2 2 0 0 1 21.5 7a24.12 24.12 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.55 49.55 0 0 1-16.2 0A2 2 0 0 1 2.5 17"/><path d="m10 15 5-3-5-3z"/>',
    'calendar': '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
    'globe': '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
    'mail': '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
    'share': '<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><path d="m16 6-4-4-4 4"/><path d="M12 2v13"/>',
    'phone': '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    'whatsapp': '<path d="M3 21l1.65-4.8A8.5 8.5 0 1 1 7.8 19.35z"/><path d="M9 9.5c0 3 2.5 5.5 5.5 5.5l1-1.5-2-1-1 .8a4 4 0 0 1-2.3-2.3l.8-1-1-2z"/>',
    'telegram': '<path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/>',
    'user-plus': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M19 8v6"/><path d="M22 11h-6"/>',
    'menu':'<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
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
  <nav class="desktop-nav" aria-label="Main navigation"><a href="/services">Services</a><a href="/how-we-work">How we work</a><a href="/case-studies">Case studies</a><a href="/about">About</a><a href="/insights">Field notes</a><a href="/contact">Contact</a></nav>
  <div class="header-actions"><a class="header-contact" href="/contact">Let’s talk {{{{i:up-right:16}}}}</a><button class="menu-toggle" type="button" aria-expanded="false" aria-controls="site-menu" aria-label="Open navigation"><span class="ico-plus">{{{{i:menu:19}}}}</span><span class="ico-x" hidden>{{{{i:x:19}}}}</span></button></div>
</header>
<nav id="site-menu" class="menu-panel" aria-label="Expanded navigation" hidden>
  <a href="/services">Services {{{{i:up-right:28}}}}</a><a href="/how-we-work">How we work {{{{i:up-right:28}}}}</a><a href="/case-studies">Case studies {{{{i:up-right:28}}}}</a><a href="/about">About {{{{i:up-right:28}}}}</a><a href="/insights">Field notes {{{{i:up-right:28}}}}</a><a href="/contact">Contact {{{{i:up-right:28}}}}</a>
  <p>Useful intelligence.<br>Built into the way you work.</p>
</nav>'''.format(mark=MARK)

FOOTER = '''<footer class="site-footer">
  <div class="footer-top"><p>Useful intelligence.<br>Built into the way you work.</p>
    <nav class="footer-nav" aria-label="Footer">
      <div><p class="fh">Explore</p><a href="/services">Services</a><a href="/how-we-work">How we work</a><a href="/case-studies">Case studies</a><a href="/insights">Field notes</a></div>
      <div><p class="fh">Company</p><a href="/about">About</a><a href="/contact">Contact</a><a href="/privacy">Privacy &amp; legal</a></div>
      <div><p class="fh">Get in touch</p><a href="mailto:hello@fands.io">hello@fands.io</a><a href="https://cal.com/fands/intro-call" {{{{cal}}}}>Book a free call {{{{i:up-right:14}}}}</a>
        <div class="socials"><a href="https://www.linkedin.com/company/fands-ai/" target="_blank" rel="noopener noreferrer" aria-label="Fands on LinkedIn">{{{{i:linkedin:18}}}}</a><a href="https://www.instagram.com/fands.ai" target="_blank" rel="noopener noreferrer" aria-label="Fands on Instagram">{{{{i:instagram:18}}}}</a><a href="https://www.youtube.com/@fands-ai" target="_blank" rel="noopener noreferrer" aria-label="Fands on YouTube">{{{{i:youtube:18}}}}</a></div></div>
    </nav></div>
  <div class="footer-word" aria-hidden="true">Fands<span>{mark}</span></div>
  <div class="footer-bottom"><span>© 2026 Fands · <em class="footer-slogan">From friction to flow.</em></span><nav class="footer-legal" aria-label="Legal"><a href="/privacy">Privacy Policy</a><a href="/terms">Terms</a><a href="/cookies">Cookies</a><a href="/privacy-choices">Your Privacy Choices</a></nav><a href="#main">Back to top ↑</a></div>
</footer>'''.format(mark=MARK)

SCHEMA = {
    "@context": "https://schema.org", "@type": "ProfessionalService", "@id": SITE + "/#org", "name": "Fands",
    "url": SITE + "/", "logo": SITE + "/brand/icon-512.png", "image": SITE + "/brand/og-v2.png", "email": "hello@fands.io",
    "slogan": "From friction to flow.",
    "description": "Fands is an AI implementation agency for small and mid-size businesses in the United States. It automates workflows, builds AI into the tools a business already uses, and produces content that keeps the brand in front of customers.",
    "areaServed": {"@type": "Country", "name": "United States"},    "knowsAbout": ["workflow automation", "business process automation", "AI integrations", "AI content generation", "lead follow-up automation", "AI search visibility", "AI readiness audits", "AI assistants", "web development"],
    "makesOffer": [{"@type": "Offer", "name": "AI Readiness Audit & Roadmap"}, {"@type": "Offer", "name": "Managed AI Retainer"}, {"@type": "Offer", "name": "Business Process Automation"}, {"@type": "Offer", "name": "Lead-to-Revenue Automation"}, {"@type": "Offer", "name": "Knowledge Assistant & Analytics"}, {"@type": "Offer", "name": "AI Training & Enablement"}, {"@type": "Offer", "name": "AI Receptionist"}, {"@type": "Offer", "name": "Custom AI Agents & Apps"}, {"@type": "Offer", "name": "AI Content Engine"}, {"@type": "Offer", "name": "AI Search Visibility & Local SEO"}, {"@type": "Offer", "name": "Paid Media Management"}, {"@type": "Offer", "name": "Branding & Design"}, {"@type": "Offer", "name": "Web & App Development"}, {"@type": "Offer", "name": "Website & E-commerce Automation"}]}


# First-visit intro: two silver squares travel in from opposite corners and lock together, the overlap lights orange,
# the name rises, the cover lifts. Repeat visits in the same session get a short version; reduced motion gets a fade.
INTRO = '''<div id="intro" aria-hidden="true">
  <div class="intro-lock"><span class="intro-mark"><i class="sq a"></i><i class="sq b"></i><i class="ov"></i></span><span class="intro-name"><b>F</b><b>a</b><b>n</b><b>d</b><b>s</b></span></div>
  <p class="intro-tag">From friction to flow.</p>
</div>
<script>(function(){var el=document.getElementById('intro');try{if(sessionStorage.getItem('fands-intro')==='1')el.classList.add('quick');sessionStorage.setItem('fands-intro','1')}catch(e){}el.addEventListener('animationend',function(e){if(e.target===el)el.remove()})})();</script>
'''

HEAD = '''<!doctype html>
<html lang="en">
<head>
<script defer src="https://cdn.userway.org/widget.js" data-account="OTeuoB7JqP"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  // Google Consent Mode defaults, set before GTM loads. No advertising storage is used. Analytics is turned off when the
  // visitor declined in the cookie banner or on /privacy-choices, or their browser sends a Global Privacy Control signal.
  (function(){{var off=!!navigator.globalPrivacyControl;try{{if(localStorage.getItem('fands-consent')==='denied'||localStorage.getItem('fands-optout')==='1')off=true}}catch(e){{}}
  gtag('consent','default',{{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:off?'denied':'granted'}});}})();
  window.dataLayer.push({{'gtm.start': new Date().getTime(), event: 'gtm.js'}});
</script>
<script async src="https://www.googletagmanager.com/gtm.js?id=GTM-N3C2TK2J"></script>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#080b10">
<meta name="robots" content="{robots}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700&family=Instrument+Sans:wght@600&display=swap">
<link rel="stylesheet" href="/assets/site.css?v={v}">
<link rel="icon" href="/brand/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/brand/favicon.ico" sizes="32x32">
<link rel="apple-touch-icon" sizes="180x180" href="/brand/apple-touch-icon.png?v=2">
<link rel="manifest" href="/site.webmanifest">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Fands">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="https://fands.io/brand/og-v2.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Fands: From friction to flow. AI systems built around a measurable outcome.">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="https://fands.io/brand/og-v2.png">
{extra}</head>
<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-N3C2TK2J" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
'''

SCULPTURE = '''<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.186.1/examples/jsm/"}}</script>
<script type="module" src="/assets/sculpture.js?v={v}"></script>
'''

TAIL = '''<div class="consent" role="region" aria-label="Cookie consent" hidden><p><strong>Cookies on fands.io</strong>We use analytics cookies to understand how the site is used. No advertising cookies. <a href="/cookies">Cookie Policy</a></p><div class="consent-actions"><button type="button" class="button ghost-dark" data-consent="denied">Decline</button><button type="button" class="button orange" data-consent="granted">Accept</button></div></div>
<a class="book-fab" href="/contact" {{{{cal}}}} aria-label="Book a free call">{{{{i:calendar:18}}}}<span class="long">Book a Free Call</span><span class="short">Book a call</span></a>
<script src="/assets/site.js?v={v}"></script>
{sculpture}<script>window.va=window.va||function(){{(window.vaq=window.vaq||[]).push(arguments)}};</script>
<script defer src="/_vercel/insights/script.js"></script>
<!-- Cal floating-popup embed code begins -->
<script type="text/javascript">
  (function (C, A, L) {{ let p = function (a, ar) {{ a.q.push(ar); }}; let d = C.document; C.Cal = C.Cal || function () {{ let cal = C.Cal; let ar = arguments; if (!cal.loaded) {{ cal.ns = {{}}; cal.q = cal.q || []; d.head.appendChild(d.createElement("script")).src = A; cal.loaded = true; }} if (ar[0] === L) {{ const api = function () {{ p(api, arguments); }}; const namespace = ar[1]; api.q = api.q || []; if(typeof namespace === "string"){{cal.ns[namespace] = cal.ns[namespace] || api;p(cal.ns[namespace], ar);p(cal, ["initNamespace", namespace]);}} else p(cal, ar); return;}} p(cal, ar); }}; }})(window, "https://app.cal.com/embed/embed.js", "init");
(function () {{ var boot = function () {{ Cal("init", "intro-call", {{origin:"https://app.cal.com"}}); Cal.config = Cal.config || {{}}; Cal.config.forwardQueryParams = true;
  Cal.ns["intro-call"]("ui", {{"hideEventTypeDetails":false,"layout":"month_view"}}); }};
  var go = function () {{ ('requestIdleCallback' in window) ? requestIdleCallback(boot, {{timeout: 2500}}) : setTimeout(boot, 1200); }};
  if (document.readyState === 'complete') go(); else addEventListener('load', go); }})();
</script>
<!-- Cal floating-popup embed code ends -->
</body>
</html>
'''

# {{cal}} expands to the attributes that open the Cal.com booking popup in place (the href stays /contact as a fallback).
CAL = '''data-cal-namespace="intro-call" data-cal-link="fands/intro-call" data-cal-config='{"layout":"month_view","useSlotsViewOnSmallScreen":"true"}\''''

# {{closing}} is the shared final call to action used at the end of most pages.
CLOSING = '''<section class="closing" aria-labelledby="closing-title">
    <div class="closing-top"><span>Start with one thing.</span><span>Make it count.</span></div>
    <a href="/contact" class="closing-link" {{cal}}><h2 id="closing-title">What’s your<br>next <em>move?</em></h2><span class="closing-arrow">{{i:up-right:80}}</span></a>
    <div class="closing-bottom"><p>Thirty minutes, free. Tell us where the work slows down.</p><a href="/contact" {{cal}}>Book a Free Call {{i:right:18}}</a></div>
  </section>'''


# {{legal-nav}}: one switcher shared by every legal document; each document has its own URL.
LEGAL = [('Privacy Policy', '/privacy'), ('Terms of Service', '/terms'), ('Cookie Policy', '/cookies'),
         ('AI & Client Data', '/ai-data-policy'), ('Accessibility', '/accessibility'), ('Your Privacy Choices', '/privacy-choices')]


def legal_nav(current):
    links = ''.join(f'<a href="{p}"' + (' aria-current="page"' if p == current else '') + f'>{n}</a>' for n, p in LEGAL)
    return f'<nav class="legal-nav" aria-label="Legal documents"><p class="fh">Legal documents</p>{links}</nav>'


# {{film}}: the company film player (cover image, play button; YouTube loads on click) and its VideoObject data.
FILM_ID = 'qrYEmKPt6mQ'
FILM = ('<div class="film-player" data-yt="' + FILM_ID + '" data-title="FANDS film: Your next lead shouldn’t wait until Monday">'
        '<button type="button" class="film-cover" aria-label="Play the FANDS film, 56 seconds">'
        '<img src="https://i.ytimg.com/vi/' + FILM_ID + '/maxresdefault.jpg" alt="" width="1280" height="720" loading="lazy" decoding="async">'
        '<span class="film-play"><svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7 4.5v15l12.5-7.5z"/></svg></span>'
        '<span class="film-meta"><b>Watch the film</b><small>0:56 · sound on</small></span></button></div>'
        '<p class="film-caption"><span>Our story in 56 seconds.</span><a href="https://www.youtube.com/watch?v=' + FILM_ID + '" target="_blank" rel="noopener">Watch on YouTube</a></p>')
FILM_LD = {"@context": "https://schema.org", "@type": "VideoObject", "name": "Your Next Lead Shouldn’t Wait Until Monday | Fands",
           "description": "FANDS, the AI systems and media agency, in 56 seconds: media earns the attention, systems earn the revenue.",
           "thumbnailUrl": ["https://i.ytimg.com/vi/" + FILM_ID + "/maxresdefault.jpg"], "uploadDate": "2026-11-11T18:29:04-08:00",
           "duration": "PT56S", "contentUrl": "https://www.youtube.com/watch?v=" + FILM_ID, "embedUrl": "https://www.youtube.com/embed/" + FILM_ID,
           "publisher": {"@id": "https://fands.io/#org"}}


def crumbs_html(crumbs):
    """Visible breadcrumb trail for the page head. crumbs = [["Services", "/services"], ["AI Operations", "/services/ai-operations"]]."""
    items = ['<li><a href="/">Home</a></li>']
    for i, (name, path) in enumerate(crumbs):
        last = i == len(crumbs) - 1
        items.append(f'<li><a href="{path}" aria-current="page">{name}</a></li>' if last else f'<li><a href="{path}">{name}</a></li>')
    return '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + ''.join(items) + '</ol></nav>'


def crumbs_schema(crumbs):
    trail = [["Home", "/"]] + crumbs
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + p} for i, (n, p) in enumerate(trail)]}


def ld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, separators=(',', ':'), ensure_ascii=False) + '</script>\n'


# Personal contact cards: one vCard per person, saved by the "Save contact" button on their links page.
# The photo is embedded (base64), so the card shows a face once it is added to the phone's contacts.
PEOPLE = {
    'seimur': {'first': 'Seimur', 'last': 'Ibragimov', 'title': 'Co-founder', 'email': 'seimur@fands.io', 'phone': '+17862604988',
               'url': 'https://seimur.fands.io', 'linkedin': 'https://www.linkedin.com/in/seimur-ibragimov/', 'telegram': 'https://t.me/seimur_ibr',
               'whatsapp': 'https://wa.me/17862604988'},
    'faris': {'first': 'Faris', 'last': 'Batayneh', 'title': 'Co-founder', 'email': 'faris@fands.io', 'phone': '',
              'url': 'https://faris.fands.io', 'linkedin': 'https://www.linkedin.com/in/farisba/'},
}


def vcard(slug, p):
    import base64
    def fold(line):  # vCard lines longer than 75 octets continue on the next line, indented by one space
        out = [line[:75]]; rest = line[75:]
        while rest: out.append(' ' + rest[:74]); rest = rest[74:]
        return '\r\n'.join(out)
    photo = base64.b64encode((ROOT / 'img' / 'links' / f'{slug}-vcard.jpg').read_bytes()).decode()
    lines = ['BEGIN:VCARD', 'VERSION:3.0', f"N:{p['last']};{p['first']};;;", f"FN:{p['first']} {p['last']}", 'ORG:FANDS', f"TITLE:{p['title']}",
             f"EMAIL;TYPE=INTERNET,WORK,PREF:{p['email']}"]
    if p.get('phone'): lines.append(f"TEL;TYPE=CELL,VOICE,PREF:{p['phone']}")
    lines += [f"URL:{p['url']}", 'URL:https://fands.io']
    for k in ('linkedin', 'telegram', 'whatsapp'):
        if p.get(k): lines.append(f"X-SOCIALPROFILE;TYPE={k}:{p[k]}")
    lines += ['NOTE:FANDS · AI Systems & Media Agency. From Friction to Flow.', f'PHOTO;ENCODING=b;TYPE=JPEG:{photo}', 'END:VCARD']
    return '\r\n'.join(fold(l) for l in lines) + '\r\n'


def main():
    import hashlib, datetime
    v = hashlib.sha1(b''.join((ROOT / 'assets' / f).read_bytes() for f in ('site.css', 'site.js', 'sculpture.js'))).hexdigest()[:8]
    pages = []
    for src in sorted((ROOT / 'src').glob('*.html')):
        first, body = src.read_text(encoding='utf-8').split('\n', 1)
        meta = json.loads(first)
        meta['src'] = src
        noindex = meta.get('noindex')
        # structured data on every page: who publishes it (Organization), what it is (WebPage type), where it sits (breadcrumbs)
        extra = ''
        if not noindex:
            extra = ld(SCHEMA)
            if meta['path'] == '/':
                extra += ld({"@context": "https://schema.org", "@type": "WebSite", "@id": SITE + "/#website", "name": "Fands", "url": SITE + "/", "publisher": {"@id": SITE + "/#org"}, "inLanguage": "en-US"})
            extra += ld({"@context": "https://schema.org", "@type": meta.get('type', 'WebPage'), "@id": SITE + meta['path'] + "#webpage", "url": SITE + meta['path'],
                         "name": meta['title'], "description": meta['description'], "isPartOf": {"@id": SITE + "/#website"}, "publisher": {"@id": SITE + "/#org"}, "inLanguage": "en-US"})
        if meta.get('hero'):
            extra += '<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>\n'
        crumbs = meta.get('crumbs')
        if crumbs:
            extra += ld(crumbs_schema(crumbs))
        body = body.replace('{{crumbs}}', crumbs_html(crumbs) if crumbs else '').replace('{{legal-nav}}', legal_nav(meta['path']))
        if '{{film}}' in body:  # pages that show the company film also describe it for search engines
            extra += ld(FILM_LD)
            body = body.replace('{{film}}', FILM)
        html = (HEAD.format(title=meta['title'], description=meta['description'], url=meta.get('canonical', SITE + meta['path']), v=v, extra=extra,
                            robots='noindex,follow' if noindex else 'index,follow,max-image-preview:large', og_type=meta.get('og_type', 'website'))
                + (INTRO if meta.get('hero') else '') + ('' if meta.get('bare') else HEADER) + '\n' + body.strip() + '\n'
                + ('' if meta.get('bare') else FOOTER) + '\n'
                + TAIL.format(v=v, sculpture=SCULPTURE.replace('{v}', v) if meta.get('hero') else ''))
        if meta.get('bare'):  # bare pages (the links page): no site header, footer or floating booking button
            html = re.sub(r'<a class="book-fab".*?</a>\n', '', html, flags=re.S)
        html = html.replace('{{closing}}', CLOSING).replace('{{cal}}', CAL)
        html = re.sub(r'\{\{i:([a-z-]+)(?::(\d+))?(?::([a-z-]+))?\}\}', icon, html)
        out = ROOT / meta['out']
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(html, encoding='utf-8')
        pages.append(meta)
        print(f'built {meta["out"]} ({len(html):,} bytes)')
    # contact cards for the personal links pages
    (ROOT / 'contact').mkdir(exist_ok=True)
    for slug, p in PEOPLE.items():
        (ROOT / 'contact' / f'{slug}.vcf').write_bytes(vcard(slug, p).encode('utf-8'))
    print(f'built contact cards ({len(PEOPLE)})')
    # sitemap: every indexable page, most important first; lastmod is the date its source file last changed
    pages = [m for m in pages if not m.get('noindex')]
    pages.sort(key=lambda m: (-float(m.get('priority', 0.5)), m['path']))
    def lastmod(m):
        return datetime.date.fromtimestamp(m['src'].stat().st_mtime).isoformat()
    rows = ''.join(f'  <url><loc>{SITE}{m["path"]}</loc><lastmod>{lastmod(m)}</lastmod><priority>{float(m.get("priority", 0.5)):.1f}</priority></url>\n' for m in pages)
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + rows + '</urlset>\n', encoding='utf-8')
    print(f'built sitemap.xml ({len(pages)} urls)')
    # robots.txt: everything public is crawlable, including AI search crawlers; the API and the 404 page are not
    ai_bots = ['GPTBot', 'OAI-SearchBot', 'ChatGPT-User', 'ClaudeBot', 'Claude-SearchBot', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended']
    robots = 'User-agent: *\nAllow: /\nDisallow: /api/\nDisallow: /404\n\n' + ''.join(f'User-agent: {b}\nAllow: /\nDisallow: /api/\n\n' for b in ai_bots) + f'Sitemap: {SITE}/sitemap.xml\n'
    (ROOT / 'robots.txt').write_text(robots, encoding='utf-8')
    # llms.txt: a plain summary of the site for AI assistants (GEO), generated from the same page list
    groups = [('Services', lambda p: p.startswith('/services')), ('Process and company', lambda p: p in ('/how-we-work', '/about', '/contact')),
              ('Case studies', lambda p: p.startswith('/case-studies')), ('Field Notes', lambda p: p.startswith('/insights')),
              ('Legal', lambda p: p in ('/privacy', '/terms', '/cookies', '/ai-data-policy', '/accessibility', '/privacy-choices'))]
    out = ['# Fands', '', '> ' + SCHEMA['description'], '',
           'Fands sells implementation, not software. Clients start with a free 30-minute call, then a paid AI Readiness Audit, then fixed-price builds and a Managed AI Retainer with a monthly results review. Contact: hello@fands.io. Book a call: https://cal.com/fands/intro-call', '']
    for title, test in groups:
        out += [f'## {title}', ''] + [f'- [{m["title"].replace(" | Fands", "")}]({SITE}{m["path"]}): {m["description"]}' for m in sorted(pages, key=lambda m: m['path']) if test(m['path'])] + ['']
    (ROOT / 'llms.txt').write_text('\n'.join(out), encoding='utf-8')
    print('built robots.txt and llms.txt')

if __name__ == '__main__':
    main()
