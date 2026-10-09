# Barvium v0.5 — Browser-shell prototype

## What it does

- No full desktop environment, graphical login manager, or panel.
- JWM right-click / Super+Space menu lists only Brave, Files, Terminal.
- Alt+F4 opens a graphical **Power menu** (Restart, Log out, Shut down, Cancel).
- The main Brave window is requested borderless and maximized using WM_CLASS `BarviumMain`.
- A watchdog attempts to reopen the main browser window if it disappears, even if Brave PWAs remain open.
- Super+N opens `nmtui` in xterm for Wi-Fi and network selection; networking uses NetworkManager.
- Brave retains support for installing PWAs. Live ISO profiles and apps do **not** persist after reboot.

## Current limitations and safety

- Browser window classification (`--class=BarviumMain`) is Chromium/Brave-dependent; validate WM_CLASS in QEMU with `xprop WM_CLASS` and adjust if needed. Brave single-instance behavior may cause the `--class` argument to be ignored if an existing Brave process is running. The watchdog consequently may spawn multiple windows in this case. Stop and fix if that occurs.
- Alt+F4 is a JWM-level shortcut, not a secure kiosk lock; alternate methods and Brave browser shortcuts can close windows. The watchdog aims to restore the main window.
- Power actions use systemd/logind permissions and require QEMU testing. Log out only exits JWM; tty1 autologin and shell profile behavior may return to a text session or restart a session depending on environment.
- JWM `-exit` behavior is untested. Confirm with the installed JWM version; change to an equivalent supported logout mechanism if necessary.
- This is **live-only**: no disk installer and no claim of full ChromeOS compatibility.
- Existing privacy-removal hooks remain experimental and do not prove complete telemetry elimination.
- No changes to your Xubuntu host are required besides build dependencies.

## Build and test on Xubuntu

1. Back up your existing Barvium folder. Copy these project files over, keeping your own `dist/` folder.
2. Run `./build.sh check` and `python3 -m unittest discover -s tests -v`.
3. Existing `work/iso-build/rootfs` must be inspected/unmounted/moved out of the way before rebuilding. **Do not delete mounted paths blindly.**
4. Run `sudo ./build.sh iso` and then `./run-latest.sh`.
5. Test Alt+F4, shutdown, Brave close/relaunch, Super+N networking, and web-app windows in QEMU.

No ISO was built or boot-tested by these source-only checks.
