#!/usr/bin/env bash
# os:e8y6 experimental live ISO builder. Does NOT install to disks.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="$ROOT/work/iso-build"
ROOTFS="$WORK/rootfs"
IMAGE="$WORK/image"
RELEASE_NAME="os:e8y6"
RELEASE_VERSION="$(cat "$ROOT/VERSION")"
RELEASE_CODENAME="Bravium"
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
printf 'Barvium image-building root\n' > "$ROOTFS/etc/barvium-build-rootfs"
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
cp "$ROOT/scripts/install-brave-chroot.sh" "$ROOTFS/tmp/install-brave.sh"
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
echo '[3/7] Install Brave from upstream repository'
chroot "$ROOTFS" env BARVIUM_BUILD_CHROOT=yes bash /tmp/install-brave.sh
chroot "$ROOTFS" bash /tmp/privacy.sh
# Configure security policies without applying firewall rules to the build host.
cp "$ROOT/scripts/configure-security-chroot.sh" "$ROOTFS/tmp/configure-security.sh"
chroot "$ROOTFS" bash /tmp/configure-security.sh
echo '[4/7] Configure read-only live session'
for script in barvium-power-menu barvium-open-brave barvium-brave-watchdog barvium-session barvium-net-speed barvium-webapp-menu bravium-install; do
  install -D -m 0755 "$ROOT/scripts/$script" "$ROOTFS/usr/local/bin/$script"
done
# NetworkManager and nmtui are supplied by network-manager; ensure live boot starts it.
chroot "$ROOTFS" systemctl enable NetworkManager.service
# Do not create a guessed Calamares configuration; verify the distribution ships it.
if [[ ! -f "$ROOTFS/etc/calamares/settings.conf" && ! -f "$ROOTFS/usr/share/calamares/settings.conf" ]]; then
  fail "Calamares configuration missing in target image: check calamares-settings-lubuntu package contents."
fi

install -D -m 0644 "$ROOT/config/tint2/tint2rc" "$ROOTFS/etc/barvium/tint2rc"
install -D -m 0644 "$ROOT/config/network/01-barvium-network.yaml" "$ROOTFS/etc/netplan/01-barvium-network.yaml"
install -D -m 0644 "$ROOT/config/network/10-barvium-managed.conf" "$ROOTFS/etc/NetworkManager/conf.d/10-barvium-managed.conf"
mkdir -p "$ROOTFS/usr/share/applications"
cat > "$ROOTFS/usr/share/applications/barvium-menu.desktop" <<'MENU'
[Desktop Entry]
Type=Application
Name=Barvium Menu
Exec=xdotool key super+space
Icon=start-here
Terminal=false
MENU
install -m 0644 "$ROOT/config/skel/.jwmrc" "$ROOTFS/etc/skel/.jwmrc"
install -m 0755 "$ROOT/config/skel/.xinitrc" "$ROOTFS/etc/skel/.xinitrc"
install -m 0644 "$ROOT/config/etc/issue" "$ROOTFS/etc/issue"
# User-visible release identity while retaining Ubuntu as the package base.
cat > "$ROOTFS/etc/os-release" <<'OS_RELEASE'
NAME="os:e8y6"
PRETTY_NAME="os:e8y6 0.8.1 (Bravium)"
ID=ubuntu
ID_LIKE=debian
VERSION_ID="26.04"
VERSION="0.8.1 (Bravium; Ubuntu 26.04 base)"
VERSION_CODENAME=resolute
UBUNTU_CODENAME=resolute
HOME_URL="https://github.com"
OS_RELEASE

cat > "$ROOTFS/usr/local/bin/barvium-live-session" <<'SESSION'
#!/bin/sh
[ "$(tty)" = /dev/tty1 ] || exit 0
[ -n "${DISPLAY:-}" ] && exit 0
exec startx
SESSION
chmod 0755 "$ROOTFS/usr/local/bin/barvium-live-session"
cat > "$ROOTFS/etc/profile.d/barvium-live.sh" <<'PROFILE'
if [ "${USER:-}" = barvium ] && [ "$(tty 2>/dev/null)" = /dev/tty1 ]; then
  /usr/local/bin/barvium-live-session
fi
PROFILE
chroot "$ROOTFS" useradd -m -s /bin/bash -G audio,video,plugdev,netdev barvium
# Cosmetic hostname only; no account change on developer host.
printf "bravium\n" > "$ROOTFS/etc/hostname"
cat > "$ROOTFS/etc/hosts" <<'HOSTS'
127.0.0.1 localhost
127.0.1.1 bravium
HOSTS
chroot "$ROOTFS" passwd -l barvium
mkdir -p "$ROOTFS/etc/systemd/system/getty@tty1.service.d"
cat > "$ROOTFS/etc/systemd/system/getty@tty1.service.d/autologin.conf" <<'GETTY'
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin barvium --noclear %I $TERM
GETTY
# No opt-in consent during a live session: deliberately do not install reporter hooks.
chroot "$ROOTFS" apt-get clean
rm -f "$ROOTFS/tmp/install-brave.sh" "$ROOTFS/tmp/privacy.sh" "$ROOTFS/tmp/configure-security.sh" "$ROOTFS/etc/barvium-build-rootfs"
rm -rf "$ROOTFS/var/lib/apt/lists/"*
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
menuentry "Try ${RELEASE_NAME} ${RELEASE_VERSION} (${RELEASE_CODENAME}, live only)" {
  linux /casper/vmlinuz boot=casper quiet splash ---
  initrd /casper/initrd
}
GRUB
echo '[6/7] Assemble BIOS/UEFI ISO (no Secure Boot guarantee)'
grub-mkrescue -o "$ISO" "$IMAGE" -volid OSE8Y6_081
echo '[7/7] Verify ISO GRUB identity'
TMP_GRUB="$(mktemp)"
if ! xorriso -osirrox on -indev "$ISO" -extract /boot/grub/grub.cfg "$TMP_GRUB" >/dev/null 2>&1; then
  rm -f "$TMP_GRUB"
  fail 'Could not read GRUB configuration from generated ISO.'
fi
if ! grep -Fq "Try ${RELEASE_NAME} ${RELEASE_VERSION} (${RELEASE_CODENAME}, live only)" "$TMP_GRUB"; then
  rm -f "$TMP_GRUB"
  fail 'Generated ISO contains unexpected GRUB menu label.'
fi
rm -f "$TMP_GRUB"
echo 'Verified: ISO contains the expected os:e8y6 0.8.1 boot label.'
echo 'ISO produced; it has NOT been boot-tested.' 
sha256sum "$ISO" | tee "$ISO.sha256"
echo "Next: test with QEMU and confirm networking, Brave, and the live login before distribution."
