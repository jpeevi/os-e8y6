# os:e8y6 0.7 — Bravium

Experimental **live ISO**, not a disk installer. Renamed from Barvium starting with v0.7.

## Security additions
- UFW defaults: deny inbound/forward; allow outbound, enabled on live boot.
- Native APT periodic timers and unattended-upgrades; no automatic reboot.
- Brave signed APT source is eligible for unattended upgrades; verify origins via `apt-cache policy brave-browser` in the guest.
- Existing user experience remains: Brave, JWM, Tint2, QTerminal, PCManFM.

**Warning:** System updates in a read-only live session are non-persistent and may use substantial temporary RAM. Persistent installations are planned for v0.8. No build/boot testing has been performed yet.

## Developer commands

Run `./build.sh check` and `python3 -m unittest discover -s tests -v` before the ISO build.

Safely inspect `findmnt -R "$PWD/work/iso-build"` before preserving an old build workspace. Build with `sudo ./build.sh iso` on Xubuntu, then use `./run-latest.sh` for QEMU.

## GitHub upload

Commit **source only**. `.gitignore` excludes `work/`, `out/`, `dist/`, caches, and ISO images. Before publishing, audit logs, metadata, passwords, SSH keys, personal data, licensing and Brave redistribution terms. Do not claim Secure Boot support, installer support, or a verified live boot until tested.

## Dependency repair (v0.7 source revision)

Removed the unavailable `apt-config-auto-update` package from the Ubuntu 26.04 package list.
`unattended-upgrades` and the existing APT periodic configuration remain enabled.
The ISO builder now checks target-release APT candidates immediately after `apt-get update`,
before installing the large live-system package set. This requires an initial `debootstrap`
step but avoids wasting time on an installation destined to fail from missing packages.
The source tests do not replace an actual live ISO build and QEMU boot test.
