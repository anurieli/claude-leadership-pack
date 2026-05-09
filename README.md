# Claude Leadership Pack — Marketplace

A Claude Code plugin marketplace by Ariel Nurieli. Each plugin below is a focused bundle of skills you can install independently.

## Plugins

| Plugin | What's inside | Install |
|---|---|---|
| **leadership-pack** | Project management, internal comms, skill creation, Linear sync | `/plugin install leadership-pack@claude-leadership-pack` |
| **content-pack** | Reel extraction, podcast guides, marketing videos, repo launches | `/plugin install content-pack@claude-leadership-pack` |

## Add this marketplace once

```
/plugin marketplace add anurieli/claude-leadership-pack
```

Then install whichever plugin you need.

## Updating

When new versions ship, run `/plugin update <name>@claude-leadership-pack` or `/reload-plugins` to refresh.

## Plugin documentation

Each plugin has its own README with skill-by-skill detail and setup instructions:

- [leadership-pack](./leadership-pack/README.md)
- [content-pack](./content-pack/README.md)

## Legacy install (script)

The repo also supports symlink-based install if you prefer not to use the plugin system:

```bash
git clone https://github.com/anurieli/claude-leadership-pack.git ~/claude-leadership-pack
cd ~/claude-leadership-pack && ./install.sh
```

This installs only the `leadership-pack` skills. For `content-pack` and any future packs, use the plugin system above.
