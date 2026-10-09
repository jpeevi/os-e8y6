# Barvium v0.6 — experimental top-bar build

This is source code, **not a built or boot-tested ISO**.

## Key changes
- QTerminal replaces XTerm.
- JWM window manager; Tint2 top bar (task buttons, clock, battery, system tray, traffic speed).
- NetworkManager is selected as Netplan's network renderer; `nm-applet` offers network selection. In QEMU the simulated adapter appears as Ethernet, not physical Wi-Fi.
- Menu includes Brave, Files, Terminal, Network settings, Power, and Brave web apps discovered at session start.
- Alt+F4 opens the YAD power menu.
- Main Brave window gets a best-effort skip-taskbar hint while app windows remain eligible for the taskbar.

## Build on Xubuntu

Copy/merge the project into your existing folder, preserving `dist/` and your custom files.

```sh
./build.sh check
python3 -m unittest discover -s tests -v
findmnt -R "$PWD/work/iso-build"
```

If mounts are listed, **do not rename/delete** the workspace until they are safely unmounted. If no mounts exist, move the previous work tree out of the way and run:

```sh
sudo mv work/iso-build "work/iso-build-backup-$(date +%Y%m%d-%H%M%S)"
sudo ./build.sh iso
./run-latest.sh
```

The intended output is `dist/barvium-0.6-amd64.iso`.

## Important limitations
- This is still live-only, with no disk installer or persistence.
- Tint2/JWM integration, desktop menu launcher, tray applets, networking, and the Brave window filtering are **not yet verified in QEMU**.
- The `brave-*.desktop` convention may change; only desktop entries matching that pattern are displayed at session start. Pinning/unpinning is not yet separately implemented.
- Brave's internal close commands are not blocked, but the watchdog attempts to reopen the main window.
- System services may still emit network traffic. A privacy audit is required before public release.
- Desktop apps and menus may not work perfectly until boot-tested.

### Audio package correction
Ubuntu 26.04 does not provide `volumeicon-alsa` in the configured repositories. The v0.6 package list now uses `pavucontrol` for graphical volume configuration and no longer starts the missing `volumeicon` tray applet. A tray volume icon is **not** supplied by this change.
