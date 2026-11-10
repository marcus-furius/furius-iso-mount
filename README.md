# Furius ISO Mount

A simple GTK+ interface to mount ISO, IMG, BIN, MDF and NRG image files without burning them to disk.

I'm the original developer of this application.

## Requirements

- Python 3
- PyGObject (`python3-gi`) with GTK 3
- `fuseiso` for FUSE-based mounting, or `pkexec` + `mount`/`umount` for loopback mounting
- `brasero` for burning images, `nautilus` for browsing mounted images (`nautilus-cd-burner` no longer exists, so burning is Brasero-only now)

## History

Originally written for Python 2 and PyGTK; ported to Python 3 and PyGObject/GTK3 in 2026.

Originally hosted on [Launchpad](https://code.launchpad.net/~marcus-furius/furiusisomount/pyfuriusisomount), converted from Bazaar to Git and now maintained here: https://github.com/marcus-furius/furius-iso-mount
