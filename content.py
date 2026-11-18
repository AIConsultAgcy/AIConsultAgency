"""Content layer for the Fands site.

Case studies and Field Notes articles live as JSON files in content/ (one file each). They are edited through the
/admin CMS or by hand, and build.py turns them into pages. Nothing here needs a third-party package.

content/cases/<slug>.json      one case study
content/insights/<slug>.json   one Field Notes article
content/videos.json            YouTube videos for the Field Notes digest (newest first)
"""
import datetime
import html as htmllib
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / 'content'


# ---------- a small Markdown renderer (headings, paragraphs, lists, tables, quotes, links, bold, italic) ----------
def inline(s):
    s = re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)', r'<a href="\2" target="_blank" rel="noopener noreferrer">\1</a>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)\s]+)\)', r'<a href="\2">\1</a>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])', r'<em>\1</em>', s)
    return s


def md_to_html(md, table_class=''):
    """Render the Markdown subset used on the site.

    ## Heading          -> h2          ### Heading -> h3
    - item              -> ul/li       1. item -> ol/li
    | a | b |           -> table (first row is the header, second row is the --- separator)
    > **Title**         -> a note box: the first line in bold is the title, the rest is its text
    ~ small print       -> <p class="fine">
    everything else     -> paragraphs separated by blank lines
    """
    blocks = [b for b in re.split(r'\n\s*\n', md.strip().replace('\r\n', '\n')) if b.strip()]
    out = []
    for block in blocks:
        lines = [l.rstrip() for l in block.split('\n')]
        first = lines[0]
        if first.startswith('## ') and len(lines) == 1:
            out.append('<h2>' + inline(first[3:].strip()) + '</h2>')
        elif first.startswith('### ') and len(lines) == 1:
            out.append('<h3>' + inline(first[4:].strip()) + '</h3>')
        elif all(re.match(r'\s*[-*] ', l) for l in lines):
            out.append('<ul>' + ''.join('<li>' + inline(re.sub(r'^\s*[-*] ', '', l)) + '</li>' for l in lines) + '</ul>')
        elif all(re.match(r'\s*\d+\. ', l) for l in lines):
            out.append('<ol>' + ''.join('<li>' + inline(re.sub(r'^\s*\d+\. ', '', l)) + '</li>' for l in lines) + '</ol>')
        elif first.startswith('|'):
            rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in lines if not re.match(r'^\|?\s*:?-{2,}', l.strip().lstrip('|'))]
            head, body = rows[0], rows[1:]
            cls = f' class="{table_class}"' if table_class else ''
            out.append(f'<table{cls}><thead><tr>' + ''.join('<th>' + inline(c) + '</th>' for c in head) + '</tr></thead><tbody>'
                       + ''.join('<tr>' + ''.join('<td>' + inline(c) + '</td>' for c in r) + '</tr>' for r in body) + '</tbody></table>')
        elif first.startswith('>'):
            text = [re.sub(r'^>\s?', '', l) for l in lines]
            m = re.match(r'^\*\*(.+?)\*\*\s*$', text[0])
            if m:
                out.append('<div class="note"><strong>' + inline(m.group(1)) + '</strong>' + ''.join('<p>' + inline(t) + '</p>' for t in text[1:] if t.strip()) + '</div>')
            else:
                out.append('<div class="note">' + ''.join('<p>' + inline(t) + '</p>' for t in text if t.strip()) + '</div>')
        elif re.match(r'^!\[[^\]]*\]\([^)\s]+\)\s*$', first) and len(lines) <= 2:
            m = re.match(r'^!\[([^\]]*)\]\(([^)\s]+)\)', first)
            cap = f'<figcaption>{inline(lines[1])}</figcaption>' if len(lines) == 2 else ''
            out.append(f'<figure class="article-figure"><img src="{m.group(2)}" alt="{esc(m.group(1))}" loading="lazy" decoding="async">{cap}</figure>')
        elif first.startswith('~ '):
            out.append('<p class="fine">' + inline(' '.join(l[2:] if i == 0 else l for i, l in enumerate(lines))) + '</p>')
        else:
            out.append('<p>' + inline(' '.join(lines)) + '</p>')
    return '\n    '.join(out)


# ---------- loading ----------
def _load(folder):
    items = []
    for f in sorted((CONTENT / folder).glob('*.json')):
        d = json.loads(f.read_text(encoding='utf-8'))
        d['slug'] = d.get('slug') or f.stem
        d['_file'] = f
        items.append(d)
    return items


def load_cases():
    return sorted(_load('cases'), key=lambda c: (c.get('order', 99), c['slug']))


def load_posts():
    return sorted(_load('insights'), key=lambda p: p.get('date', ''), reverse=True)


def load_videos():
    f = CONTENT / 'videos.json'
    if not f.exists():
        return []
    d = json.loads(f.read_text(encoding='utf-8'))
    return d.get('videos', []) if isinstance(d, dict) else d


def cover_figure(item):
    if not item.get('cover'):
        return ''
    cap = f'<figcaption>{esc(item["cover_caption"])}</figcaption>' if item.get('cover_caption') else ''
    return (f'<figure class="article-cover"><img src="{item["cover"]}" alt="{esc(item.get("cover_alt", ""))}" width="1600" height="1000" '
            f'decoding="async">{cap}</figure>\n  ')


def esc(s):
    return htmllib.escape(s, quote=False)


def _lines(main, em, mid=''):
    if not em:
        return esc(main)
    return esc(main) + '<br>' + (esc(mid) + ' ' if mid else '') + '<em>' + esc(em) + '</em>'


# ---------- case studies ----------
def case_path(c):
    return '/case-studies/' + c['slug']


BADGE = ('<span class="cs-badge" aria-hidden="true"><svg viewBox="0 0 64 64" width="22" height="22"><rect y="24" width="40" height="40" fill="#e0e6eb"/><rect x="24" width="40" height="40" fill="#e0e6eb"/><rect x="24" y="24" width="16" height="16" fill="#ff7547"/></svg>FANDS PROJECT</span>')


def case_card(c):
    feature = ' feature' if c.get('feature') else ''
    kpis = ''.join(f'<div><strong>{esc(k["value"])}</strong><span>{esc(k["label"])}</span></div>' for k in c.get('card_kpis', []))
    cover = f'<span class="case-cover"><img src="{c["cover"]}" alt="" width="1600" height="1000" loading="lazy" decoding="async">' + BADGE + '</span>' if c.get('cover') else ''
    return (f'<a class="case-card{feature}" href="{case_path(c)}">{cover}<div class="tags"><span class="tag">{esc(c["tag_industry"])}</span>'
            f'<span class="tag outline">{esc(c["tag_practice"])}</span></div><h3>{esc(c["card_title"])}</h3><p>{esc(c["card_summary"])}</p>'
            f'<div class="kpis">{kpis}</div><b>Read the case {{{{i:right:15}}}}</b></a>')


def case_cards_html(limit=None):
    cases = [c for c in load_cases() if not c.get('draft')]
    return '\n      '.join(case_card(c) for c in cases[:limit])


SERVICES = {
    'Business Process Automation': '/services/ai-operations#business-process-automation',
    'Lead-to-Revenue Automation': '/services/ai-operations#lead-to-revenue-automation',
    'Internal Knowledge Assistant & Analytics': '/services/ai-operations#knowledge-assistant-analytics',
    'AI Training & Enablement': '/services/ai-operations#ai-training',
    'AI Receptionist & Inbound Lead Capture': '/services/ai-assistants#ai-receptionist',
    'Custom AI Agents & Apps': '/services/ai-assistants#custom-ai-agents',
    'AI Content Engine': '/services/media-growth#ai-content-engine',
    'AI Search Visibility (GEO/AEO) + Local SEO': '/services/media-growth#ai-search-visibility',
    'Paid Media Management': '/services/media-growth#paid-media',
    'Branding & Design': '/services/media-growth#branding-design',
    'Web & App Development': '/services/digital-development#web-app-development',
    'Website & E-commerce Automation': '/services/digital-development#ecommerce-automation',
    'AI Readiness Audit & Roadmap': '/services/strategy-entry#ai-readiness-audit',
    'Managed AI Retainer': '/services/strategy-entry#managed-ai-retainer',
}
ICONS_OK = {'compass', 'workflow', 'megaphone', 'message', 'code', 'gauge', 'target', 'scale', 'chart', 'clock', 'plug', 'pen', 'search', 'house',
            'sparkles', 'heart-pulse', 'building', 'briefcase', 'store', 'shield-check', 'key-round', 'users', 'circle-dollar-sign', 'calendar',
            'globe', 'check', 'phone', 'mail'}


def _paras(text):
    return ''.join('<p>' + inline(esc_keep(p.strip())) + '</p>' for p in re.split(r'\n\s*\n', text.strip()) if p.strip())


def esc_keep(s):
    # escape < and > but leave entities such as &amp; alone, then Markdown links still work
    return s.replace('<', '&lt;').replace('>', '&gt;')


def _h2(title, id_):
    words = title.split()
    if len(words) < 2:
        return f'<h2 id="{id_}" data-reveal>{esc(title)}</h2>'
    k = (len(words) + 1) // 2
    return f'<h2 id="{id_}" data-reveal>{esc(" ".join(words[:k]))}<br><span>{esc(" ".join(words[k:]))}</span></h2>'


def _og_size(path):
    # width and height of a local JPEG or PNG, for the Open Graph tags and the img attributes
    import struct
    f = ROOT / path.lstrip('/')
    try:
        d = f.read_bytes()
        if d[:8] == b'\x89PNG\r\n\x1a\n':
            return struct.unpack('>II', d[16:24])
        i = 2
        while d[:2] == b'\xff\xd8' and i < len(d):
            if d[i] != 0xFF:
                i += 1
                continue
            if d[i + 1] in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack('>HH', d[i + 5:i + 9])
                return w, h
            i += 2 + struct.unpack('>H', d[i + 2:i + 4])[0]
    except OSError:
        pass
    return 1600, 1000


def case_page(c):
    url = 'https://fands.io' + case_path(c)
    name = c['crumb']
    cover = c.get('cover', '')
    cw, ch = _og_size(cover) if cover else (1600, 1000)
    crumbs = [['Case studies', '/case-studies'], [name, case_path(c)]]
    meta = {'out': f'case-studies/{c["slug"]}.html', 'path': case_path(c), 'title': c['seo_title'], 'description': c['seo_description'],
            'crumbs': crumbs, 'priority': 0.6, 'type': 'WebPage', 'og_type': 'article'}
    if cover:
        meta.update(og_image='https://fands.io' + cover, og_w=cw, og_h=ch, og_alt=c.get('cover_alt', name))

    link = c.get('link') or {}
    visit = ''
    if link.get('url'):
        visit = (f'<a class="button orange" href="{link["url"]}" target="_blank" rel="noopener noreferrer" '
                 f'data-track="Case: {esc(name)} - {esc(link.get("label", "Visit"))}">{esc(link.get("label", "Visit"))} {{{{i:up-right:19}}}}</a>')
    actions = (visit + '<a class="button ghost" href="/contact" {{cal}}>Start a project {{i:right:18}}</a>') if visit else \
        ('<a class="button orange" href="/contact" {{cal}}>Start a project {{i:up-right:19}}</a><a class="button ghost" href="/case-studies">All projects {{i:right:18}}</a>')

    facts = ''.join(f'<div><dt>{esc(f["label"])}</dt><dd>{esc(f["value"])}</dd></div>' for f in c.get('facts', []))
    out = [f'''<main id="main">
  <section class="page-head cs-head">
    {{{{crumbs}}}}
    <p class="eyebrow">{esc(c['eyebrow'])}</p>
    <h1>{_lines(c['headline_main'], c.get('headline_em'))}</h1>
    <p class="lead">{esc(c['lead'])}</p>
    <div class="head-actions">{actions}</div>
    <dl class="facts">{facts}</dl>
  </section>''']

    if cover:
        cap = f'<figcaption>{esc(c["cover_caption"])}</figcaption>' if c.get('cover_caption') else ''
        out.append(f'''  <figure class="cs-cover wrap"><div class="cs-frame"><img src="{cover}" alt="{esc(c.get('cover_alt', name))}" width="{cw}" height="{ch}" fetchpriority="high" decoding="async">{BADGE}</div>{cap}</figure>''')

    stats = c.get('highlights') or c.get('card_kpis') or []
    if stats:
        out.append('  <section class="cs-stats wrap" aria-label="Project at a glance">' +
                   ''.join(f'<div><strong>{esc(k["value"])}</strong><span>{esc(k["label"])}</span></div>' for k in stats) + '</section>')

    if c.get('challenge'):
        out.append(f'''  <section class="section wrap cs-split" aria-labelledby="cs-challenge">
    <div><p class="eyebrow">{esc(c.get('challenge_label', 'THE STARTING POINT'))}</p>{_h2(c.get('challenge_title', 'Where it started'), 'cs-challenge')}</div>
    <div class="cs-text">{_paras(c['challenge'])}</div>
  </section>''')

    if c.get('built'):
        cards = ''
        for i, b_ in enumerate(c['built'], 1):
            ic = b_.get('icon') if b_.get('icon') in ICONS_OK else 'sparkles'
            cards += (f'<article class="icard"><i class="hub-ico" aria-hidden="true">{{{{i:{ic}:26}}}}</i><span>{i:02d}</span>'
                      f'<h3>{esc(b_["title"])}</h3><p>{inline(esc_keep(b_["text"]))}</p></article>')
        out.append(f'''  <section class="section wrap" aria-labelledby="cs-built">
    <div class="section-head">{_h2(c.get('built_title', 'What we built'), 'cs-built')}<p>{esc(c.get('built_intro', ''))}</p></div>
    <div class="cards-3 cs-built">{cards}</div>
  </section>''')

    if c.get('ai_text'):
        pts = ''.join(f'<li>{{{{i:check:18}}}}<span>{esc(x)}</span></li>' for x in c.get('ai_points', []))
        out.append(f'''  <section class="section wrap dark rounded-top cs-ai" aria-labelledby="cs-ai">
    <div class="cs-ai-grid">
      <div><p class="eyebrow">{esc(c.get('ai_label', 'HOW AI IS USED'))}</p><h2 id="cs-ai">{esc(c.get('ai_title', 'AI with a person in control'))}</h2><p>{esc(c['ai_text'])}</p></div>
      <ul class="cs-points">{pts}</ul>
    </div>
  </section>''')

    if c.get('gallery'):
        figs = ''.join(f'<figure><img src="{g["image"]}" alt="{esc(g.get("alt", ""))}" loading="lazy" decoding="async">' +
                       (f'<figcaption>{esc(g["caption"])}</figcaption>' if g.get('caption') else '') + '</figure>' for g in c['gallery'])
        out.append(f'  <section class="section wrap" aria-label="Project screens"><div class="cs-gallery">{figs}</div></section>')

    if c.get('body'):
        out.append(f'  <section class="section wrap"><div class="article cs-extra">{md_to_html(c["body"])}</div></section>')

    if c.get('outcomes'):
        outs = ''.join(f'<article class="cs-out"><span>{i:02d}</span><h3>{esc(o["title"])}</h3><p>{esc(o["text"])}</p></article>' for i, o in enumerate(c['outcomes'], 1))
        out.append(f'''  <section class="section wrap" aria-labelledby="cs-outcomes">
    <div class="section-head">{_h2(c.get('outcomes_title', 'What it gives the business'), 'cs-outcomes')}<p>{esc(c.get('outcomes_intro', ''))}</p></div>
    <div class="cs-outcomes">{outs}</div>
  </section>''')

    svcs = [(n, SERVICES[n]) for n in c.get('services', []) if n in SERVICES]
    if svcs:
        chips = ''.join(f'<a href="{u}" data-track="Case: {esc(name)} - service {esc(n)}">{esc(n)} {{{{i:up-right:15}}}}</a>' for n, u in svcs)
        out.append(f'''  <section class="section wrap soft rounded-top cs-services" aria-labelledby="cs-services">
    <div class="section-head">{_h2('Services behind this project', 'cs-services')}<p>The same services are available for your business.</p></div>
    <div class="cs-chips">{chips}</div>
  </section>''')

    others = [o for o in load_cases() if o['slug'] != c['slug'] and not o.get('draft')][:3]
    if others:
        out.append(f'''  <section class="section wrap" aria-labelledby="cs-more">
    <div class="section-head">{_h2('More projects', 'cs-more')}<p>Other things we have built.</p></div>
    <div class="case-grid">{''.join(case_card(o) for o in others)}</div>
    <div class="section-foot"><p>Have something similar in mind?</p><a class="arrow-link" href="/contact" {{{{cal}}}}>Start a project {{{{i:up-right:15}}}}</a></div>
  </section>''')

    ld = {"@context": "https://schema.org", "@type": "Article", "headline": c.get('schema_headline', c['card_title']),
          "description": c.get('schema_description', c['seo_description']), "author": {"@id": "https://fands.io/#org"},
          "publisher": {"@id": "https://fands.io/#org"}, "mainEntityOfPage": url, "url": url,
          "image": ['https://fands.io' + cover] if cover else ["https://fands.io/brand/og-v2.png"], "inLanguage": "en-US"}
    if link.get('url'):
        ld['about'] = {"@type": "WebSite" if 'apps.apple.com' not in link['url'] else "SoftwareApplication", "name": name, "url": link['url']}
    out.append('  {{closing}}\n  <script type="application/ld+json">' + json.dumps(ld, separators=(',', ':'), ensure_ascii=False) + '</script>\n</main>\n')
    return meta, '\n'.join(out)


# ---------- Field Notes articles ----------
def post_path(p):
    return '/insights/' + p['slug']


def post_date_label(p):
    try:
        return datetime.date.fromisoformat(p['date']).strftime('%b %Y')
    except (KeyError, ValueError):
        return ''


def post_card(p, heading='h2', with_date=True):
    cover = p.get('cover', '/img/insights/first-workflow-cover.svg')
    tags = f'<span class="tag">{esc(p["label"])}</span><span class="tag outline">{esc(str(p["minutes"]))} min read</span>'
    if with_date and post_date_label(p):
        tags += f'<span class="tag outline">{post_date_label(p)}</span>'
    return (f'<article class="post-card">\n        <a class="post-cover" href="{post_path(p)}" tabindex="-1" aria-hidden="true"><img src="{cover}" alt="" width="1600" height="1000" loading="lazy" decoding="async"></a>\n'
            f'        <div class="post-body">\n          <div class="post-meta">{tags}</div>\n'
            f'          <{heading}><a href="{post_path(p)}">{esc(p["card_title"])}</a></{heading}>\n          <p>{esc(p["card_summary"])}</p>\n'
            f'          <a class="arrow-link" href="{post_path(p)}">{esc(p.get("card_cta", "Read the guide"))} {{{{i:right:15}}}}</a>\n        </div>\n      </article>')


def post_cards_html():
    return '\n      '.join(post_card(p) for p in load_posts() if not p.get('draft'))


def post_page(p):
    url = 'https://fands.io' + post_path(p)
    crumbs = [['Field Notes', '/insights'], [p['crumb'], post_path(p)]]
    meta = {'out': f'insights/{p["slug"]}.html', 'path': post_path(p), 'title': p['seo_title'], 'description': p['seo_description'],
            'priority': 0.6, 'type': 'WebPage', 'crumbs': crumbs, 'og_type': 'article'}
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": p.get('schema_headline', p['card_title']),
          "description": p.get('schema_description', p['seo_description']), "datePublished": p.get('date', ''),
          "author": {"@id": "https://fands.io/#org"}, "publisher": {"@id": "https://fands.io/#org"}, "mainEntityOfPage": url,
          "image": "https://fands.io/brand/og-v2.png"}
    c_main = p.get('closing_main', 'Find the first')
    c_mid = p.get('closing_mid', 'useful')
    c_em = p.get('closing_em', 'system.')
    c_text = p.get('closing_text', 'Tell us which handoff you would start with.')
    c_btn = p.get('closing_button', 'Request a workflow review')
    body = f'''<main id="main">
  <section class="page-head">{{{{crumbs}}}}<p class="eyebrow">{esc(p['eyebrow'])}</p><h1>{_lines(p['headline_main'], p.get('headline_em'), p.get('headline_mid', ''))}</h1><p>{esc(p['subtitle'])}</p></section>
  {cover_figure(p)}<article class="article">
    {md_to_html(p['body'])}
  </article>
  <section class="closing"><div class="closing-top"><span>Start with one thing.</span><span>Make it count.</span></div><a href="/contact" class="closing-link"><h2>{esc(c_main)}<br>{esc(c_mid)} <em>{esc(c_em)}</em></h2><span class="closing-arrow">{{{{i:up-right:80}}}}</span></a><div class="closing-bottom"><p>{esc(c_text)}</p><a href="/contact">{esc(c_btn)} {{{{i:right:18}}}}</a></div></section>
  <script type="application/ld+json">{json.dumps(ld, separators=(',', ':'), ensure_ascii=False)}</script>
</main>
'''
    return meta, body


def generated_pages():
    """(meta, body, source file) for every page that comes from content/ instead of src/."""
    pages = []
    for c in load_cases():
        if not c.get('draft'):
            meta, body = case_page(c)
            pages.append((meta, body, c['_file']))
    for p in load_posts():
        if not p.get('draft'):
            meta, body = post_page(p)
            pages.append((meta, body, p['_file']))
    return pages
