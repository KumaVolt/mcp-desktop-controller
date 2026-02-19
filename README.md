# Desktop Controller MCP Server

**Give any AI full control of your desktop.** Mouse, keyboard, screenshots — all through the [Model Context Protocol](https://modelcontextprotocol.io/).

One MCP server. Ten tools. Your AI can now see your screen and interact with any application, just like you do.

https://github.com/user-attachments/assets/placeholder

## What can it do?

- **See your screen** — Take full or partial screenshots, auto-optimized for LLM token usage
- **Move & click** — Navigate, click, double-click, right-click, drag and drop
- **Type anything** — Full keyboard control including Unicode, emoji, and key combos (Cmd+C, Ctrl+Shift+T, etc.)
- **Cross-platform** — Works on macOS, Windows, and Linux

## Tools

| Tool | What it does |
|------|-------------|
| `desktop_screenshot` | Capture the screen or a region (returns image directly to the LLM) |
| `desktop_get_screen_size` | Get screen dimensions in logical pixels |
| `desktop_get_mouse_position` | Get current cursor coordinates |
| `desktop_move_mouse` | Move cursor (absolute or relative) |
| `desktop_click` | Click, double-click, or right-click at any position |
| `desktop_scroll` | Scroll up or down |
| `desktop_drag` | Drag from one position to another |
| `desktop_type_text` | Type text with full Unicode support |
| `desktop_press_key` | Press special keys (Enter, Tab, arrows, F1-F12, etc.) |
| `desktop_hotkey` | Press key combinations (Cmd+C, Ctrl+V, Alt+F4, etc.) |

## Quick Start

### Install

```bash
git clone https://github.com/YOUR_USERNAME/mcp-desktop-controller.git
cd mcp-desktop-controller
pip install -e .
```

### Add to Claude Desktop

Add to your config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "desktop-controller": {
      "command": "mcp-desktop-controller"
    }
  }
}
```

<details>
<summary>Using a virtual environment? Use the full path instead.</summary>

```json
{
  "mcpServers": {
    "desktop-controller": {
      "command": "/path/to/venv/bin/mcp-desktop-controller"
    }
  }
}
```

</details>

### Add to Claude Code

```bash
claude mcp add desktop-controller -- mcp-desktop-controller
```

### macOS Permissions

On first run, you'll need to grant two permissions in **System Settings > Privacy & Security**:

1. **Accessibility** — so the server can control mouse and keyboard
2. **Screen Recording** — so it can take screenshots

## Safety

- **Failsafe** — Move your mouse to the top-left corner (0,0) to instantly abort any action
- **Action pause** — 0.1s delay between all actions to keep things predictable
- **Retina-aware** — All coordinates use logical resolution; screenshots are auto-downscaled to save tokens

## How it works

Built with [FastMCP](https://github.com/jlowin/fastmcp) and [PyAutoGUI](https://pyautogui.readthedocs.io/). The server exposes desktop control as MCP tools over stdio. Any MCP-compatible client (Claude Desktop, Claude Code, or your own) connects and gets full desktop access.

```
Your AI  ←→  MCP Client  ←→  Desktop Controller  ←→  Your Screen
```

## Platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| macOS | Full support | Uses `pbcopy` for Unicode input |
| Windows | Full support | Uses `clip` for Unicode input |
| Linux | Full support | Requires `xclip` (`sudo apt install xclip`) |

## Development

```bash
# Run directly
python server.py

# Test with MCP Inspector
fastmcp dev server.py
```

## License

MIT
