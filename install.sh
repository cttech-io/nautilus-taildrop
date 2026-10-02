#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if ! compgen -G "/usr/lib*/nautilus/extensions-4/libnautilus-python.so" >/dev/null &&
   ! compgen -G "/usr/lib/*/nautilus/extensions-4/libnautilus-python.so" >/dev/null; then
    echo "nautilus-python is required (Fedora: sudo dnf install nautilus-python," >&2
    echo "Debian/Ubuntu: sudo apt install python3-nautilus)" >&2
fi

install -Dm755 taildrop-send "$HOME/.local/bin/taildrop-send"
install -Dm644 taildrop.py "$HOME/.local/share/nautilus-python/extensions/taildrop.py"

if ! tailscale file cp --targets >/dev/null 2>&1; then
    echo "Your user can't use Taildrop yet. Run: sudo tailscale set --operator=\$USER" >&2
fi

# Nautilus only loads extensions at startup
nautilus -q 2>/dev/null || true
echo "Installed. Open Files and right-click a file -> Send with Taildrop."
