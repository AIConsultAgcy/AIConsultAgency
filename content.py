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


def slugify(text):
    t = re.sub(r'<[^>]+>', '', text).lower()
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')
    return t or 'section'


def md_to_html(md, table_class='', headings=None):
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
    seen = {}
    for block in blocks:
        lines = [l.rstrip() for l in block.split('\n')]
        first = lines[0]
        if (first.startswith('## ') or first.startswith('### ')) and len(lines) == 1:
            level = 2 if first.startswith('## ') else 3
            text = first[level + 1:].strip()
            hid = slugify(text)
            n = seen.get(hid, 0)
            seen[hid] = n + 1
            if n:
                hid = f'{hid}-{n + 1}'
            if headings is not None:
                headings.append((level, re.sub(r'\*\*|\*', '', re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)), hid))
            out.append(f'<h{level} id="{hid}">' + inline(text) + f'</h{level}>')
        elif all(re.match(r'\s*[-*] ', l) for l in lines):
            out.append('<ul>' + ''.join('<li>' + inline(re.sub(r'^\s*[-*] ', '', l)) + '</li>' for l in lines) + '</ul>')
        elif all(re.match(r'\s*\d+\. ', l) for l in lines):
            out.append('<ol>' + ''.join('<li>' + inline(re.sub(r'^\s*\d+\. ', '', l)) + '</li>' for l in lines) + '</ol>')
        elif first.startswith('|'):
            rows = [[c.strip() for c in l.strip().strip('|').split('|')] for l in lines if not re.match(r'^\|?\s*:?-{2,}', l.strip().lstrip('|'))]
            head, body = rows[0], rows[1:]
            cls = f' class="{table_class}"' if table_class else ''
            out.append(f'<div class="table-wrap"><table{cls}><thead><tr>' + ''.join('<th>' + inline(c) + '</th>' for c in head) + '</tr></thead><tbody>'
                       + ''.join('<tr>' + ''.join('<td>' + inline(c) + '</td>' for c in r) + '</tr>' for r in body) + '</tbody></table></div>')
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
    return sorted(_load('insights'), key=lambda p: (p.get('date', ''), -p.get('order', 99)), reverse=True)


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
    return (f'<figure class="article-cover"><img {responsive(item["cover"], "(max-width: 1100px) 100vw, 1100px")} alt="{esc(item.get("cover_alt", ""))}" width="1600" height="1000" '
            f'decoding="async">{cap}</figure>\n  ')


def esc(s):
    return htmllib.escape(s, quote=False)


def _lines(main, em, mid=''):
    if not em:
        return esc(main)
    return esc(main) + '<br>' + (esc(mid) + ' ' if mid else '') + '<em>' + esc(em) + '</em>'


# ---------- responsive images ----------
WIDTHS = (480, 800, 1200, 1600)


def make_variants(path):
    # make WebP copies of a local JPEG or PNG at several widths; needs Pillow and is skipped quietly without it
    try:
        from PIL import Image
    except ImportError:
        return
    src = ROOT / path.lstrip('/')
    if src.suffix.lower() not in ('.jpg', '.jpeg', '.png') or not src.exists():
        return
    with Image.open(src) as im:
        im = im.convert('RGB')
        for w in WIDTHS:
            if w > im.width:
                continue
            dest = src.with_name(f'{src.stem}-{w}.webp')
            if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
                continue
            im.resize((w, round(im.height * w / im.width)), Image.LANCZOS).save(dest, 'WEBP', quality=80, method=6)


def responsive(path, sizes):
    # returns the src, srcset and sizes attributes for an image, using WebP copies when they exist
    if not path or path.rsplit('.', 1)[-1].lower() not in ('jpg', 'jpeg', 'png'):
        return f'src="{path}"'
    make_variants(path)
    base = path.rsplit('.', 1)[0]
    found = [(w, f'{base}-{w}.webp') for w in WIDTHS if (ROOT / f'{base}-{w}.webp'.lstrip('/')).exists()]
    if not found:
        return f'src="{path}"'
    mid = [u for w, u in found if w >= 1200] or [found[-1][1]]
    return f'src="{mid[0]}" srcset="' + ', '.join(f'{u} {w}w' for w, u in found) + f'" sizes="{sizes}"'


# ---------- case studies ----------
def case_path(c):
    return '/case-studies/' + c['slug']


BADGE = ('<span class="cs-badge" aria-hidden="true"><svg viewBox="0 0 64 64" width="22" height="22"><rect y="24" width="40" height="40" fill="#e0e6eb"/><rect x="24" width="40" height="40" fill="#e0e6eb"/><rect x="24" y="24" width="16" height="16" fill="#ff7547"/></svg>FANDS PROJECT</span>')


def badge(c):
    # "badge_bottom": true moves the badge to the bottom right when the cover has text in its top left corner
    return BADGE.replace('cs-badge', 'cs-badge br', 1) if c.get('badge_bottom') else BADGE


def case_card(c):
    feature = ' feature' if c.get('feature') else ''
    kpis = ''.join(f'<div><strong>{esc(k["value"])}</strong><span>{esc(k["label"])}</span></div>' for k in c.get('card_kpis', []))
    cover = (f'<span class="case-cover"><img {responsive(c["cover"], "(max-width: 767px) 92vw, 33vw")} alt="" width="1600" height="1000" loading="lazy" decoding="async">' + badge(c) + '</span>') if c.get('cover') else ''
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
        out.append(f'''  <figure class="cs-cover wrap"><div class="cs-frame"><img {responsive(cover, '(max-width: 1100px) 100vw, 1040px')} alt="{esc(c.get('cover_alt', name))}" width="{cw}" height="{ch}" fetchpriority="high" decoding="async">{badge(c)}</div>{cap}</figure>''')

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
        figs = ''.join(f'<figure><img {responsive(g["image"], "(max-width: 767px) 100vw, 50vw")} alt="{esc(g.get("alt", ""))}" loading="lazy" decoding="async">' +
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
DEFAULT_AUTHOR = {'name': 'Fands Team', 'url': 'https://fands.io/about'}


def post_path(p):
    return '/insights/' + p['slug']


def post_date_label(p):
    try:
        return datetime.date.fromisoformat(p['date']).strftime('%b %Y')
    except (KeyError, ValueError):
        return ''


def long_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f'{d:%B} {d.day}, {d.year}'


def _words(md):
    return len(re.findall(r"[A-Za-z0-9$%][A-Za-z0-9$%'’.-]*", re.sub(r'\]\([^)]*\)', ' ', md)))


def post_minutes(p):
    return int(p.get('minutes') or max(1, round(_words(p['body']) / 200)))


def post_card(p, heading='h2', with_date=True):
    cover = p.get('cover', '/img/insights/first-workflow-cover.svg')
    tags = f'<span class="tag">{esc(p["label"])}</span><span class="tag outline">{post_minutes(p)} min read</span>'
    if with_date and post_date_label(p):
        tags += f'<span class="tag outline">{post_date_label(p)}</span>'
    return (f'<article class="post-card">\n        <a class="post-cover" href="{post_path(p)}" tabindex="-1" aria-hidden="true"><img {responsive(cover, "(max-width: 767px) 92vw, 33vw")} alt="" width="1600" height="1000" loading="lazy" decoding="async"></a>\n'
            f'        <div class="post-body">\n          <div class="post-meta">{tags}</div>\n'
            f'          <{heading}><a href="{post_path(p)}">{esc(p["card_title"])}</a></{heading}>\n          <p>{esc(p["card_summary"])}</p>\n'
            f'          <a class="arrow-link" href="{post_path(p)}">{esc(p.get("card_cta", "Read the guide"))} {{{{i:right:15}}}}</a>\n        </div>\n      </article>')


def post_cards_html():
    return '\n      '.join(post_card(p) for p in load_posts() if not p.get('draft'))


def related_posts(p, n=3):
    others = [o for o in load_posts() if o['slug'] != p['slug'] and not o.get('draft')]
    mine = set(p.get('tags', []))
    others.sort(key=lambda o: -len(mine & set(o.get('tags', []))))  # stable: ties stay newest first
    return others[:n]


def toc_html(heads, extra):
    h2 = [h for h in heads if h[0] == 2]
    if len(h2) < 3:
        return ''
    items = ''
    i = 0
    while i < len(heads):
        lvl, text, hid = heads[i]
        if lvl == 2:
            subs = ''
            j = i + 1
            while j < len(heads) and heads[j][0] == 3:
                subs += f'<li><a href="#{heads[j][2]}">{esc(heads[j][1])}</a></li>'
                j += 1
            items += f'<li><a href="#{hid}">{esc(text)}</a>' + (f'<ol>{subs}</ol>' if subs else '') + '</li>'
            i = j
        else:
            i += 1
    items += ''.join(f'<li><a href="#{hid}">{esc(t)}</a></li>' for t, hid in extra)
    return f'<nav class="toc" aria-label="In this article"><details open><summary class="toc-title">In this article</summary><ol>{items}</ol></details></nav>'


def author_ld(p):
    a = p.get('author') or DEFAULT_AUTHOR
    if a.get('name') in (None, 'Fands Team', 'Fands'):
        return {"@type": "Organization", "name": "Fands", "url": "https://fands.io/", "@id": "https://fands.io/#org"}
    return {"@type": "Person", "name": a['name'], "url": a.get('url', 'https://fands.io/about'), "worksFor": {"@id": "https://fands.io/#org"}}


def post_page(p):
    url = 'https://fands.io' + post_path(p)
    crumbs = [['Field Notes', '/insights'], [p['crumb'], post_path(p)]]
    cover = p.get('cover', '')
    cw, ch = _og_size(cover) if cover else (1600, 1000)
    updated = p.get('updated') or p.get('date', '')
    minutes = post_minutes(p)
    author = p.get('author') or DEFAULT_AUTHOR
    category = p.get('category', 'AI for small business')
    meta = {'out': f'insights/{p["slug"]}.html', 'path': post_path(p), 'title': p['seo_title'], 'description': p['seo_description'],
            'priority': 0.6, 'type': 'WebPage', 'crumbs': crumbs, 'og_type': 'article', 'lastmod': updated}
    if cover:
        meta.update(og_image='https://fands.io' + cover, og_w=cw, og_h=ch, og_alt=p.get('cover_alt', p['card_title']))
    head = [f'<meta property="article:published_time" content="{p.get("date", "")}">', f'<meta property="article:modified_time" content="{updated}">',
            f'<meta property="article:section" content="{esc(category)}">', f'<meta property="article:author" content="{esc(author.get("name", "Fands Team"))}">']
    head += [f'<meta property="article:tag" content="{esc(t)}">' for t in p.get('tags', [])]
    head.append(f'<link rel="alternate" type="text/markdown" href="{post_path(p)}.md" title="{esc(p["card_title"])} (Markdown)">')
    meta['head_extra'] = '\n'.join(head) + '\n'

    headings = []
    body_html = md_to_html(p['body'], headings=headings)
    extra = []
    faq = p.get('faq') or []
    sources = p.get('sources') or []
    if faq:
        extra.append(('Frequently asked questions', 'faq'))
    if sources:
        extra.append(('Sources and further reading', 'sources'))

    dates = f'Published <time datetime="{p["date"]}">{long_date(p["date"])}</time>' + (f' · Updated <time datetime="{updated}">{long_date(updated)}</time>' if updated != p['date'] else '')
    byline = f'<p class="byline">By <a href="{author.get("url", "/about")}">{esc(author.get("name", "Fands Team"))}</a> · {dates} · {minutes} min read</p>'

    parts = [f'''<main id="main">
  <section class="page-head">{{{{crumbs}}}}<p class="eyebrow">{esc(p['eyebrow'])}</p><h1>{_lines(p['headline_main'], p.get('headline_em'), p.get('headline_mid', ''))}</h1><p>{esc(p['subtitle'])}</p>{byline}</section>
  {cover_figure(p)}''']
    main = []
    if p.get('takeaways'):
        main.append('<aside class="takeaways" aria-labelledby="takeaways-title"><p class="takeaways-title" id="takeaways-title">Key takeaways</p><ul>' +
                    ''.join(f'<li>{inline(esc_keep(t))}</li>' for t in p['takeaways']) + '</ul></aside>')
    main.append(f'<article class="post-article">\n    {body_html}\n  </article>')
    if faq:
        main.append('<section class="faq-block" aria-labelledby="faq"><h2 id="faq">Frequently asked questions</h2>' +
                    ''.join(f'<h3>{esc(f["q"])}</h3><p>{inline(esc_keep(f["a"]))}</p>' for f in faq) + '</section>')
    if sources:
        main.append('<section class="sources" aria-labelledby="sources"><h2 id="sources">Sources and further reading</h2><ol>' +
                    ''.join(f'<li><a href="{s["url"]}" target="_blank" rel="noopener noreferrer">{esc(s["title"])}</a>' + (f' <span>{esc(s["publisher"])}</span>' if s.get('publisher') else '') + '</li>' for s in sources) +
                    '</ol></section>')
    main.append(f'<aside class="author-box"><p class="eyebrow">WRITTEN BY</p><p class="author-name">{esc(author.get("name", "Fands Team"))}</p>'
                '<p>We are an AI implementation agency for small and mid-size businesses. We find where AI will pay off, build it into the way your team already works and measure the result.</p>'
                '<a class="arrow-link" href="/about">About Fands {{i:right:15}}</a></aside>')
    main.append('<aside class="subscribe-card"><p class="subscribe-title">One useful idea, every two weeks.</p><p>Workflow breakdowns and measurement methods for small and mid-size businesses. No hype.</p>'
                '<a class="button orange" href="/insights#field-notes-signup">Get Field Notes {{i:up-right:18}}</a></aside>')
    from urllib.parse import quote
    enc = quote(url, safe='')
    share = (f'<div class="share"><p class="toc-title">Share</p>'
             f'<a href="https://www.linkedin.com/sharing/share-offsite/?url={enc}" target="_blank" rel="noopener noreferrer" data-track="Share: LinkedIn - {esc(p["slug"])}">LinkedIn</a>'
             f'<a href="https://twitter.com/intent/tweet?url={enc}&text={quote(p["card_title"])}" target="_blank" rel="noopener noreferrer" data-track="Share: X - {esc(p["slug"])}">X</a>'
             f'<button type="button" data-copy="{url}">Copy link</button>'
             f'<a class="md-link" href="{post_path(p)}.md" data-track="Markdown view - {esc(p["slug"])}">Read as Markdown</a></div>')
    parts.append('<div class="post-layout wrap"><aside class="post-aside">' + toc_html(headings, extra) + share + '</aside><div class="post-main">' + ''.join(main) + '</div></div>')
    rel = related_posts(p)
    if rel:
        parts.append('<section class="section wrap" aria-labelledby="more-notes"><div class="section-head"><h2 id="more-notes" data-reveal>Keep<br><span>reading.</span></h2><p>More field notes on putting AI to work in a small business.</p></div><div class="post-grid">' +
                     ''.join(post_card(o, 'h3', False) for o in rel) + '</div></section>')
    c_main = p.get('closing_main', 'Find the first')
    c_mid = p.get('closing_mid', 'useful')
    c_em = p.get('closing_em', 'system.')
    c_text = p.get('closing_text', 'Tell us which handoff you would start with.')
    c_btn = p.get('closing_button', 'Request a workflow review')
    parts.append(f'<section class="closing"><div class="closing-top"><span>Start with one thing.</span><span>Make it count.</span></div><a href="/contact" class="closing-link"><h2>{esc(c_main)}<br>{esc(c_mid)} <em>{esc(c_em)}</em></h2><span class="closing-arrow">{{{{i:up-right:80}}}}</span></a><div class="closing-bottom"><p>{esc(c_text)}</p><a href="/contact">{esc(c_btn)} {{{{i:right:18}}}}</a></div></section>')

    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p.get('schema_headline', p['card_title']),
          "description": p.get('schema_description', p['seo_description']), "datePublished": p.get('date', ''), "dateModified": updated,
          "author": author_ld(p), "publisher": {"@id": "https://fands.io/#org"}, "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "url": url,
          "image": ['https://fands.io' + cover] if cover else ["https://fands.io/brand/og-v2.png"], "wordCount": _words(p['body']),
          "timeRequired": f"PT{minutes}M", "articleSection": category, "inLanguage": "en-US", "isAccessibleForFree": True}
    if p.get('tags'):
        ld['keywords'] = ', '.join(p['tags'])
    if sources:
        ld['citation'] = [{"@type": "CreativeWork", "name": s['title'], "url": s['url']} for s in sources]
    scripts = '<script type="application/ld+json">' + json.dumps(ld, separators=(',', ':'), ensure_ascii=False) + '</script>'
    if faq:
        fld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f['q'], "acceptedAnswer": {"@type": "Answer", "text": re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', f['a'])}} for f in faq]}
        scripts += '\n  <script type="application/ld+json">' + json.dumps(fld, separators=(',', ':'), ensure_ascii=False) + '</script>'
    parts.append(scripts + '\n</main>\n')
    return meta, '\n  '.join(x for x in parts if x)


def post_markdown(p):
    # a clean Markdown version of an article, for AI assistants, agents and offline reading
    url = 'https://fands.io' + post_path(p)
    updated = p.get('updated') or p['date']
    head = f"{p['headline_main']} {p.get('headline_mid', '')} {p.get('headline_em', '')}"
    head = re.sub(r'\s+', ' ', head).strip()
    author = (p.get('author') or DEFAULT_AUTHOR).get('name', 'Fands Team')
    out = ['---', f'title: {json.dumps(p["card_title"], ensure_ascii=False)}', f'url: {url}', f'published: {p["date"]}', f'updated: {updated}',
           f'author: {author}', f'category: {p.get("category", "AI for small business")}', 'tags: [' + ', '.join(p.get('tags', [])) + ']',
           f'description: {json.dumps(p["seo_description"], ensure_ascii=False)}', f'reading_time_minutes: {post_minutes(p)}', '---', '',
           f'# {head}', '', p['subtitle'], '']
    if p.get('takeaways'):
        out += ['## Key takeaways', ''] + [f'- {t}' for t in p['takeaways']] + ['']
    out += [p['body'].strip(), '']
    if p.get('faq'):
        out += ['## Frequently asked questions', '']
        for f in p['faq']:
            out += [f'### {f["q"]}', '', f['a'], '']
    if p.get('sources'):
        out += ['## Sources and further reading', ''] + [f'- [{x["title"]}]({x["url"]})' + (f' ({x["publisher"]})' if x.get('publisher') else '') for x in p['sources']] + ['']
    return '\n'.join(out).strip() + '\n'


def llms_full():
    posts = [p for p in load_posts() if not p.get('draft')]
    head = '# Fands Field Notes: full text\n\n> Practical notes on putting AI to work in a small or mid-size business. Each note is also available as Markdown at its address plus .md.\n\n'
    return head + '\n\n---\n\n'.join(post_markdown(p) for p in posts)


def lint_posts():
    # quality checks for Field Notes articles; returns a list of warnings (empty is good)
    warns = []
    for p in load_posts():
        if p.get('draft'):
            continue
        sl = p['slug']
        w = lambda m: warns.append(f'{sl}: {m}')  # noqa: E731
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', sl):
            w('slug must be lowercase words joined by hyphens')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', p.get('date', '')):
            w('date must be YYYY-MM-DD')
        if len(p.get('seo_title', '')) > 60:
            w(f'seo_title is {len(p["seo_title"])} characters, keep it at 60 or fewer')
        d = len(p.get('seo_description', ''))
        if not 70 <= d <= 160:
            w(f'seo_description is {d} characters, aim for 70 to 160')
        if not p.get('cover_alt'):
            w('cover_alt is missing')
        if not p.get('takeaways'):
            w('add 3 to 5 key takeaways')
        h2 = len(re.findall(r'(?m)^## ', p['body']))
        if h2 < 3:
            w(f'only {h2} sections (## headings), use at least 3')
        if _words(p['body']) < 600:
            w(f'only {_words(p["body"])} words, aim for 600 or more')
        if not re.search(r'\]\(/[a-z]', p['body']):
            w('no internal link in the body (link to a service, case study or another note)')
        if not p.get('sources') and not p.get('original'):
            w('no sources listed (add them, or mark the note as original: true when it is your own method)')
        for s_ in p.get('sources', []):
            if not str(s_.get('url', '')).startswith('https://'):
                w(f'source "{s_.get("title", "?")}" needs an https URL')
        if len(p.get('faq') or []) < 2:
            w('add at least 2 FAQ entries')
        if 'TODO' in p['body'] or 'lorem' in p['body'].lower():
            w('placeholder text found in the body')
        for m in re.finditer(r'!\[([^\]]*)\]\(', p['body']):
            if not m.group(1).strip():
                w('an image in the body has no description (alt text)')
        if p.get('updated') and p['updated'] < p.get('date', ''):
            w('updated is earlier than date')
    return warns + lint_cases()


def lint_cases():
    # quality checks for case studies; returns a list of warnings
    warns = []
    for c in load_cases():
        if c.get('draft'):
            continue
        sl = c['slug']
        w = lambda m: warns.append(f'case {sl}: {m}')  # noqa: E731
        if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', sl):
            w('slug must be lowercase words joined by hyphens')
        if len(c.get('seo_title', '')) > 60:
            w(f'seo_title is {len(c["seo_title"])} characters, keep it at 60 or fewer')
        d = len(c.get('seo_description', ''))
        if not 70 <= d <= 160:
            w(f'seo_description is {d} characters, aim for 70 to 160')
        if len(c.get('card_title', '')) > 60:
            w('card_title is long, keep it under 60 characters')
        if not c.get('cover') or not (ROOT / c['cover'].lstrip('/')).exists():
            w('cover image is missing or the file does not exist')
        else:
            cw, ch = _og_size(c['cover'])
            if abs(cw / ch - 1.6) > 0.05:
                w(f'cover is {cw}x{ch}, use 16:10 (for example 1600x1000)')
        if not c.get('cover_alt'):
            w('cover_alt is missing')
        if not c.get('challenge'):
            w('challenge text is missing')
        if len(c.get('built') or []) < 3:
            w('add at least 3 "what we built" cards')
        if len(c.get('outcomes') or []) < 3:
            w('add 3 outcomes')
        if len(c.get('highlights') or c.get('card_kpis') or []) < 2:
            w('add at least 2 highlights')
        for n in c.get('services', []):
            if n not in SERVICES:
                w(f'unknown service "{n}": pick it from the list')
        if not c.get('services'):
            w('select the services behind this project')
    return warns


def feed_xml():
    posts = [p for p in load_posts() if not p.get('draft')]
    items = ''
    for p in posts[:30]:
        d = datetime.date.fromisoformat(p['date'])
        pub = d.strftime('%a, %d %b %Y 08:00:00 +0000')
        items += (f'  <item><title>{htmllib.escape(p["card_title"])}</title><link>https://fands.io{post_path(p)}</link>'
                  f'<guid isPermaLink="true">https://fands.io{post_path(p)}</guid><pubDate>{pub}</pubDate>'
                  f'<category>{htmllib.escape(p.get("category", "AI for small business"))}</category>'
                  f'<description>{htmllib.escape(p["card_summary"])}</description></item>\n')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>Fands Field Notes</title><link>https://fands.io/insights</link>'
            '<description>Practical notes on putting AI to work in a small or mid-size business.</description><language>en-us</language>\n' + items + '</channel></rss>\n')


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
