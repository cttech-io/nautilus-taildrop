# Nautilus extension: right-click -> "Send with Taildrop" -> <device>
import os
import subprocess

import gi
try:
    gi.require_version("Nautilus", "4.1")
except ValueError:
    gi.require_version("Nautilus", "4.0")  # Nautilus 43-46, e.g. Ubuntu 24.04
from gi.repository import Gio, GLib, GObject, Nautilus

TAILSCALE = "/usr/bin/tailscale"
SENDER = os.path.expanduser("~/.local/bin/taildrop-send")


def notify(summary, body="", icon="document-send"):
    subprocess.Popen(["notify-send", "-a", "Taildrop", "-i", icon, summary, body])


class TaildropExtension(GObject.GObject, Nautilus.MenuProvider):
    def _get_targets(self):
        # Fetched fresh every time: Nautilus already rebuilds this menu
        # whenever the selection changes, and the call takes milliseconds.
        try:
            out = subprocess.run(
                [TAILSCALE, "file", "cp", "--targets"],
                capture_output=True, text=True, timeout=3,
            ).stdout
        except (OSError, subprocess.TimeoutExpired):
            return []
        targets = []
        for line in out.splitlines():
            parts = line.split("\t")
            if len(parts) >= 2:
                status = parts[2] if len(parts) > 2 else ""
                targets.append((parts[1], status))
        # Online devices first, then alphabetical
        targets.sort(key=lambda t: (bool(t[1]), t[0]))
        return targets

    def get_file_items(self, files):
        paths = []
        for f in files:
            loc = f.get_location()
            path = loc.get_path() if loc else None
            if not path or f.is_directory():
                return []  # Taildrop only sends regular local files
            paths.append(path)
        if not paths:
            return []

        targets = self._get_targets()
        if not targets:
            return []

        top = Nautilus.MenuItem(
            name="Taildrop::Send",
            label="Send with Taildrop",
            icon="document-send",
        )
        submenu = Nautilus.Menu()
        top.set_submenu(submenu)
        for name, status in targets:
            label = name if not status else f"{name} (offline)"
            item = Nautilus.MenuItem(name=f"Taildrop::{name}", label=label)
            item.connect("activate", self._send, paths, name)
            submenu.append_item(item)
        return [top]

    def _send(self, _item, paths, target):
        # The helper shows a progress window and does the online check.
        # Gio.Subprocess reaps the child, so no zombies are left in Nautilus.
        try:
            Gio.Subprocess.new([SENDER, target, *paths], Gio.SubprocessFlags.NONE)
        except GLib.Error as e:
            notify("Taildrop failed", e.message, "dialog-error")
