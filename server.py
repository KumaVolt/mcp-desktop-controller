"""MCP server for desktop control: mouse, keyboard, screenshots, and screen info."""

import io
import platform
import subprocess
import sys
from typing import Optional

import pyautogui
from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from pydantic import Field

# PyAutoGUI safety config
pyautogui.FAILSAFE = True  # Move mouse to top-left corner to abort
pyautogui.PAUSE = 0.1  # Small pause between actions

mcp = FastMCP(
    "Desktop Controller",
    instructions="Full desktop control: mouse, keyboard, screenshots, and screen info",
)


# ---------------------------------------------------------------------------
# macOS permission checks
# ---------------------------------------------------------------------------


def _check_macos_permissions() -> None:
    """Check and request macOS Accessibility and Screen Recording permissions.

    Triggers the system permission prompt if not already granted.
    Opens System Settings to the right pane for any missing permission.
    """
    if platform.system() != "Darwin":
        return

    import ctypes
    import ctypes.util

    # --- Accessibility check ---
    # AXIsProcessTrusted checks without prompting
    app_services = ctypes.cdll.LoadLibrary(
        ctypes.util.find_library("ApplicationServices")
    )
    app_services.AXIsProcessTrusted.restype = ctypes.c_bool
    if not app_services.AXIsProcessTrusted():
        print(
            "Accessibility permission required.\n"
            "Opening System Settings — please grant access, then restart.",
            file=sys.stderr,
        )
        subprocess.Popen([
            "open",
            "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility",
        ])

    # --- Screen Recording check ---
    # NOTE: We skip the CGWindowListCreateImage probe on macOS 15+ because
    # calling it can *itself* trigger the system permission dialog on every
    # launch.  Instead, we just print a hint.  If permission is actually
    # missing the screenshot tool will fail with a clear error at call time.
    print(
        "Tip: If screenshots fail, grant Screen Recording permission in\n"
        "System Settings → Privacy & Security → Screen & System Audio Recording,\n"
        "then restart.",
        file=sys.stderr,
    )


# ---------------------------------------------------------------------------
# Screen info tools
# ---------------------------------------------------------------------------


@mcp.tool()
def desktop_get_screen_size() -> str:
    """Get the screen dimensions in pixels.

    Returns logical resolution (not physical pixels on Retina/HiDPI displays).
    All coordinate-based tools use this same logical coordinate space.
    """
    width, height = pyautogui.size()
    return f"Screen size: {width}x{height}"


@mcp.tool()
def desktop_get_mouse_position() -> str:
    """Get the current mouse cursor position.

    Returns coordinates in the logical screen coordinate space.
    """
    x, y = pyautogui.position()
    return f"Mouse position: x={x}, y={y}"


# ---------------------------------------------------------------------------
# Mouse tools
# ---------------------------------------------------------------------------


@mcp.tool()
def desktop_move_mouse(
    x: int = Field(description="Target X coordinate"),
    y: int = Field(description="Target Y coordinate"),
    relative: bool = Field(
        default=False,
        description="If True, move relative to current position instead of absolute",
    ),
    duration: float = Field(
        default=0.25,
        ge=0.0,
        description="Duration of the movement in seconds (0 = instant)",
    ),
) -> str:
    """Move the mouse cursor to a position.

    Coordinates are in logical screen space. Use desktop_get_screen_size to
    find the bounds. The image coordinates from desktop_screenshot map 1:1
    to screen coordinates (when reduce_resolution is True on Retina displays).
    """
    if relative:
        pyautogui.moveRel(x, y, duration=duration)
    else:
        pyautogui.moveTo(x, y, duration=duration)
    actual_x, actual_y = pyautogui.position()
    return f"Moved mouse to ({actual_x}, {actual_y})"


@mcp.tool()
def desktop_click(
    x: Optional[int] = Field(
        default=None, description="X coordinate to click (None = current position)"
    ),
    y: Optional[int] = Field(
        default=None, description="Y coordinate to click (None = current position)"
    ),
    button: str = Field(
        default="left", description="Mouse button: 'left', 'middle', or 'right'"
    ),
    clicks: int = Field(default=1, ge=1, description="Number of clicks (2 = double-click)"),
) -> str:
    """Click the mouse at a position.

    If x/y are omitted, clicks at the current cursor position.
    """
    pyautogui.click(x=x, y=y, button=button, clicks=clicks)
    cx, cy = pyautogui.position()
    click_type = "Double-clicked" if clicks == 2 else "Clicked"
    return f"{click_type} {button} button at ({cx}, {cy})"


@mcp.tool()
def desktop_scroll(
    clicks: int = Field(
        description="Number of scroll 'clicks'. Positive = up, negative = down"
    ),
    x: Optional[int] = Field(
        default=None, description="X coordinate to scroll at (None = current position)"
    ),
    y: Optional[int] = Field(
        default=None, description="Y coordinate to scroll at (None = current position)"
    ),
) -> str:
    """Scroll the mouse wheel at a position.

    If x/y are omitted, scrolls at the current cursor position.
    """
    pyautogui.scroll(clicks, x=x, y=y)
    direction = "up" if clicks > 0 else "down"
    pos_str = f"({x}, {y})" if x is not None and y is not None else "current position"
    return f"Scrolled {direction} {abs(clicks)} clicks at {pos_str}"


@mcp.tool()
def desktop_drag(
    start_x: int = Field(description="Starting X coordinate"),
    start_y: int = Field(description="Starting Y coordinate"),
    end_x: int = Field(description="Ending X coordinate"),
    end_y: int = Field(description="Ending Y coordinate"),
    duration: float = Field(
        default=0.5,
        ge=0.1,
        description="Duration of drag in seconds (minimum 0.1s; instant drags fail on macOS)",
    ),
    button: str = Field(default="left", description="Mouse button to hold during drag"),
) -> str:
    """Drag the mouse from one position to another.

    Moves to start position, holds the button, moves to end position, releases.
    Duration must be >= 0.1s because instant drags fail on macOS.
    """
    pyautogui.moveTo(start_x, start_y, duration=0.1)
    pyautogui.drag(
        end_x - start_x,
        end_y - start_y,
        duration=duration,
        button=button,
    )
    return f"Dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"


# ---------------------------------------------------------------------------
# Keyboard tools
# ---------------------------------------------------------------------------


def _type_via_clipboard(text: str) -> None:
    """Type text by copying to clipboard and pasting. Works with Unicode."""
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
        pyautogui.hotkey("command", "v")
    elif system == "Linux":
        subprocess.run(
            ["xclip", "-selection", "clipboard"],
            input=text.encode("utf-8"),
            check=True,
        )
        pyautogui.hotkey("ctrl", "v")
    elif system == "Windows":
        subprocess.run(["clip"], input=text.encode("utf-16-le"), check=True)
        pyautogui.hotkey("ctrl", "v")
    else:
        raise RuntimeError(f"Unsupported platform for clipboard paste: {system}")


@mcp.tool()
def desktop_type_text(
    text: str = Field(description="Text to type"),
    interval: float = Field(
        default=0.02,
        ge=0.0,
        description="Seconds between each keystroke",
    ),
) -> str:
    """Type a text string using the keyboard.

    For ASCII text, types character by character. For text containing non-ASCII
    characters (Unicode, emoji, accented letters), falls back to clipboard paste.
    """
    if text.isascii():
        pyautogui.write(text, interval=interval)
    else:
        _type_via_clipboard(text)
    return f"Typed {len(text)} characters"


@mcp.tool()
def desktop_press_key(
    key: str = Field(
        description=(
            "Key to press. Examples: 'enter', 'tab', 'escape', 'space', 'backspace', "
            "'delete', 'up', 'down', 'left', 'right', 'home', 'end', 'pageup', "
            "'pagedown', 'f1'-'f12', 'a'-'z', '0'-'9'"
        )
    ),
    presses: int = Field(default=1, ge=1, description="Number of times to press the key"),
) -> str:
    """Press a keyboard key one or more times.

    Use this for special keys (Enter, Tab, arrows, function keys, etc.).
    For typing regular text, use desktop_type_text instead.
    """
    pyautogui.press(key, presses=presses)
    times_str = f" {presses} times" if presses > 1 else ""
    return f"Pressed '{key}'{times_str}"


@mcp.tool()
def desktop_hotkey(
    keys: list[str] = Field(
        description=(
            "Keys to press simultaneously. Examples: ['command', 'c'] for Cmd+C, "
            "['ctrl', 'shift', 't'] for Ctrl+Shift+T, ['alt', 'f4'] for Alt+F4"
        )
    ),
) -> str:
    """Press a keyboard shortcut (key combination).

    On macOS, use 'command' for Cmd key. On Windows/Linux, use 'ctrl'.
    Keys are pressed in order and released in reverse order.
    """
    pyautogui.hotkey(*keys)
    combo = "+".join(keys)
    return f"Pressed hotkey: {combo}"


# ---------------------------------------------------------------------------
# Screenshot tool
# ---------------------------------------------------------------------------


@mcp.tool()
def desktop_screenshot(
    region_x: Optional[int] = Field(
        default=None, description="X coordinate of the top-left corner of capture region"
    ),
    region_y: Optional[int] = Field(
        default=None, description="Y coordinate of the top-left corner of capture region"
    ),
    region_width: Optional[int] = Field(
        default=None, description="Width of the capture region in pixels"
    ),
    region_height: Optional[int] = Field(
        default=None, description="Height of the capture region in pixels"
    ),
    reduce_resolution: bool = Field(
        default=True,
        description=(
            "Halve the screenshot dimensions to save tokens. Recommended for "
            "Retina/HiDPI displays. Set to False for pixel-perfect captures."
        ),
    ),
) -> Image:
    """Take a screenshot of the screen or a region.

    Returns the image directly so the LLM can see it. By default, resolution
    is halved to reduce token usage (Retina screens produce very large images).
    The returned image pixel coordinates map 1:1 to the logical screen
    coordinates used by all other tools (move, click, etc.).
    """
    region = None
    if all(v is not None for v in [region_x, region_y, region_width, region_height]):
        region = (region_x, region_y, region_width, region_height)

    screenshot = pyautogui.screenshot(region=region)

    if reduce_resolution:
        new_size = (screenshot.width // 2, screenshot.height // 2)
        screenshot = screenshot.resize(new_size)

    buffer = io.BytesIO()
    screenshot.save(buffer, format="PNG")
    return Image(data=buffer.getvalue(), format="png")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    _check_macos_permissions()
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
