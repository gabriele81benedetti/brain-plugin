---
name: html-to-slides
description: |
  Convert any HTML file or URL into an editable Google Slides presentation.
  Uses the company branded template. Extracts sections, text, lists, and tables
  as native editable Slides elements.
  USE WHEN user says "convert html to slides", "html to presentation",
  "turn this report into a presentation", "make slides from html", or runs /html-to-slides.
---

# HTML to Slides Converter

Convert any HTML file or URL into an editable Google Slides presentation using the
company's branded template (same master/layouts as `generate_slides.py`).

---

## What It Does

- Parses HTML semantically: `<section>`, `<article>`, headings, paragraphs, lists, tables
- Each logical section → one content slide (layout: "Titolo e testo")
- First `<h1>` / `<title>` → cover slide (layout: "Copertina")
- `<table>` elements → native editable Google Slides tables
- All text is editable in Google Slides — not screenshots
- Applies company template: Poppins font, teal accents, logo, footer

---

## Before Running

Check that prerequisites are in place:

```bash
test -f "$CLAUDE_PROJECT_DIR/data/html_to_slides.py" && echo "OK" || echo "MISSING"
test -f ~/.google-slides-credentials.json && echo "AUTH OK" || echo "AUTH MISSING"
```

If credentials are missing → ask user to run `/EnableGooglePresentation` first.

---

## Usage

**Ask the user for the HTML source:**

> "What's the HTML file path or URL you want to convert?"

Options to present:
1. File path (e.g. `data/Report-GoogleAds/fiko.html`)
2. URL (e.g. `https://example.com/report.html`)
3. A client's latest audit report → find path in `clients/<alias>/reports/`

**Optional: ask for a custom title**

> "Do you want a custom presentation title, or should I use the one from the HTML?"

---

## Run

```bash
source "$CLAUDE_PROJECT_DIR/.venv/bin/activate"
python3 "$CLAUDE_PROJECT_DIR/data/html_to_slides.py" <source> [--title "Title"] [--out <path>]
```

**Examples:**

```bash
# From file
python3 data/html_to_slides.py data/Report-GoogleAds/fiko.html

# From URL with custom title
python3 data/html_to_slides.py https://example.com/report.html --title "Q1 2025 Review"

# Save URL to client folder
python3 data/html_to_slides.py clients/mondoffice/reports/audit-2025.html \
  --out clients/mondoffice/reports/slides-html-2025.txt
```

On first run a browser window will open for Google OAuth.
Tell the user: "A browser window will open — log in with the Google account that has access to the template."

---

## After Running

Display the presentation URL and offer to open it.

---

## Install Dependency

If `beautifulsoup4` is not installed:

```bash
source "$CLAUDE_PROJECT_DIR/.venv/bin/activate" && pip install -q beautifulsoup4
```

---

## Limitations

- Complex CSS layouts, charts, and styled `<div>` visuals are not replicated
- Long sections are truncated at ~900 characters (slide stays readable)
- Tables are capped at 20 rows per slide
- Works best on HTML with clear semantic structure (headings, sections, tables)
