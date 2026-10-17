#!/usr/bin/env bash
# os:e8y6 experimental live ISO builder. Does NOT install to disks.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/work/iso-build"
ROOTFS="$WORK/rootfs"
IMAGE="$WORK/image"
RELEASE_NAME="os:e8y6"
RELEASE_VERSION="$(cat "$ROOT/VERSION")"
ISO="$ROOT/dist/os-e8y6-${RELEASE_VERSION}-amd64.iso"
MIRROR="${UBUNTU_MIRROR:-http://archive.ubuntu.com/ubuntu}"
MOUNTS=()
fail() { echo "ERROR: $*" >&2; exit 1; }
cleanup() {
  for (( i=${#MOUNTS[@]}-1; i>=0; i-- )); do umount -lf "${MOUNTS[$i]}" || true; done
}
trap cleanup EXIT
[[ $EUID -eq 0 ]] || fail 'Use sudo to build inside the isolated work directory.'
[[ $(uname -m) == x86_64 ]] || fail 'This first builder only supports amd64 hosts.'
[[ -d "$ROOT/packages" && -f "$ROOT/build.sh" ]] || fail 'Invalid project root.'
for c in debootstrap mksquashfs grub-mkrescue xorriso chroot mount findmnt; do
  command -v "$c" >/dev/null || fail "Missing host tool: $c (see BUILD-ISO.md)"
done
[[ ! -e "$ROOTFS" ]] || fail 'Build directory exists. Inspect/unmount it manually before moving it aside; do not delete blindly.'
mkdir -p "$ROOTFS" "$IMAGE/boot/grub" "$IMAGE/casper" "$ROOT/dist"
echo '[1/7] Bootstrap Ubuntu Resolute (this downloads packages)'
debootstrap --arch=amd64 --variant=minbase resolute "$ROOTFS" "$MIRROR"
printf 'os:e8y6 image-building root\n' > "$ROOTFS/etc/e8y6-build-rootfs"
cat > "$ROOTFS/etc/apt/sources.list" <<SOURCES
deb $MIRROR resolute main restricted universe multiverse
deb $MIRROR resolute-updates main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu resolute-security main restricted universe multiverse
SOURCES
cp /etc/resolv.conf "$ROOTFS/etc/resolv.conf"
mkdir -p "$ROOTFS/proc" "$ROOTFS/sys" "$ROOTFS/dev" "$ROOTFS/run"
mount -t proc proc "$ROOTFS/proc"; MOUNTS+=("$ROOTFS/proc")
mount --rbind /sys "$ROOTFS/sys"; mount --make-rslave "$ROOTFS/sys"; MOUNTS+=("$ROOTFS/sys")
mount --rbind /dev "$ROOTFS/dev"; mount --make-rslave "$ROOTFS/dev"; MOUNTS+=("$ROOTFS/dev")
mount --bind /run "$ROOTFS/run"; MOUNTS+=("$ROOTFS/run")
BROWSER_DEB="$("$ROOT/scripts/fetch-browser-package.sh" "$ROOT/work/browser-cache")"
cp "$ROOT/privacy/remove-optional-reporting-chroot.sh" "$ROOTFS/tmp/privacy.sh"
echo '[2/7] Install live-system packages'
mapfile -t PACKAGES < <(sed 's/#.*//; /^[[:space:]]*$/d' "$ROOT/packages/base.list")
chroot "$ROOTFS" apt-get update
# Fail before downloading a large set of packages if Ubuntu does not publish one.
# Query the isolated target release, never the Xubuntu host package database.
echo 'Checking target-release package availability'
MISSING=()
for pkg in "${PACKAGES[@]}" casper linux-image-generic; do
  candidate="$(chroot "$ROOTFS" apt-cache policy "$pkg" | sed -n 's/^[[:space:]]*Candidate: //p' | head -n 1)"
  if [[ -z "$candidate" || "$candidate" == '(none)' ]]; then
    MISSING+=("$pkg")
  fi
done
if (( ${#MISSING[@]} )); then
  printf 'ERROR: Ubuntu Resolute has no installation candidate for: %s\n' "${MISSING[*]}" >&2
  fail 'Correct packages/base.list before attempting package installation.'
fi
chroot "$ROOTFS" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  "${PACKAGES[@]}" casper linux-image-generic || fail 'Package installation failed; inspect work/iso-build/rootfs.'
# Verify indispensable installer commands inside the rootfs before creating a large ISO.
# A package candidate check alone does not ensure an executable made it into the image.
for installer_tool in rsync unsquashfs calamares parted mkfs.ext4 mkfs.vfat blkid grub-install update-initramfs; do
  chroot "$ROOTFS" /usr/bin/env sh -c 'command -v "$1" >/dev/null' sh "$installer_tool" || \
    fail "Missing required installer executable in image: $installer_tool"
done
# Dependency state matters as well as executable presence.
for installer_pkg in calamares calamares-settings-lubuntu rsync squashfs-tools parted e2fsprogs dosfstools util-linux grub-pc-bin grub-efi-amd64-bin initramfs-tools casper; do
  chroot "$ROOTFS" dpkg-query -W -f='${Status}' "$installer_pkg" | grep -qx 'install ok installed' || \
    fail "Installer package not fully installed: $installer_pkg"
done
for executable in /usr/bin/rsync /usr/bin/calamares; do
  if chroot "$ROOTFS" ldd "$executable" | grep -q 'not found'; then
    fail "Unresolved runtime libraries: $executable"
  fi
done
echo '[3/7] Install pinned browser:e8y6 release'
install -m 0644 "$BROWSER_DEB" "$ROOTFS/tmp/browser-e8y6.deb"
chroot "$ROOTFS" env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends /tmp/browser-e8y6.deb || fail 'Cannot install browser:e8y6 or resolve Qt WebEngine dependencies.'
chroot "$ROOTFS" test -x '/usr/bin/browser:e8y6' || fail 'Browser executable missing in rootfs.'
# The Qt SQL library is not the SQLite plugin. Verify real plugin files, not just
# package metadata, so a build cannot ship the browser's startup-error dialog.
chroot "$ROOTFS" dpkg-query -W -f='${Status}' libqt6sql6-sqlite | grep -qx 'install ok installed' || \
  fail 'Qt SQLite driver package is not fully installed.'
SQLITE_PLUGIN="$(chroot "$ROOTFS" dpkg -L libqt6sql6-sqlite | grep -E '/sqldrivers/libqsqlite[.]so$' | head -n 1)"
[[ -n "$SQLITE_PLUGIN" && -f "$ROOTFS$SQLITE_PLUGIN" ]] || \
  fail 'Qt SQLite driver libqsqlite.so missing from ISO rootfs.'
if chroot "$ROOTFS" ldd "$SQLITE_PLUGIN" | grep -q 'not found'; then
  fail 'Qt SQLite driver has unresolved shared-library dependencies.'
fi
chroot "$ROOTFS" bash /tmp/privacy.sh
# Configure security policies without applying firewall rules to the build host.
cp "$ROOT/scripts/configure-security-chroot.sh" "$ROOTFS/tmp/configure-security.sh"
chroot "$ROOTFS" bash /tmp/configure-security.sh
echo '[4/7] Configure read-only live session'
for script in e8y6-open-browser e8y6-session e8y6-install e8y6-power-menu e8y6-lock e8y6-logout e8y6-debug e8y6-core-update e8y6-terminal; do
  install -D -m 0755 "$ROOT/scripts/$script" "$ROOTFS/usr/local/bin/$script"
done
# Theme and branded lock-screen assets (no desktop wallpaper).
install -D -m 0644 "$ROOT/config/gtk/3.0/settings.ini" "$ROOTFS/etc/gtk-3.0/settings.ini"
install -D -m 0644 "$ROOT/config/gtk/3.0/settings.ini" "$ROOTFS/etc/skel/.config/gtk-3.0/settings.ini"
install -D -m 0644 "$ROOT/config/gtk/3.0/settings.ini" "$ROOTFS/etc/skel/.config/gtk-4.0/settings.ini"
install -D -m 0644 "$ROOT/config/fontconfig/fonts.conf" "$ROOTFS/etc/fonts/local.conf"
install -D -m 0644 "$ROOT/config/branding/lockscreen.png" "$ROOTFS/usr/share/os-e8y6/lockscreen.png"
# NetworkManager and nmtui are supplied by network-manager; ensure live boot starts it.
chroot "$ROOTFS" systemctl enable NetworkManager.service
# Restore the verified v0.8.13 packaged Calamares workflow rather than
# replacing its vendor module sequence with a hand-assembled one.
SETTINGS="$ROOTFS/etc/calamares/settings.conf"
if [[ ! -f "$SETTINGS" ]]; then
  [[ -f "$ROOTFS/usr/share/calamares/settings.conf" ]] || \
    fail 'calamares-settings-lubuntu did not provide settings.conf.'
  install -D -m 0644 "$ROOTFS/usr/share/calamares/settings.conf" "$SETTINGS"
fi
python3 "$ROOT/scripts/prepare-calamares-settings.py" "$SETTINGS" || \
  fail 'Packaged Calamares workflow differs from the verified configuration.'
install -D -m 0644 "$ROOT/config/calamares/initramfs.conf" \
  "$ROOTFS/etc/calamares/modules/initramfs.conf"
if ! find "$ROOTFS/usr/lib" "$ROOTFS/usr/share/calamares" -iname '*initramfs*' -print -quit | grep -q .; then
  fail 'Calamares initramfs module missing.'
fi
# Preserve installer diagnostics without requiring optional Ubuntu ISO metadata.
install -D -m 0755 "$ROOT/scripts/os-e8y6-installer-logs" \
  "$ROOTFS/usr/local/bin/os-e8y6-installer-logs"
python3 "$ROOT/scripts/prepare-calamares-v0811.py" "$ROOTFS" || \
  fail 'v0.8.13 Calamares vendor workflow adaptation failed.'
# Install os:e8y6-owned branding.
install -D -m 0644 "$ROOT/config/calamares/branding/branding.desc" \
  "$ROOTFS/etc/calamares/branding/os-e8y6/branding.desc"
install -D -m 0644 "$ROOT/config/calamares/branding/wordmark.svg" \
  "$ROOTFS/etc/calamares/branding/os-e8y6/wordmark.svg"
# Fail before ISO mastering if the installer branding is structurally unusable.
python3 "$ROOT/scripts/validate-calamares-branding.py" \
  "$ROOTFS/etc/calamares/branding/os-e8y6/branding.desc" \
  "$ROOTFS/etc/calamares/settings.conf" || fail 'Calamares branding/settings validation failed.'
# Preserve v0.8.14+ removal of the inherited live user/autologin on disk.
install -D -m 0644 "$ROOT/config/calamares/modules/shellprocess-installed-session.conf" \
  "$ROOTFS/etc/calamares/modules/shellprocess-installed-session.conf"
python3 "$ROOT/scripts/integrate-installed-session.py" "$SETTINGS" || \
  fail 'Cannot safely integrate installed-user cleanup with vendor Calamares sequence.'
# Installed GRUB should use the public product name, not its Ubuntu base.
if [[ -f "$ROOTFS/etc/default/grub" ]]; then
  sed -i '/^GRUB_DISTRIBUTOR=/d' "$ROOTFS/etc/default/grub"
fi
printf '%s\n' 'GRUB_DISTRIBUTOR="os:e8y6"' >> "$ROOTFS/etc/default/grub"
# Ubuntu/Lubuntu Calamares defaults refer to multiple minimal images that we do not build.
# os:e8y6 produces exactly one image, so stage an explicit single-source unpack rule.
install -D -m 0644 "$ROOT/config/calamares/unpackfs.conf" \
  "$ROOTFS/etc/calamares/modules/unpackfs.conf"
# zram: half of RAM as compressed swap with high priority (no disk swap created).
install -D -m 0644 "$ROOT/config/zram/zram-generator.conf" \
  "$ROOTFS/etc/systemd/zram-generator.conf"
# Minimal JWM browser shell. No panel, desktop shortcuts or autostart entries.
install -D -m 0644 "$ROOT/config/skel/.jwmrc" "$ROOTFS/etc/skel/.jwmrc"
# Scoped polkit action and one-shot systemd guard create a runtime marker only on live QEMU/KVM.
install -D -m 0755 "$ROOT/scripts/e8y6-calamares-root" "$ROOTFS/usr/local/libexec/e8y6-calamares-root"
install -D -m 0755 "$ROOT/scripts/e8y6-live-installer-enable" "$ROOTFS/usr/local/libexec/e8y6-live-installer-enable"
install -D -m 0644 "$ROOT/config/polkit/org.os-e8y6.live-install.policy" "$ROOTFS/usr/share/polkit-1/actions/org.os-e8y6.live-install.policy"
install -D -m 0644 "$ROOT/config/polkit/49-e8y6-live-installer.rules" "$ROOTFS/etc/polkit-1/rules.d/49-e8y6-live-installer.rules"
install -D -m 0644 "$ROOT/config/systemd/e8y6-live-installer-enable.service" "$ROOTFS/etc/systemd/system/e8y6-live-installer-enable.service"
chroot "$ROOTFS" systemctl enable e8y6-live-installer-enable.service
install -D -m 0644 "$ROOT/config/network/01-e8y6-network.yaml" "$ROOTFS/etc/netplan/01-e8y6-network.yaml"
install -D -m 0644 "$ROOT/config/network/10-e8y6-managed.conf" "$ROOTFS/etc/NetworkManager/conf.d/10-e8y6-managed.conf"
mkdir -p "$ROOTFS/usr/share/applications"
install -m 0755 "$ROOT/config/skel/.xinitrc" "$ROOTFS/etc/skel/.xinitrc"
install -m 0644 "$ROOT/config/skel/.profile" "$ROOTFS/etc/skel/.profile"
install -m 0644 "$ROOT/config/etc/issue" "$ROOTFS/etc/issue"
# User-visible release identity while retaining Ubuntu as the package base.
cat > "$ROOTFS/etc/os-release" <<OS_RELEASE
NAME="os:e8y6"
PRETTY_NAME="os:e8y6 ${RELEASE_VERSION}"
ID=ubuntu
ID_LIKE=debian
VERSION_ID="26.04"
VERSION="${RELEASE_VERSION} (Ubuntu 26.04 base)"
VERSION_CODENAME=resolute
UBUNTU_CODENAME=resolute
HOME_URL="https://github.com"
OS_RELEASE

chroot "$ROOTFS" useradd -m -s /bin/bash -G audio,video,plugdev,netdev e8y6
install -m 0644 "$ROOT/config/skel/.profile" "$ROOTFS/home/e8y6/.profile"
chroot "$ROOTFS" chown e8y6:e8y6 /home/e8y6/.profile
# Cosmetic hostname only; no account change on developer host.
printf "os-e8y6\n" > "$ROOTFS/etc/hostname"
cat > "$ROOTFS/etc/hosts" <<'HOSTS'
127.0.0.1 localhost
127.0.1.1 os-e8y6
HOSTS
chroot "$ROOTFS" passwd -l e8y6
mkdir -p "$ROOTFS/etc/systemd/system/getty@tty1.service.d"
cat > "$ROOTFS/etc/systemd/system/getty@tty1.service.d/autologin.conf" <<'GETTY'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin e8y6 --noclear %I $TERM
GETTY
# No opt-in consent during a live session: deliberately do not install reporter hooks.
chroot "$ROOTFS" apt-get clean
rm -f "$ROOTFS/tmp/browser-e8y6.deb" "$ROOTFS/tmp/privacy.sh" "$ROOTFS/tmp/configure-security.sh" "$ROOTFS/etc/e8y6-build-rootfs"
rm -rf "$ROOTFS/var/lib/apt/lists/"*
# Final installed-dependency check after all rootfs customizations.
python3 "$ROOT/scripts/validate-installer.py" "$ROOTFS" || fail 'Installer audit failed before SquashFS.'
# Unmount chroot mounts before squashfs packaging.
cleanup; MOUNTS=()
echo '[5/7] Squash filesystem'
mksquashfs "$ROOTFS" "$IMAGE/casper/filesystem.squashfs" -comp xz -noappend
KERNEL="$(find "$ROOTFS/boot" -maxdepth 1 -name 'vmlinuz-*' | sort -V | tail -1)"
INITRD="$(find "$ROOTFS/boot" -maxdepth 1 -name 'initrd.img-*' | sort -V | tail -1)"
[[ -f "$KERNEL" && -f "$INITRD" ]] || fail 'Kernel or initrd missing.'
cp "$KERNEL" "$IMAGE/casper/vmlinuz"
cp "$INITRD" "$IMAGE/casper/initrd"
cat > "$IMAGE/boot/grub/grub.cfg" <<GRUB
set timeout=5
set default=0
menuentry "Try ${RELEASE_NAME} ${RELEASE_VERSION} (live)" {
  linux /casper/vmlinuz boot=casper noswap quiet splash ---
  initrd /casper/initrd
}
GRUB
# Fail early if the installer points to a nonexistent squashfs image.
python3 "$ROOT/scripts/validate-calamares-unpack.py" \
  "$ROOTFS/etc/calamares/modules/unpackfs.conf" "$IMAGE"
for required_image_path in usr/bin/rsync usr/bin/calamares etc/calamares/settings.conf etc/calamares/modules/unpackfs.conf; do
  unsquashfs -ll "$IMAGE/casper/filesystem.squashfs" "$required_image_path" | grep -Fq "$required_image_path" || \
    fail "Final SquashFS missing: $required_image_path"
done
echo '[6/7] Assemble BIOS/UEFI ISO (no Secure Boot guarantee)'
grub-mkrescue -o "$ISO" "$IMAGE" -volid OSE8Y6_0819
echo '[7/7] Verify ISO GRUB identity'
TMP_GRUB="$(mktemp)"
if ! xorriso -osirrox on -indev "$ISO" -extract /boot/grub/grub.cfg "$TMP_GRUB" >/dev/null 2>&1; then
  rm -f "$TMP_GRUB"
  fail 'Could not read GRUB configuration from generated ISO.'
fi
if ! grep -Fq "Try ${RELEASE_NAME} ${RELEASE_VERSION} (live)" "$TMP_GRUB"; then
  rm -f "$TMP_GRUB"
  fail 'Generated ISO contains unexpected GRUB menu label.'
fi
rm -f "$TMP_GRUB"
echo "Verified: ISO contains the expected os:e8y6 ${RELEASE_VERSION} boot label."
echo 'ISO produced; it has NOT been boot-tested.'
sha256sum "$ISO" | tee "$ISO.sha256"
echo "Next: test with QEMU and confirm networking, browser:e8y6, and the live login before distribution."
