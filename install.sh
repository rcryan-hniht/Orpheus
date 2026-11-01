#!/usr/bin/env bash
set -e

# Orpheus installer script
# Run via: curl -fsSL https://raw.githubusercontent.com/rcryan-hniht/Orpheus/main/install.sh | bash

REPO_URL="https://github.com/rcryan-hniht/Orpheus.git"
INSTALL_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/orpheus/app"
VENV_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/orpheus/venv"
BIN_DIR="${HOME}/.local/bin"

echo "🎵 Installing Orpheus..."

# 1. Verify python3 availability and version (>= 3.11)
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Error: python3 is required but not installed." >&2
    echo "   Please install Python 3.11 or later and rerun this script." >&2
    exit 1
fi

python3 -c '
import sys
if sys.version_info < (3, 11):
    sys.exit(1)
' 2>/dev/null || {
    echo "❌ Error: Python 3.11+ is required (found $(python3 --version 2>&1))." >&2
    exit 1
}

# 2. Check mpv player
if ! command -v mpv >/dev/null 2>&1; then
    echo "⚠️  Warning: 'mpv' was not found in PATH."
    echo "   Orpheus requires mpv to play audio."
    echo "   Install it with:"
    echo "     - Ubuntu/Debian: sudo apt install mpv"
    echo "     - Fedora:        sudo dnf install mpv"
    echo "     - Arch Linux:    sudo pacman -S mpv"
    echo "     - macOS:         brew install mpv"
    echo ""
fi

# 3. Check git
if ! command -v git >/dev/null 2>&1; then
    echo "❌ Error: git is required to download Orpheus." >&2
    exit 1
fi

# 4. Clone or update repository
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
if [ -f "$SCRIPT_DIR/pyproject.toml" ] && grep -q 'name = "orpheus"' "$SCRIPT_DIR/pyproject.toml" 2>/dev/null; then
    echo "📂 Installing directly from local directory: $SCRIPT_DIR"
    SOURCE_PATH="$SCRIPT_DIR"
else
    mkdir -p "$(dirname "$INSTALL_DIR")"
    if [ -d "$INSTALL_DIR/.git" ]; then
        echo "🔄 Updating existing Orpheus repository in $INSTALL_DIR..."
        git -C "$INSTALL_DIR" fetch --depth=1 origin main
        git -C "$INSTALL_DIR" reset --hard origin/main
    else
        if [ -d "$INSTALL_DIR" ]; then
            rm -rf "$INSTALL_DIR"
        fi
        echo "📦 Cloning Orpheus repository to $INSTALL_DIR..."
        git clone --depth=1 "$REPO_URL" "$INSTALL_DIR"
    fi
    SOURCE_PATH="$INSTALL_DIR"
fi

# 5. Create or refresh virtual environment
echo "⚙️  Setting up virtual environment in $VENV_DIR..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install "$SOURCE_PATH" --quiet

# 6. Create binary link in ~/.local/bin/orpheus
mkdir -p "$BIN_DIR"
ln -sf "$VENV_DIR/bin/orpheus" "$BIN_DIR/orpheus"

echo ""
echo "✨ Installation successful!"
echo "🚀 You can now start the player by running:"
echo "   orpheus"
echo ""

if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "ℹ️  Note: $BIN_DIR is not currently in your PATH."
    echo "   Add it to your current shell session:"
    echo "     export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo "   Or add that export line to your ~/.bashrc or ~/.zshrc."
    echo ""
fi
