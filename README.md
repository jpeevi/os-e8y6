# os:e8y6 v0.8.12 (experimental)

**Brave is the OS interface.** This minimal Ubuntu 26.04-based live prototype uses JWM for invisible window management, starts Brave once, has no desktop bar or file manager, and opens QTerminal with **Ctrl+Alt+T**. Network management is via `nmcli`/`nmtui`; processes via `ps`/`top`. Optional utilities (including UFW and htop) are **not installed** by default. Thus no UFW default firewall is provided.

### Experimental installation

From QTerminal, run `bravium-install`, read the warning, and type `INSTALL`. Calamares is restricted to disposable QEMU/KVM **live** virtual disks. Version 0.8.10 retains the corrected unpackfs filename by pointing to `/cdrom/casper/filesystem.squashfs`; the remaining installer modules and installed-system boot **have not been validated**. Do not use real drives. After a failed install, treat the VM disk as potentially modified.

v0.8.10 restores `rsync` and checks `rsync`, `unsquashfs`, and `calamares` inside the isolated image before ISO packaging. This addresses the confirmed missing-tool failure but does not prove an installation will finish.

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

Expected ISO: `dist/os-e8y6-0.8.10-amd64.iso`. Full ISO build and QEMU boot tests must be completed on the development machine. Test browser, terminal shortcut, Calamares unpacking and target-disk boot; check `zramctl` and `swapon --show`. Do not proceed to v0.9 until the installed prototype is working.

Project source scripts are GPL-3.0 licensed; third-party packages retain their own licenses.

### v0.8.10 installer audit

Adds explicit partitioning, filesystem, and GRUB runtime tools and replaces inherited Dracut jobs with the Ubuntu `initramfs` job. The build refuses an unrecognized Calamares sequence rather than silently shipping it. Calamares may still contain other Lubuntu-specific jobs; a full QEMU installation and installed-disk boot remain mandatory before claiming installer support.

### v0.8.12 Calamares refinement and testing

Calamares uses the `os:e8y6` text-only wordmark. The ISO build keeps required storage, account, initramfs, and bootloader modules, removes known Lubuntu-only optional steps, and makes optional `cdrom.sources` removal tolerant of a missing file. Installed GRUB should display `os:e8y6`. **This has not been validated in a full fresh QEMU installation**.

**Clean-install acceptance test:** Attach only `vm-disks/bravium-clean.qcow2` (32 GB) to a QEMU VM booted from `dist/os-e8y6-0.8.12-amd64.iso`. In the guest press Ctrl+Alt+T and run `bravium-install`; check the target disk is the disposable 32 GB image before confirming erase. Once complete, shut down QEMU completely and boot the same QCOW2 without the ISO. Verify Brave, terminal, network, zram, and a saved file after reboot.

**Dual-boot acceptance test (UEFI/GPT):** Use only the separate disposable `vm-disks/bravium-dualboot.qcow2` (64 GB). Back it up before modifying partitions. Create a test VM with UEFI OVMF firmware and a private writable OVMF variables copy; attach **only that virtual disk**, never `/dev/sd*` or the host's partitions. Install an Ubuntu test guest first, reserving unallocated space for os:e8y6. Confirm Ubuntu boots before starting Calamares. Then boot the os:e8y6 ISO in the **same firmware mode** with that same disk, inspect Calamares's proposed alongside partitions carefully, and install only if the original OS partitions and EFI system partition are preserved. Boot **both** OSes independently and verify their files survive. Treat dual-boot as unverified until these tests pass.

Source checks validate configuration only. They cannot substitute for real QEMU tests of erase, alongside, BIOS/UEFI boot, or completion of Calamares jobs.

### v0.8.12 installer and Brave window repair

Fixes the Calamares 3.3 startup crash caused by missing branding `style` mapping, ensures required boolean installer settings are explicitly set, and validates branding YAML and asset paths at build time. JWM's Brave window group now includes `nomove`, `noresize`, and `nodrag` without adding a browser watchdog. These are window-manager restrictions, not a security boundary. `python3-yaml` (PyYAML) is required on the Xubuntu build host for validation (`sudo apt install python3-yaml`).

**Testing:** Boot the ISO with only a disposable QEMU disk attached. Confirm Calamares opens without a FATAL YAML error, verify navigation before running the installer, and test both normal and Alt-drag attempts on the main Brave window. Only then attempt erase-disk or alongside installation; do not use physical disks. The patch has source-level tests only; runtime behavior is not verified.
