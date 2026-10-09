# v0.7 GRUB identity + QEMU launcher fix

The original v0.7 `build-iso.sh` already used the new `os:e8y6` menu name, but `run-latest.sh` only searched `barvium-*.iso`. QEMU could therefore start an older v0.6 ISO.

This update makes the launcher select the most recently modified ISO matching either `os-e8y6-*.iso` or the legacy `barvium-*.iso` pattern, and prints the GRUB entry *inside* the selected ISO (using `xorriso`). It also makes the v0.7 GRUB label use release metadata and verifies the embedded menu after ISO creation.

## Verify before rebuilding

Run `./run-latest.sh` and check both the selected ISO path and embedded GRUB boot entry. If it shows `Try os:e8y6 0.7`, the existing ISO is fine and you do **not** need to rebuild just to correct the menu. If the current ISO itself has an incorrect GRUB entry, rebuild with this updated builder.

## If rebuilding

Run `./build.sh check` and `python3 -m unittest discover -s tests -v`. Before running `sudo ./build.sh iso`, inspect mounts with `findmnt -R "$PWD/work/iso-build"`. Do not move or delete mounted workspace directories. Preserve old builds and move unmounted workspaces aside with a unique name.

No source update changes the already-built ISO or your Xubuntu system.
