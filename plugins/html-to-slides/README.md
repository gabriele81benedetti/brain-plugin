# html-to-slides

Brain plugin that converts any HTML file or URL into an editable Google Slides presentation
using your company's branded template.

After installing, run `/html-to-slides` in Claude Code and provide a file path or URL.

## What it does

- Parses HTML semantically — extracts `<section>`, `<article>`, headings, paragraphs, lists, tables
- Each logical section → one content slide ("Titolo e testo" layout)
- First `<h1>` / document `<title>` → cover slide ("Copertina" layout)
- `<table>` elements → native, editable Google Slides tables
- Uses your company's branded template (same as `generate_slides.py`) — Poppins font, teal accents, logo, footer

Works best on HTML with clear semantic structure. Complex CSS visuals and charts are not replicated.

## Requirements

- 8020Brain installed and configured
- `data/html_to_slides.py` present (included in this plugin)
- Python venv at `brain/.venv/`
- Google Slides API credentials (`~/.google-slides-credentials.json`)
  → Run `/EnableGooglePresentation` if not yet configured

## Install

Download the latest release zip and extract it into your brain folder:

```bash
cd ~/Projects/brain   # replace with your brain path if different
unzip ~/Downloads/html-to-slides.zip
```

Or with curl:

```bash
curl -L https://github.com/gabriele81benedetti/brain-plugin/releases/latest/download/html-to-slides.zip \
  -o /tmp/hts.zip && unzip /tmp/hts.zip -d ~/Projects/brain/
```

Install the Python dependency:

```bash
source ~/Projects/brain/.venv/bin/activate && pip install beautifulsoup4
```

Then open Claude Code in your brain folder and run:

```
/html-to-slides
```

## Files installed

```
data/html_to_slides.py
.claude/commands/html-to-slides.md
.claude/skills/html-to-slides/SKILL.md
```

## Usage examples

```bash
# Convert a local audit report
python3 data/html_to_slides.py data/Report-GoogleAds/fiko.html

# Convert a URL with a custom title
python3 data/html_to_slides.py https://example.com/report.html --title "Q1 2025 Review"

# Save the output URL to a file
python3 data/html_to_slides.py report.html --out clients/acme/reports/slides-2025.txt
```
