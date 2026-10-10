# os:e8y6 v0.8.9 — Bravium (experimental)

**Brave is the OS interface.** This minimal Ubuntu 26.04-based live prototype uses JWM for invisible window management, starts Brave once, has no desktop bar or file manager, and opens QTerminal with **Ctrl+Alt+T**. Network management is via `nmcli`/`nmtui`; processes via `ps`/`top`. Optional utilities (including UFW and htop) are **not installed** by default. Thus no UFW default firewall is provided.

### Experimental installation

From QTerminal, run `bravium-install`, read the warning, and type `INSTALL`. Calamares is restricted to disposable QEMU/KVM **live** virtual disks. Version 0.8.9 retains the corrected unpackfs filename by pointing to `/cdrom/casper/filesystem.squashfs`; the remaining installer modules and installed-system boot **have not been validated**. Do not use real drives. After a failed install, treat the VM disk as potentially modified.

v0.8.9 restores `rsync` and checks `rsync`, `unsquashfs`, and `calamares` inside the isolated image before ISO packaging. This addresses the confirmed missing-tool failure but does not prove an installation will finish.

### Size improvements

Removes graphical audio preferences, UFW, and non-essential window management utilities from the base list. Includes a limited font set: Noto Core, DejaVu Core and Noto Color Emoji for basic multilingual fallback. Dependency packages may bring additional fonts, icons and services; they are *not* manually deleted. The ISO size reduction remains unmeasured until a full build. `systemd-zram-generator` uses zstd and a zram device with uncompressed capacity equal to half RAM, high swap priority.

### Build & test (Xubuntu development host)

```sh
./build.sh version
./build.sh check
python3 -m unittest discover -s tests -v
findmnt -R "$PWD/work/iso-build"
# Only if nothing is mounted, move an existing work/iso-build aside before rebuilding.
sudo ./build.sh iso
```

Expected ISO: `dist/os-e8y6-0.8.9-amd64.iso`. Full ISO build and QEMU boot tests must be completed on the development machine. Test browser, terminal shortcut, Calamares unpacking and target-disk boot; check `zramctl` and `swapon --show`. Do not proceed to v0.9 until the installed prototype is working.

Project source scripts are GPL-3.0 licensed; third-party packages retain their own licenses.
