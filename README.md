# os:e8y6 0.8.1 — Bravium (experimental)

> Installer and top-panel troubleshooting patch. QEMU/KVM disposable virtual disks only; no physical-disk installs.

# os:e8y6 (Bravium) — v0.8 experimental

Minimal Brave-first Ubuntu 26.04 live OS using JWM, Tint2, QTerminal and PCManFM.

**Status:** experimental source. v0.8 ISO installation and dual-boot have **not** been verified. **Do not use this installer on physical disks.**

## Build host

Use Xubuntu 26.04 amd64. Install tools on the build host: `debootstrap`, `squashfs-tools`, `xorriso`, `grub-common`, `grub-pc-bin`, `grub-efi-amd64-bin`, `mtools`, and `qemu-system-x86`.

## Build and test

From the repository root:

```sh
./build.sh check
python3 -m unittest discover -s tests -v
./build.sh stage
findmnt -R "$PWD/work/iso-build"
```

Only if the workspace has **no active mounts**, back it up before building a new version; never delete a mounted root filesystem.

```sh
sudo ./build.sh iso
./run-latest.sh
```

Expected ISO: `dist/os-e8y6-0.8-amd64.iso`. Always verify the ISO path selected by the launcher. Building is not equivalent to boot-testing.

## Usage

The live environment starts Brave automatically. Use the Barvium menu for Files, QTerminal, networking and power actions. Alt+F4 opens the power menu. Tint2 is configured as the top panel.

## Experimental installer: **QEMU/KVM ONLY**

The `Install (QEMU test only)` menu item runs `bravium-install`, which checks for a QEMU/KVM virtual machine, requires manual `TEST-VM` confirmation, then opens Calamares. Calamares may provide erase-disk and alongside partitioning, but **neither path nor installed-system boot, account creation, UEFI, or persistence has been verified**. Only use **disposable** virtual disks with no important data; do not attempt installation to real disks or publish an install-ready ISO. v0.9 will add proper account setup and login.

## Privacy and maintenance

Ubuntu's optional reporting packages are removed or disabled where present. Barvium installation reporting is opt-in and not enabled by default. UFW rules are configured for default-deny incoming and automatic APT security updating is configured without automatic reboots. These behaviors need guest validation, especially for an installed system.

## License

Project-original code is released under GPL-3.0 (see `LICENSE`). Bundled Ubuntu, Brave and other packages retain their respective licenses; review redistribution and branding permissions before the planned public v0.10 ISO.

## v0.8.1 troubleshooting

This patch DOES NOT certify Calamares disk installation, dual boot, or the Tint2 panel.
The ISO builder now refuses to package an image if standard Calamares settings.conf is missing.
The menu installer gives a visible QEMU-only confirmation and logs errors to the session runtime directory.
For a missing panel, open QTerminal and read `~/.local/state/bravium/panel.log`, and check `pgrep -a tint2`.
If the installer prompts for authentication but fails, the live user needs appropriate narrowly-scoped administrator authorization; do not bypass authentication or install on a physical disk.
Build version: `./build.sh version`.
