# brain-plugins

Community plugins for [8020Brain](https://github.com/8020brain/brain) — skills and commands
you can drop into your brain with a single zip extract.

## Available plugins

| Plugin | Description |
|--------|-------------|
| [enable-google-presentation](plugins/enable-google-presentation/) | Set up Google Slides API for automatic presentation generation after audits |
| [html-to-slides](plugins/html-to-slides/) | Convert any HTML file or URL into an editable Google Slides presentation |
| [threshold-recommender](plugins/threshold-recommender/) | Interactive Shopping product bucketing report with ROAS/CPA sliders and spend-based thresholds |

## How to install a plugin

1. Download the plugin zip from [Releases](../../releases)
2. Extract into your brain folder:

```bash
cd ~/Projects/brain   # replace with your brain path
unzip ~/Downloads/<plugin-name>.zip
```

3. Reload Claude Code — the new command and skill are immediately available.

## How plugins work

Each plugin is a self-contained folder with the same structure as the brain's `.claude/` directory.
The zip contains only `.claude/commands/` and `.claude/skills/` files — no overwrites to existing brain files.

## Contributing

To add a plugin, open a PR with:
- `plugins/<plugin-name>/.claude/commands/<name>.md`
- `plugins/<plugin-name>/.claude/skills/<name>/SKILL.md`
- `plugins/<plugin-name>/README.md`
