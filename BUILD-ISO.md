# Barvium 0.4 — experimental Ubuntu 26.04 live ISO

**Not yet boot-tested.** This generates a trial *live-only* ISO, not a system installer, and does not guarantee UEFI Secure Boot support. It is not ready for GitHub release without VM validation.

## Host preparation (Xubuntu 26.04, amd64)

Run in your development machine's terminal:

```bash
sudo apt update
sudo apt install debootstrap squashfs-tools xorriso grub-common grub-pc-bin grub-efi-amd64-bin mtools qemu-system-x86
```

These commands **install build tools on Xubuntu**, but do not remove your desktop or touch your installed filesystem. Expect multi-gigabyte downloads and working disk space (recommend at least 20 GB free).

## Build

```bash
./build.sh check
sudo ./build.sh iso
```

The script creates only `work/iso-build/` and `dist/` within the project. Build as root because `debootstrap`, APT chroot and temporary mounts require it. Network access to Ubuntu and Brave's upstream repositories is needed. The script refuses to overwrite an existing `work/iso-build/rootfs` directory. It unmounts its chroot mounts on normal exit or most errors; if interrupted by power loss, verify mounts with `findmnt` before manually cleaning up. **Do not blindly delete a mounted rootfs.**

Expected output (if the build succeeds): `dist/barvium-0.4-amd64.iso` and its `.sha256` hash. Because upstream package names and Ubuntu 26.04 live-boot behavior can change, this first builder is **experimental**. Investigate an error rather than executing cleanup commands you do not understand.

## VM test

```bash
qemu-system-x86_64 -m 4096 -smp 2 -enable-kvm -cdrom dist/barvium-0.4-amd64.iso -boot d
```

If KVM is not available, omit `-enable-kvm` (slower). Verify boot, auto-login to the **live** account, JWM, Brave, PCManFM, XTerm, networking, and absence of unexpected outbound reporting. For UEFI testing use separate OVMF firmware if installed. A successful `grub-mkrescue` command alone does **not** prove USB/BIOS/UEFI boot compatibility.

There is **no installer** and no persistent per-device install telemetry. The existing opt-in event reporter is intentionally **not run** during a live session. Do not publish installation-count claims for this ISO.

## Privacy and known limitations

The image purges a handful of optional Ubuntu reporting packages and disables Apport; this does not prove there are no other telemetry/network connections. Brave analytics policy controls still require implementation and verification. Package dependencies may bring in services that need audit. Test before making strong privacy claims.

The auto-logged-in live user has a locked password. This is for a disposable VM/live environment only; it is not a secure persistent installation configuration. Ubuntu updates and package provenance are maintained via official Ubuntu archives and Brave's signed APT repo. No unattended disk changes are made.
