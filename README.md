# nautilus-taildrop

Send files to your devices over [Tailscale Taildrop](https://tailscale.com/kb/1106/taildrop) from the right-click menu in GNOME Files (Nautilus). A small window shows the progress.

## The problem

Taildrop works well from a phone's share sheet, but on the Linux desktop the only way to send a file is the terminal: `tailscale file cp <file> <device>:`. GNOME Files has no share button for it.

## The fix

Two small pieces:

- **`taildrop.py`** is a [nautilus-python](https://gitlab.gnome.org/GNOME/nautilus-python) extension. It adds **Send with Taildrop** to the right-click menu for local files. A submenu lists your tailnet devices from `tailscale file cp --targets`, online ones first and offline ones marked.
- **`taildrop-send`** is a GTK4/libadwaita window that sends the files. It shows a progress bar, transfer speed, time left and an `(n/m)` counter for several files, and it has a Cancel button. It checks that the device is online before sending. On success it closes itself and posts a notification. On failure it stays open and shows the error.

For exact progress, `taildrop-send` streams each file into `tailscale file cp --name <name> -` itself, so it counts the bytes as they're written. It doesn't parse the CLI's terminal output.

## Requirements

- GNOME Files 43 or later (tested on Nautilus 50, Fedora 44)
- `nautilus-python` (Fedora: `sudo dnf install nautilus-python`, Debian/Ubuntu: `sudo apt install python3-nautilus`)
- GTK4, libadwaita and `python3-gobject`, all included with GNOME
- Tailscale, with your user allowed to use Taildrop without sudo:

```bash
sudo tailscale set --operator=$USER
tailscale file cp --targets   # should list your devices
```

## Install

```bash
./install.sh
```

This copies `taildrop-send` to `~/.local/bin` and the extension to `~/.local/share/nautilus-python/extensions`, then restarts Files so it loads the extension.

## Use

Right-click one or more files, choose **Send with Taildrop**, then pick a device.

## Uninstall

```bash
rm ~/.local/bin/taildrop-send ~/.local/share/nautilus-python/extensions/taildrop.py
nautilus -q
```

## Notes

- **Folders:** Taildrop can't send folders, so the menu entry doesn't appear for them. Zip the folder first.
- **Device list:** Files builds the context menu when the selection changes, not when you right-click. If a device has just come online, select a different file and right-click again to get a fresh list. `taildrop-send` checks the device again before sending, so an out-of-date label can't make it send to an offline device.
- **No Python threads in the extension:** nautilus-python keeps hold of Python's global lock between calls into the extension, so Python threads started inside Files never run. That's why the extension starts a separate process for the transfer.
- **Notifications and Do Not Disturb:** with Do Not Disturb on, GNOME doesn't show the "Sent" notification as a pop-up. The progress window still appears.
