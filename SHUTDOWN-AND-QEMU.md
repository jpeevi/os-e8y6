# Barvium v0.5 QEMU shutdown testing

The 0.4 live ISO boots into Brave, but Casper can print a request to remove the live CD during shutdown. The repeated `/cdrom` unmount errors are a guest-side behavior. This release adds a QEMU monitor-based eject workflow; it does **not** claim to have patched Casper itself.

Run QEMU as your regular user (not sudo):

```bash
chmod +x run-latest.sh
./run-latest.sh
```

Once Barvium shows "Please remove the installation medium, then press ENTER", switch to the terminal running QEMU (its stdin is the QEMU monitor) and type:

```text
eject -f barviumcd
```

Then focus the guest VM window and press Enter. If that does not work, use `info block` in the monitor to confirm the virtual drive is present. Repeated `/cdrom` errors indicate the guest may still be using the mount; forcibly closing QEMU is a last resort **only after** the guest has reached its shutdown prompt, not while writing data.

## Host permission checks

- `Permission denied` immediately on `./run-latest.sh` usually means the file is not executable: `chmod +x run-latest.sh`.
- An unreadable ISO can be fixed with `sudo chmod a+r dist/<iso-name>.iso` after verifying its ownership.
- For `/dev/kvm` access check `ls -l /dev/kvm` and `id -nG`. If appropriate, run `sudo usermod -aG kvm "$USER"`, then log out and back in. The launcher falls back to software emulation without KVM.
- Run `sudo` only for the ISO build, not to launch a graphical QEMU instance.

The original v0.4 ISO stays usable. An actual guest-side Casper shutdown patch should be investigated and boot-tested separately before release.
