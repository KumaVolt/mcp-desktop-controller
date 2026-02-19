# Desktop Controller MCP Server

An MCP server that gives LLMs full desktop control: mouse, keyboard, screenshots, and screen info. Built with [FastMCP](https://github.com/jlowin/fastmcp) and [PyAutoGUI](https://pyautogui.readthedocs.io/).

## Tools

| Tool | Description |
|------|-------------|
| `desktop_get_screen_size` | Get screen dimensions |
| `desktop_get_mouse_position` | Get current cursor position |
| `desktop_move_mouse` | Move cursor to absolute or relative position |
| `desktop_click` | Click at a position (single, double, right-click) |
| `desktop_scroll` | Scroll the mouse wheel |
| `desktop_drag` | Drag from one position to another |
| `desktop_type_text` | Type a text string (supports Unicode via clipboard fallback) |
| `desktop_press_key` | Press special keys (Enter, Tab, arrows, etc.) |
| `desktop_hotkey` | Press key combinations (Cmd+C, Ctrl+Shift+T, etc.) |
| `desktop_screenshot` | Capture the screen or a region (returns image to LLM) |

## Setup

### Install

```bash
cd mcp-desktop-controller
pip install -e .
```

### macOS Permissions

PyAutoGUI requires two permissions on macOS:

1. **Accessibility**: System Settings > Privacy & Security > Accessibility — add your terminal app (Terminal, iTerm2, VS Code, etc.)
2. **Screen Recording**: System Settings > Privacy & Security > Screen Recording — add your terminal app (required for screenshots)

You'll be prompted to grant these on first use.

### Claude Desktop Configuration

Add this to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "desktop-controller": {
      "command": "mcp-desktop-controller"
    }
  }
}
```

If you installed with `pip install -e .` in a virtual environment, use the full path:

```json
{
  "mcpServers": {
    "desktop-controller": {
      "command": "/path/to/venv/bin/mcp-desktop-controller"
    }
  }
}
```

## Usage

### Run directly

```bash
python server.py
```

### Test with MCP Inspector

```bash
fastmcp dev server.py
```

### Safety

- **Failsafe**: Move mouse to top-left corner (0,0) to abort any running action
- **Pause**: 0.1s pause between all PyAutoGUI actions
- All coordinates use **logical resolution** (not physical pixels on Retina/HiDPI)
- Screenshots are **halved by default** to save tokens (`reduce_resolution=True`)

## Platform Support

- **macOS**: Full support. Uses `pbcopy` for Unicode text input.
- **Windows**: Full support. Uses `clip` for Unicode text input.
- **Linux**: Full support. Requires `xclip` for Unicode text input (`sudo apt install xclip`).
