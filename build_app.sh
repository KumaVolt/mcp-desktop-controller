#!/bin/bash
set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
source "$DIR/.venv/bin/activate"

echo "Building DesktopController..."
pyinstaller --onedir --name DesktopController \
  --copy-metadata fastmcp \
  --copy-metadata mcp \
  --copy-metadata pydantic \
  --collect-submodules rich._unicode_data \
  --collect-all lupa \
  --collect-all fakeredis \
  --collect-all docket \
  server.py

# Sign the executable before placing it in the bundle
codesign --force --sign - "$DIR/dist/DesktopController/DesktopController"

# Copy the onedir bundle into the app
rm -rf "$DIR/DesktopController.app/Contents/MacOS"
rm -rf "$DIR/DesktopController.app/Contents/Frameworks"
mkdir -p "$DIR/DesktopController.app/Contents/MacOS"
cp -R "$DIR/dist/DesktopController/"* "$DIR/DesktopController.app/Contents/MacOS/"

# PyInstaller bootloader looks in Contents/Frameworks/ when inside a .app bundle
ln -s "$DIR/DesktopController.app/Contents/MacOS/_internal" \
      "$DIR/DesktopController.app/Contents/Frameworks"

echo "Done! App bundle: $DIR/DesktopController.app"
