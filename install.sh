#!/bin/sh
# Installs Furius ISO Mount for the current user on Debian/Ubuntu.
set -e

if ! command -v apt-get >/dev/null 2>&1; then
    echo "This installer supports Debian/Ubuntu (apt-get) systems only." >&2
    exit 1
fi

SOURCE_DIR="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
INSTALL_DIR="$HOME/.local/share/furiusisomount"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

echo "==> Installing system dependencies (requires sudo)..."
sudo apt-get update
sudo apt-get install -y python3-gi gir1.2-gtk-3.0 fuseiso brasero nautilus policykit-1

echo "==> Copying application files to $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r "$SOURCE_DIR/src" "$SOURCE_DIR/res" "$SOURCE_DIR/pix" "$SOURCE_DIR/locale" "$SOURCE_DIR/doc" "$SOURCE_DIR/furiusisomount" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/furiusisomount"

echo "==> Linking launcher into $BIN_DIR..."
mkdir -p "$BIN_DIR"
ln -sf "$INSTALL_DIR/furiusisomount" "$BIN_DIR/furiusisomount"

echo "==> Installing desktop entry..."
mkdir -p "$DESKTOP_DIR"
sed "s|^Exec=furiusisomount|Exec=$BIN_DIR/furiusisomount|" "$SOURCE_DIR/app.desktop" > "$DESKTOP_DIR/furiusisomount.desktop"

case ":$PATH:" in
    *":$BIN_DIR:"*) ;;
    *) echo "NOTE: $BIN_DIR is not on your PATH. Add it to your shell profile or launch Furius ISO Mount from your application menu." ;;
esac

echo "==> Done. Launch it from your application menu, or run: $BIN_DIR/furiusisomount"
