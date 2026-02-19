---
name: enable-google-presentation
description: |
  Interactive setup wizard for Google Slides API integration.
  Guides users step-by-step through credentials, template, and audit workflow configuration.
  USE WHEN user runs /EnableGooglePresentation, asks to "set up google slides",
  "enable presentations", "configure slides API", or "set up Google Presentation".
---

# Enable Google Presentation — Setup Wizard

Guide the user through configuring automatic Google Presentation generation after audits.
This is a conversational, step-by-step wizard. Ask one thing at a time. Celebrate progress.

---

## Before Starting

Use `$CLAUDE_PROJECT_DIR` as the brain path (it's always set by Claude Code to the current project directory).

Check if credentials already exist:
```bash
test -f ~/.google-slides-credentials.json && echo "EXISTS" || echo "MISSING"
```

- If EXISTS → "It looks like you've already started this setup. Let's pick up where you left off."
- If MISSING → "Let's get you set up to generate Google Presentations automatically after every audit. This takes about 10 minutes."

---

## Step 1 — Prerequisites Check (automatic, no question)

Run silently and display a checklist:

```bash
# Check generate_slides.py
test -f "$CLAUDE_PROJECT_DIR/data/generate_slides.py" && echo "SLIDES_OK" || echo "SLIDES_MISSING"

# Check Python venv
test -f "$CLAUDE_PROJECT_DIR/.venv/bin/python" && echo "VENV_OK" || echo "VENV_MISSING"
```

Display result as a checklist:
```
Prerequisites:
✅ data/generate_slides.py found
✅ Python virtual environment found
```

If `generate_slides.py` is missing:
```
❌ data/generate_slides.py not found.
Your brain may need to be updated. Run /update to get the latest version, then try again.
```
Stop here if critical files are missing.

---

## Step 2 — Python Dependencies

Tell the user: "Installing required Python packages…"

Run:
```bash
source "$CLAUDE_PROJECT_DIR/.venv/bin/activate" && pip install -q google-auth google-auth-oauthlib google-api-python-client
```

On success: "Dependencies installed ✅"

On error: show the pip output and suggest checking the venv setup.

---

## Step 3 — Google Cloud Setup (guided, no code)

Tell the user:

> "Now let's set up your Google Cloud credentials. Follow these steps in your browser — I'll wait."

Show numbered instructions:
```
1. Go to https://console.cloud.google.com
2. Create a new project (or select an existing one)
3. Go to: APIs & Services → Library
4. Search "Google Slides API" → Enable it
5. Search "Google Drive API" → Enable it
6. Go to: APIs & Services → Credentials
7. Click "Create Credentials" → "OAuth 2.0 Client ID"
8. Application type: Desktop App → Name it anything (e.g. "Brain Slides")
9. Click Create → Download the JSON file
10. Save the file as: ~/.google-slides-credentials.json
11. Run in your terminal: chmod 600 ~/.google-slides-credentials.json

Note: If this is your first OAuth credential, you'll need to configure the
"OAuth consent screen" first. Set it to Internal (if using a Google Workspace
account) or External with your email as a test user.
```

Then **AskUserQuestion**:
- Question: "Have you saved the credentials file to ~/.google-slides-credentials.json?"
- Options:
  1. "Yes, done" → proceed to Step 4
  2. "I need help with the consent screen" → show expanded guidance below

**Expanded guidance (if "I need help"):**
```
OAuth Consent Screen setup:
1. APIs & Services → OAuth consent screen
2. User Type: External → Create
3. App name: "Brain Slides" (anything works)
4. Support email: your Gmail address
5. Developer contact: same email
6. Save and continue (skip Scopes)
7. Add Test Users → add your Gmail address
8. Save → go back to Credentials and create the OAuth 2.0 Client ID
```
After showing this, ask again: "Ready now?" → proceed.

---

## Step 4 — Template URL

Tell the user:

> "Now let's connect your Google Slides template — the presentation with your logo, fonts, and brand colors."

**AskUserQuestion:**
- Question: "What's the URL of your Google Slides template?"
- Options:
  1. "I have a URL" → user provides URL via "Other" input
  2. "Use the Search On example template" → use ID `1Cy0pGP-Cnp8x-hNcDdjjvZAo9ksuUxwTcSZOIdqTwxQ`
  3. "I'll set this up later" → skip, leave existing placeholder in script

**If user provides a URL:**
Extract the ID from the URL pattern `/d/<ID>/edit` or `/d/<ID>/`:
```
URL: https://docs.google.com/presentation/d/ABC123XYZ/edit
ID:  ABC123XYZ
```
Tell the user the extracted ID and confirm it looks right.

**If using example template or extracted ID:**
Update `data/generate_slides.py` line with `SLIDES_TEMPLATE_ID`:

Read the file and replace:
```python
SLIDES_TEMPLATE_ID = "1Cy0pGP-Cnp8x-hNcDdjjvZAo9ksuUxwTcSZOIdqTwxQ"
```
With:
```python
SLIDES_TEMPLATE_ID = "<new-id>"
```

**Layout check:**
After setting the template, explain:
```
Your template needs two specific layouts to work correctly:
- "Copertina"        → used for the cover slide
- "Titolo e testo"   → used for all content slides

To verify: open your template → View → Slide Master → check layout names in the left panel.
```

**AskUserQuestion:**
- Question: "Do the layout names in your template match 'Copertina' and 'Titolo e testo'?"
- Options:
  1. "Yes, they match" → proceed to Step 5
  2. "My layouts have different names" → ask for actual names, update script

**If layouts differ:**
Ask: "What are the exact names of your cover layout and content layout?"
(Use "Other" input for each name.)

Then in `data/generate_slides.py`, search for references to `"Copertina"` and `"Titolo e testo"` in the layout-selection logic and update them to match.

---

## Step 5 — Audit Workflow Integration

Tell the user:

> "Almost there! One last choice: how should Google Presentation fit into your audit workflow?"

**AskUserQuestion:**
- Question: "After running an audit, when should Google Presentation be generated?"
- Options:
  1. "Ask me each time (recommended)" → update audit SKILL.md with optional step
  2. "Always generate automatically" → update audit SKILL.md with mandatory step
  3. "Skip for now" → no changes to audit SKILL.md

**If "Ask me each time":**

Read `.claude/skills/google-ads-audit/SKILL.md` and append this block at the end
(before any trailing newline):

```markdown

---

### Generate Google Presentation (Optional)

After the HTML report is complete, ask the user:

**AskUserQuestion:**
- "Do you want to generate a Google Presentation for this client?"
- Options:
  1. "Yes – generate now"
  2. "No – HTML only"

If yes:
\```bash
source "$CLAUDE_PROJECT_DIR/.venv/bin/activate"
python3 "$CLAUDE_PROJECT_DIR/data/generate_slides.py" <client-alias> <year>
\```

The generated presentation URL is saved to:
`clients/<client>/reports/slides-<year>.txt`
```

**If "Always generate automatically":**

Append the same block but without the AskUserQuestion — make it a mandatory step that runs automatically after the HTML report.

---

## Step 6 — First Run Test (optional)

Tell the user: "Setup is complete! Want to do a quick test run to make sure everything works?"

**AskUserQuestion:**
- Question: "Run a test now?"
- Options:
  1. "Yes – test with a client" → ask for client alias and year, then run
  2. "No, I'll test later" → show manual command

**If yes:**
Ask: "Which client alias and year? (e.g. `mondoffice 2025`)"

Run:
```bash
source "$CLAUDE_PROJECT_DIR/.venv/bin/activate"
python3 "$CLAUDE_PROJECT_DIR/data/generate_slides.py" <alias> <year>
```

On first run, a browser window will open for Google OAuth authentication.
Tell the user: "A browser window will open — log in with the Google account that owns the template and has Drive access."

After success, find the generated URL:
```bash
cat "$CLAUDE_PROJECT_DIR/clients/<alias>/reports/slides-<year>.txt"
```
Display the URL and offer to open it.

**If no:**
Show:
```bash
# Manual test command (run from inside your brain folder):
source .venv/bin/activate
python3 data/generate_slides.py <client-alias> <year>
```

---

## Completion Message

```
✅ Google Presentation setup complete!

Here's what was configured:
- Python dependencies: google-auth, google-auth-oauthlib, google-api-python-client
- Credentials path: ~/.google-slides-credentials.json
- Token path: ~/.google-slides-token.json (auto-generated on first run)
- Template ID: [ID used]
- Layout names: Copertina / Titolo e testo [or custom names if changed]
- Audit workflow: [ask each time / generates automatically / manual only]

To generate a presentation manually at any time:
  python3 data/generate_slides.py <client-alias> <year>

Note: Make sure your Google account has edit access to the template presentation,
otherwise Drive will not be able to copy it.
```
