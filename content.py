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


def case_card(c):
    feature = ' feature' if c.get('feature') else ''
    kpis = ''.join(f'<div><strong>{esc(k["value"])}</strong><span>{esc(k["label"])}</span></div>' for k in c.get('card_kpis', []))
    cover = f'<span class="case-cover"><img src="{c["cover"]}" alt="" width="1600" height="1000" loading="lazy" decoding="async"></span>' if c.get('cover') else ''
    return (f'<a class="case-card{feature}" href="{case_path(c)}">{cover}<div class="tags"><span class="tag">{esc(c["tag_industry"])}</span>'
            f'<span class="tag outline">{esc(c["tag_practice"])}</span></div><h3>{esc(c["card_title"])}</h3><p>{esc(c["card_summary"])}</p>'
            f'<div class="kpis">{kpis}</div><b>Read the case {{{{i:right:15}}}}</b></a>')


def case_cards_html():
    return '\n      '.join(case_card(c) for c in load_cases() if not c.get('draft'))


def case_page(c):
    url = 'https://fands.io' + case_path(c)
    crumbs = [['Case studies', '/case-studies'], [c['crumb'], case_path(c)]]
    meta = {'out': f'case-studies/{c["slug"]}.html', 'path': case_path(c), 'title': c['seo_title'], 'description': c['seo_description'],
            'crumbs': crumbs, 'priority': 0.6, 'type': 'WebPage', 'og_type': 'article'}
    facts = ''.join(f'<div><dt>{esc(f["label"])}</dt><dd>{esc(f["value"])}</dd></div>' for f in c.get('facts', []))
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": c.get('schema_headline', c['card_title']),
          "description": c.get('schema_description', c['seo_description']), "author": {"@id": "https://fands.io/#org"},
          "publisher": {"@id": "https://fands.io/#org"}, "mainEntityOfPage": url, "image": "https://fands.io/brand/og-v2.png"}
    body = f'''<main id="main">
  <section class="page-head">
    {{{{crumbs}}}}
    <p class="eyebrow">{esc(c['eyebrow'])}</p>
    <h1>{_lines(c['headline_main'], c.get('headline_em'))}</h1>
    <p class="lead">{esc(c['lead'])}</p>
    <dl class="facts">{facts}</dl>
  </section>

  {cover_figure(c)}<article class="article">
    {md_to_html(c['body'], 'kpi-table')}
  </article>

  {{{{closing}}}}
  <script type="application/ld+json">{json.dumps(ld, separators=(',', ':'), ensure_ascii=False)}</script>
</main>
'''
    return meta, body


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
