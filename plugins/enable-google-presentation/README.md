# enable-google-presentation

Interactive setup wizard for Google Slides API integration in your 8020Brain.

After installing, run `/EnableGooglePresentation` in Claude Code to start the guided setup.

## What it does

Guides you step-by-step through:
1. **Prerequisites check** — verifies `generate_slides.py` and Python venv are in place
2. **Python dependencies** — installs `google-auth`, `google-auth-oauthlib`, `google-api-python-client`
3. **Google Cloud credentials** — walks through OAuth 2.0 setup with consent screen guidance
4. **Template URL** — connects your branded Google Slides template (or uses the Search On example)
5. **Audit workflow** — configures whether to ask each time or auto-generate after every audit
6. **Test run** — optional first run to verify everything works end to end

## Requirements

- 8020Brain installed and configured
- `data/generate_slides.py` present (included in brain v2026.02+)
- Python venv at `brain/.venv/`
- A Google account with access to Google Cloud Console

## Install

Download the latest release zip and extract it into your brain folder:

```bash
cd ~/Projects/brain   # replace with your brain path if different
unzip ~/Downloads/enable-google-presentation.zip
```

Or with curl (replace `<version>` with the latest release tag):

```bash
curl -L https://github.com/gabrielebn/brain-plugins/releases/download/<version>/enable-google-presentation.zip \
  -o /tmp/egp.zip && unzip /tmp/egp.zip -d ~/Projects/brain/
```

Then open Claude Code in your brain folder and run:

```
/EnableGooglePresentation
```

## Files installed

```
.claude/commands/enable-google-presentation.md
.claude/skills/enable-google-presentation/SKILL.md
```
