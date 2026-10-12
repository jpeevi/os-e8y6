# os:e8y6 v0.8.18 (experimental)

**browser:e8y6 is the OS interface.**

os:e8y6 is a minimal, browser-first operating system prototype based on Ubuntu 26.04 amd64. It uses JWM for nearly invisible window management, without a conventional desktop panel, dock, or file manager.

The project is experimental. Installation testing is restricted to disposable QEMU/KVM virtual machines.

## Desktop and user interface

os:e8y6 uses browser:e8y6, a Qt WebEngine browser derived from KDE Falkon, as its primary graphical interface.

JWM manages application windows without presenting a traditional desktop environment.

Current components include:

- browser:e8y6 as the primary maximized, borderless interface.
- Event-driven browser recovery when the browser process exits.
- QTerminal for command-line access.
- A graphical power menu.
- Screen locking.
- NetworkManager for networking.
- PipeWire and WirePlumber for audio.
- Lightweight GTK and icon themes for utility dialogs.

There is no conventional desktop bar, dock, or file manager in the default interface.

### Keyboard shortcuts

| Shortcut | Action |
|---|---|
| Ctrl+Alt+T | Open QTerminal |
| Alt+F4 | Open the power menu |
| Super+L | Lock the screen |

The main browser window uses JWM's `noborder`, `notitle`, `maximized`, `nomove`, `noresize`, `nodrag`, and `nomin` options.

These are window-management restrictions, not security controls.

### Browser recovery

The `e8y6-session` script runs the browser using `e8y6-open-browser`.

If the browser process exits, the session attempts to restart it after a short delay.

This is exit-driven recovery rather than continuous process polling.

## Browser integration

The OS uses browser:e8y6 instead of Brave.

The browser Debian package is pinned in:

`packages/browser-e8y6.lock`

The current v0.8.18 package pin is:

- Package: `browser-e8y6`
- Version: `0.1.0-1`
- Architecture: `amd64`
- Distribution: GitHub Releases
- Integrity verification: SHA-256

The browser version and operating system version are managed independently.

## Experimental installation

os:e8y6 uses Calamares for experimental installation.

**Installation is restricted to disposable QEMU/KVM virtual disks. Do not use physical disks or drives containing valuable data.**

Open QTerminal using Ctrl+Alt+T, then run:

```sh
e8y6-install
```

The launcher checks for an interactive terminal, QEMU/KVM virtualization, a Casper live session, and the required Calamares configuration.

Read the installation warning carefully and type:

`INSTALL`

Calamares will then launch with elevated privileges.

Inspect the selected virtual disk and all proposed partition changes before proceeding.

A failed installation may still modify the virtual disk.

### Installer development

**v0.8.10–v0.8.12**

- Corrected the SquashFS unpack path.
- Restored required installation utilities, including `rsync`.
- Added installer configuration and branding validation.
- Refined filesystem, GRUB, and initramfs integration.
- Addressed Calamares startup configuration failures.

**v0.8.13**

- Stabilized Calamares configuration, branding, and log collection.
- Removed obsolete Lubuntu installer jobs.
- Preserved GRUB and initramfs integration.
- Recorded successful QEMU installation, independent disk boot, persistence, and browser window-restriction testing.

**v0.8.18**

- Updated Calamares settings and module configuration.
- Introduced installed-session integration handling.
- Updated the installer launcher to `e8y6-install`.
- Refined kernel, session, and installer logging.
- Added installer validation scripts and tests.

The v0.8.13 runtime results do not automatically verify the changes introduced in v0.8.18. Fresh acceptance testing remains necessary.

## Clean installation test

Use a disposable 32 GB virtual disk, for example:

`vm-disks/e8y6-clean.qcow2`

Boot the v0.8.18 ISO in QEMU/KVM with only this virtual disk attached.

Open QTerminal and launch `e8y6-install`.

Verify the selected disk before confirming any erase operation.

After installation, shut down the VM completely and boot the same virtual disk without the ISO.

Verify:

- browser:e8y6 starts correctly.
- QTerminal opens using Ctrl+Alt+T.
- Networking is functional.
- The graphical power menu works.
- Screen locking works.
- zram is active.
- A saved file survives reboot.

Do not claim that the v0.8.18 installation has passed until the complete test succeeds.

## Dual-boot acceptance test

Dual-boot is experimental and must be evaluated only in QEMU/KVM.

Use a separate disposable 64 GB virtual disk, for example:

`vm-disks/e8y6-dualboot.qcow2`

Configure the VM with UEFI OVMF firmware and a private, writable OVMF variables file.

Install an Ubuntu test guest first, leaving free space for os:e8y6.

Confirm Ubuntu boots before attempting the second installation.

Boot the os:e8y6 ISO in the same firmware mode, inspect the Calamares partitioning proposal, and proceed only if the existing operating system partitions and EFI system partition are preserved.

After installation, boot both operating systems independently and verify that their files remain intact.

Never attach physical disks or host partitions to these tests.

Dual-boot remains unverified until these acceptance tests pass.

## Minimal system design

os:e8y6 avoids a conventional full desktop environment while retaining the packages required for its browser-first workflow.

The base package selection includes:

- JWM, Xorg, and Xinit.
- QTerminal.
- NetworkManager.
- PipeWire and WirePlumber.
- Calamares and required installation utilities.
- `systemd-zram-generator`.
- Noto Core, DejaVu Core, Noto Color Emoji, and Ubuntu fonts.
- Greybird GTK theme and Papirus icons.
- `unattended-upgrades`.

Dependencies may install additional services, fonts, icons, or libraries. These are not automatically removed simply to reduce ISO size.

Optional utilities such as UFW and htop are not installed by default.

**The base system does not provide a default UFW firewall.**

## Memory management

os:e8y6 uses `systemd-zram-generator` for compressed swap.

The intended configuration uses:

- zstd compression.
- Uncompressed zram capacity equal to half the system RAM.
- Swap priority 100.

Verify the live system using:

```sh
zramctl
swapon --show
```

## Build and test

Development and ISO building take place on an Ubuntu/Xubuntu development host.

Build operations must remain isolated from the host's installed operating system.

Do not modify the host firewall, desktop environment, or installed packages as part of ISO construction.

### Source checks

```sh
./build.sh version
./build.sh check
python3 -m unittest discover -s tests -v
```

These checks validate source configuration and test expectations. They cannot replace runtime testing in QEMU.

### Staging

Prepare the project filesystem overlay:

```sh
./build.sh stage
```

This creates staged project files under `out/staging/` without generating an ISO.

### ISO build

Inspect existing build mounts first:

```sh
findmnt -R "$PWD/work/iso-build"
```

Resolve any existing mounts safely before rebuilding.

Then run:

```sh
sudo ./build.sh iso
```

Expected output filename:

`dist/os-e8y6-0.8.18-amd64.iso`

A successful ISO build does not establish successful live boot or installation. Validate both in QEMU.

## Technical debt

### Browser package upgrade

os:e8y6 v0.8.18 currently pins browser:e8y6 version `0.1.0-1`.

The newer browser package `0.1.3-2` has been built separately but has not yet been integrated into the OS ISO.

**Deferred work:**

- Update `packages/browser-e8y6.lock` to version `0.1.3-2`.
- Update the GitHub Releases download URL.
- Calculate and verify the new SHA-256 checksum.
- Rebuild the ISO with the updated browser.
- Test the live browser session in QEMU.
- Test browser startup after installation and reboot.
- Investigate remaining legacy startup URL behavior, including `falkon:start`.

Until these steps are completed, the newer browser must not be described as included in os:e8y6.

### Installer testing

- Complete fresh v0.8.18 clean-install testing.
- Verify independent installed-disk boot and persistence.
- Complete disposable-VM UEFI/GPT dual-boot testing.
- Validate browser recovery and graphical utility behavior after installation.

### Further improvements

- Review login and session handling.
- Improve browser recovery and failure diagnostics.
- Measure ISO size and identify safe reductions.
- Continue desktop and installer integration testing.

## Licensing

Project source scripts are licensed under GPL-3.0.

Third-party components, including Ubuntu packages, KDE Falkon-derived browser components, and other dependencies, retain their respective licenses.
