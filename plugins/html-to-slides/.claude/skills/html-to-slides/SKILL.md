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

Convert any HTML file or URL into an editable Google Slides presentation using your
company's branded template. Preserves master slides, layouts, fonts, and design system.

---

## Triggers

This skill activates when the user:
- Says "convert html to slides" or "html to presentation"
- Asks to "turn this report into a presentation" or "make slides from html"
- Runs the `/html-to-slides` command
- Mentions converting HTML files or URLs to Google Slides
- Wants to transform HTML reports or documents into slide decks

---

## What It Does

- Parses HTML semantically: `<section>`, `<article>`, headings, paragraphs, lists, tables
- Each logical section → one content slide (configurable layout)
- First `<h1>` / `<title>` → cover slide (configurable layout)
- `<table>` elements → native editable Google Slides tables
- All text is editable in Google Slides — not screenshots
- Applies company template: Poppins font, teal accents, logo, footer

---

## Prerequisites Check

Before running, verify:

```bash
# Check script exists
test -f "$CLAUDE_PROJECT_DIR/.claude/skills/html-to-slides/html_to_slides.py" && echo "Script: OK" || echo "Script: MISSING"

# Check auth
test -f ~/.google-slides-credentials.json && echo "Auth: OK" || echo "Auth: MISSING"

# Check Python dependency
python3 -c "import bs4" 2>/dev/null && echo "bs4: OK" || echo "bs4: MISSING"
```

**If credentials are missing:**
→ Ask user to run `/enable-google-presentation` first for guided setup.

**If beautifulsoup4 is missing:**
→ Install with: `source "$CLAUDE_PROJECT_DIR/.venv/bin/activate" && pip install -q beautifulsoup4`

---

## Configuration

The script supports customization via command-line arguments:

### Layout Names (Customizable)

**Default layouts** (Italian):
- Cover slide: `"Copertina"`
- Content slide: `"Titolo e testo"`

These match the company template. If your template uses different layout names:

```bash
# Edit the script and modify lines 431, 442, 460:
# - Change "Copertina" to your cover layout name
# - Change "Titolo e testo" to your content layout name
```

**Alternative:** Use `--template` flag to specify a different template ID that has English layout names.

### Template ID

Default: `1Cy0pGP-Cnp8x-hNcDdjjvZAo9ksuUxwTcSZOIdqTwxQ` (company template)

To use a different template:
```bash
python3 html_to_slides.py source.html --template "YOUR_TEMPLATE_ID"
```

---

## Usage

**Step 1: Ask the user for the HTML source**

> "What's the HTML file path or URL you want to convert?"

Options to present:
1. **File path** (e.g., `data/Report-GoogleAds/fiko.html`)
2. **URL** (e.g., `https://example.com/report.html`)
3. **Client's latest audit report** → find path in `clients/<alias>/reports/`

**Step 2: Optional - ask for a custom title**

> "Do you want a custom presentation title, or should I use the one from the HTML?"

---

## Running the Script

```bash
cd "$CLAUDE_PROJECT_DIR"
source .venv/bin/activate
python3 .claude/skills/html-to-slides/html_to_slides.py <source> [options]
```

### Examples

```bash
# From file
python3 .claude/skills/html-to-slides/html_to_slides.py data/Report-GoogleAds/fiko.html

# From URL with custom title
python3 .claude/skills/html-to-slides/html_to_slides.py https://example.com/report.html --title "Q1 2025 Review"

# Save URL to client folder
python3 .claude/skills/html-to-slides/html_to_slides.py clients/mondoffice/reports/audit-2025.html \
  --out clients/mondoffice/reports/slides-html-2025.txt

# Use different template
python3 .claude/skills/html-to-slides/html_to_slides.py report.html --template "1AbC_DeF_GhI"
```

### Command-line Options

| Option | Description | Default |
|--------|-------------|---------|
| `source` | HTML file path or URL (required) | - |
| `--title "Title"` | Override presentation title | Extracted from HTML |
| `--out <path>` | Save presentation URL to file | None |
| `--template <id>` | Google Slides template ID | Company template |

---

## First Run OAuth Flow

On first run, a browser window will open for Google OAuth.

**Tell the user:**
> "A browser window will open — log in with the Google account that has access to the template."

The script will:
1. Save credentials to `~/.google-slides-token.json`
2. Reuse the token for future runs
3. Auto-refresh when expired

---

## After Running

The script outputs:
```
✅  Done! Total slides: 12
🔗  https://docs.google.com/presentation/d/[ID]/edit
```

**Actions:**
1. Display the presentation URL to the user
2. Offer to open it in browser (if on desktop)
3. If `--out` was used, show the saved file path:
   ```bash
   cat <out-path>
   ```

---

## Error Handling

### Network errors (URL sources)
```
❌  Failed to load URL: [error]
```
→ Check internet connection, verify URL is accessible

### Missing credentials
```
❌  Credentials not found at ~/.google-slides-credentials.json
Run /EnableGooglePresentation in Claude Code for guided setup.
```
→ Guide user through `/enable-google-presentation` skill

### Invalid HTML structure
- Script falls back to treating entire body as one section
- No crash on malformed HTML (BeautifulSoup handles gracefully)

### Template not found
```
❌  Template ID not accessible
```
→ Verify template ID, check Google account has access

### Empty sections
- Sections with no body text or tables are skipped
- Minimum: 1 cover slide always created

---

## Limitations

- **Complex CSS layouts** - Not replicated (only semantic structure)
- **Charts and images** - Not extracted (Google Slides API limitation for HTML)
- **Styled `<div>` visuals** - Converted to plain text
- **Long sections** - Truncated at ~900 characters per slide (keeps slides readable)
- **Large tables** - Capped at 20 rows per slide
- **Best with semantic HTML** - Works best on HTML with clear structure (headings, sections, tables)

---

## Resources

This skill bundles all required files:

| File | Purpose |
|------|---------|
| `html_to_slides.py` | Python script for HTML → Slides conversion |
| `SKILL.md` | This documentation |

**External dependencies:**
- Python package: `beautifulsoup4` (auto-installed on first run)
- Google APIs: Slides API + Drive API (enabled via `/enable-google-presentation`)

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'bs4'"
```bash
source "$CLAUDE_PROJECT_DIR/.venv/bin/activate"
pip install beautifulsoup4
```

### "Template layout 'Copertina' not found"
Your template uses different layout names. Edit `html_to_slides.py` lines 431, 442, 460 to match your template's layout names, or use a different `--template` ID.

### Slides are blank
- Check HTML has recognizable structure (`<h1>`, `<h2>`, `<section>`, `<p>`)
- Verify HTML is not heavily JavaScript-rendered (static HTML works best)

### Permission denied errors
```bash
chmod 600 ~/.google-slides-credentials.json
```
