#!/usr/bin/env bash
# Install 늑구 (Neukgu) theme for Clawd on Desk on macOS/Linux.

set -euo pipefail

case "$(uname)" in
  Darwin) USER_DATA="$HOME/Library/Application Support/clawd-on-desk" ;;
  Linux)  USER_DATA="$HOME/.config/clawd-on-desk" ;;
  *) echo "ERROR: unsupported OS $(uname). Use install.ps1 on Windows." >&2; exit 1 ;;
esac

if [ ! -d "$USER_DATA" ]; then
  echo "ERROR: Clawd userData not found at $USER_DATA" >&2
  echo "Is Clawd on Desk installed? https://github.com/rullerzhou-afk/clawd-on-desk" >&2
  exit 1
fi

THEME_DIR="$USER_DATA/themes/neukgu"
CACHE_DIR="$USER_DATA/theme-cache/neukgu/assets"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing 늑구 (Neukgu) theme..."
echo "  source: $SCRIPT_DIR"
echo "  target: $THEME_DIR"
echo

# 1. Theme files -> userData/themes/neukgu/
mkdir -p "$THEME_DIR/assets"
cp "$SCRIPT_DIR/theme.json" "$THEME_DIR/"
cp "$SCRIPT_DIR/assets/"* "$THEME_DIR/assets/"
echo "  [1/2] theme + assets copied"

# 2. Workaround: copy PNG also to theme-cache so SVG's relative href resolves
#    (Clawd's external-theme loader caches SVGs but leaves non-SVG in source dir,
#    breaking <image href="idle-eyeless.png"> in idle-follow.svg)
mkdir -p "$CACHE_DIR"
cp "$SCRIPT_DIR/assets/idle-eyeless.png" "$CACHE_DIR/"
rm -f "$CACHE_DIR/idle-follow.svg"
echo "  [2/2] cache workaround applied"

echo
echo "Installed!"
echo
echo "Next steps:"
echo "  1. Restart Clawd on Desk (quit from tray then relaunch)"
echo "  2. Right-click pet -> Theme -> 늑구 (Neukgu)"
