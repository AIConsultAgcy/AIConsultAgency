# Content guide for Field Notes (people and AI agents)

Every article is one JSON file in `content/insights/<slug>.json`. Copy `content/templates/insight.json` to start.
The site is rebuilt from these files (`python build.py`), which also creates the table of contents, the FAQ and
Article structured data, the sources list, related notes, the RSS feed (`/feed.xml`) and the sitemap entry.

## Rules an article must follow

1. **One idea, one reader problem.** Written for the owner of a small or mid-size US business. Plain English, no hype.
2. **Length:** 600 words or more. Open with the problem, not with "In today's world".
3. **Structure:** at least three `##` sections, `###` for sub-steps. The table of contents is built from the headings.
4. **Key takeaways:** 3 to 5 short points in `takeaways`.
5. **FAQ:** at least 2 real questions with direct 1 to 3 sentence answers.
6. **Sources:** every outside fact, study or figure needs a working `https://` link in `sources`, and ideally an inline link
   where it is mentioned. Never invent a statistic, a quote, a client result or a source. If a figure comes from a vendor or an
   old study, say so. For your own method or opinion set `"original": true`.
7. **No client claims.** Do not claim results for Fands clients unless they are published on a case study page.
8. **Internal links:** link to at least one service page or case study with a path such as `/services/ai-operations`.
9. **SEO fields:** `seo_title` up to 60 characters, `seo_description` 70 to 160 characters, `cover_alt` describing the image,
   `tags` (3 to 5), one `category`.
10. **Dates:** `date` is the publication date (YYYY-MM-DD). Set `updated` when you change an article later.
    Use `order` to rank notes that share a date (lower number = shown first).
11. **Slug:** lowercase words joined by hyphens, unique, never changed after publishing.

## Markdown supported in `body`

`## Heading`, `### Subheading`, `- list`, `1. list`, `| table | rows |`, `> **Title**` followed by `> text` for a note box,
`~ small print`, `![alt text](/img/uploads/file.jpg)` for an image (alt text is required), links `[text](url)`, `**bold**`, `*italic*`.

## Cover image

1600x1000, as JPG, PNG or SVG in `img/insights/<slug>.<ext>`. SVG covers in the Fands style are fine (dark background, orange
accent, the mark and a "FIELD GUIDE" label, an honest diagram that matches the article; mark illustrative charts as illustrative).

## Before publishing

```bash
FANDS_STRICT=1 python build.py   # stops with a list of problems if the article breaks the rules above
```

Then open a pull request. A person reads it, checks facts and sources, and merges. Agents must not publish straight to `main`.
Set `"draft": true` to keep an article out of the site while it is being written.

## Case studies

One JSON file per case in `content/cases/<slug>.json` (the CMS edits the same files). The page is built from fields, so there is no
free-form layout: cover (1600x1000, 16:10) with `cover_alt`, three `highlights`, a `challenge`, 3 to 6 `built` cards (icon, title, text),
an optional AI section (`ai_title`, `ai_text`, `ai_points`), three `outcomes`, and the `services` behind the project, chosen from the
exact service names on the site. Only publish facts the client has approved: no invented numbers, quotes or results. The Fands badge is
added to every cover automatically. `FANDS_STRICT=1 python build.py` checks all of this.
