# HTML to Slides Converter

**Version:** 1.0.1
**Grade:** A (85/100)
**Status:** Production-ready

Convert any HTML file or URL into an editable Google Slides presentation with your company's branded template.

---

## Features

✅ **Self-contained** - All files bundled, no external dependencies
✅ **Semantic parsing** - Extracts sections, headings, lists, and tables
✅ **Native Slides elements** - All text is editable (not screenshots)
✅ **Company branding** - Uses your template with logos, fonts, colors
✅ **Configurable** - Custom templates and layout names supported
✅ **Auto-activation** - Triggers on keywords like "convert html to slides"

---

## Installation

### Option 1: Copy to your brain

```bash
cp -r .claude/skills/html-to-slides ~/.claude/skills/
```

### Option 2: Clone from GitHub

```bash
cd ~/.claude/skills/
git clone <repo-url> html-to-slides
```

---

## Quick Start

### 1. Prerequisites

Run the setup wizard (one-time):
```
/enable-google-presentation
```

This will:
- Guide you through Google API credentials setup
- Configure your branded template
- Test the integration

### 2. Use the skill

In Claude Code, say:
- "Convert this HTML to slides"
- "Turn report.html into a presentation"
- "Make slides from https://example.com/report"

Or run directly:
```bash
/html-to-slides
```

---

## Configuration

### Layout Names

**Default (Italian):**
- Cover slide: `"Copertina"`
- Content slide: `"Titolo e testo"`

**For English Google Slides:**
Use command-line parameters:
```bash
python3 html_to_slides.py source.html \
  --cover-layout "Title Slide" \
  --content-layout "Title and Body"
```

**For other languages:**
Check your template's layout names in Google Slides ("Slide" → "Apply layout") and use the appropriate parameters.

### Template ID

**Default:** `1Cy0pGP-Cnp8x-hNcDdjjvZAo9ksuUxwTcSZOIdqTwxQ`

**To use your own template:**
```bash
python3 html_to_slides.py source.html --template "YOUR_TEMPLATE_ID"
```

---

## Usage Examples

### From local file
```bash
python3 .claude/skills/html-to-slides/html_to_slides.py data/report.html
```

### From URL with custom title
```bash
python3 .claude/skills/html-to-slides/html_to_slides.py \
  https://example.com/report.html \
  --title "Q1 2025 Review"
```

### Save URL to file
```bash
python3 .claude/skills/html-to-slides/html_to_slides.py report.html \
  --out clients/acme/slides-url.txt
```

### English Google Slides
```bash
python3 .claude/skills/html-to-slides/html_to_slides.py report.html \
  --cover-layout "Title Slide" \
  --content-layout "Title and Body"
```

---

## Command-line Options

| Option | Description | Default |
|--------|-------------|---------|
| `source` | HTML file path or URL (required) | - |
| `--title "Title"` | Override presentation title | From HTML |
| `--out <path>` | Save presentation URL to file | None |
| `--template <id>` | Google Slides template ID | Company template |
| `--cover-layout <name>` | Layout for cover slide | `"Copertina"` |
| `--content-layout <name>` | Layout for content slides | `"Titolo e testo"` |

---

## Requirements

- **Python 3.8+** with venv
- **beautifulsoup4** (auto-installed on first run)
- **Google Slides API** enabled (via `/enable-google-presentation`)
- **Google Drive API** enabled (via `/enable-google-presentation`)

---

## What Gets Converted

| HTML Element | Slides Output |
|--------------|---------------|
| `<h1>` or `<title>` | Cover slide |
| `<section>` / `<article>` | One slide per section |
| `<h2>`, `<h3>` | Slide titles |
| `<p>`, `<div>` | Text content |
| `<ul>`, `<ol>`, `<li>` | Bullet lists |
| `<table>` | Native editable tables |

### Not Supported
- Complex CSS layouts
- JavaScript-rendered content
- Charts and images (API limitation)
- Heavily styled `<div>` visuals

---

## Limitations

- **Long sections** - Truncated at ~900 characters per slide
- **Large tables** - Capped at 20 rows per slide
- **Best with semantic HTML** - Works best with clear structure

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'bs4'"
```bash
source .venv/bin/activate
pip install beautifulsoup4
```

### "Template layout 'Copertina' not found"
Your Google Slides is in English. Use layout parameters:
```bash
python3 html_to_slides.py source.html \
  --cover-layout "Title Slide" \
  --content-layout "Title and Body"
```

### "Permission denied"
```bash
chmod 600 ~/.google-slides-credentials.json
```

### Blank slides
- Verify HTML has recognizable structure (`<h1>`, `<h2>`, `<section>`, `<p>`)
- Static HTML works best (not JavaScript-heavy SPAs)

---

## Quality Score

**Skill Auditor Results:**

| Category | Score | Max |
|----------|-------|-----|
| Structure | 20 | 20 |
| Triggers | 13 | 15 |
| Process | 16 | 20 |
| Self-contained | 14 | 20 |
| Scripts | 15 | 15 |
| Documentation | 7 | 10 |
| **Total** | **85** | **100** |

**Grade:** A
**Pass:** ✅ YES

---

## Changelog

### v1.0.1 (2026-02-23)
- 🌍 **CLI layout parameters** - `--cover-layout` and `--content-layout` for multi-language support
- 🎯 **Bundled Python script** - Now self-contained
- 📝 **Enhanced documentation** - Triggers, error handling, config
- 🌐 **Universal portability** - Works with English, Italian, and other languages
- ✅ **Grade A** - Improved from 82/100 (B) to 85/100 (A)

### v1.0.0 (2026-02-01)
- Initial release

---

## License

MIT License - Use freely, modify as needed

---

## Support

For issues or questions:
1. Check [SKILL.md](SKILL.md) for detailed documentation
2. Run `/enable-google-presentation` to verify setup
3. Test with a simple HTML file first

---

## Credits

**Created by:** Gabriele Benedetti
**Based on:** 8020Brain Template
**Reviewed by:** Mike Rhodes (Skill Auditor)

**Powered by:**
- Google Slides API
- BeautifulSoup4
- Claude Code

---

**Ready to use? Try:** `/html-to-slides` 🚀
