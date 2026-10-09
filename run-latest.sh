#!/usr/bin/env bash
# Launch the newest os:e8y6/legacy Barvium live ISO with a QEMU monitor.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DIST="$ROOT/dist"

if (( EUID == 0 )); then
  echo 'Do not run QEMU as root. Run: ./run-latest.sh' >&2
  exit 1
fi
command -v qemu-system-x86_64 >/dev/null || {
  echo 'QEMU missing: sudo apt install qemu-system-x86' >&2
  exit 1
}
[[ -d "$DIST" ]] || { echo "No dist/ directory. Build an ISO first." >&2; exit 1; }

# Find by modification time and support spaces in paths.
LATEST=''
while IFS= read -r -d '' f; do
  LATEST="$f"
  break
done < <(find "$DIST" -maxdepth 1 -type f \( -name 'os-e8y6-*.iso' -o -name 'barvium-*.iso' \) -printf '%T@ %p\0' \
  | sort -z -nr | cut -z -d' ' -f2-)
[[ -n "$LATEST" ]] || { echo 'No os-e8y6-*.iso or barvium-*.iso found in dist/' >&2; exit 1; }
[[ -r "$LATEST" ]] || {
  echo "ISO not readable as your user: $LATEST" >&2
  echo 'Check permissions. If this ISO was built by root, use:' >&2
  echo "  sudo chmod a+r -- '$LATEST'" >&2
  exit 1
}

ACCEL=(-accel tcg)
if [[ -c /dev/kvm && -r /dev/kvm && -w /dev/kvm ]]; then
  ACCEL=(-enable-kvm)
else
  echo 'KVM unavailable to your user; using slower software emulation.'
  echo 'Check: ls -l /dev/kvm ; id -nG'
  echo 'For KVM access, your user may need membership in the kvm group.'
fi

echo "Selected ISO: $LATEST"
# Inspect the real boot menu embedded in the ISO, not just its filename.
if command -v xorriso >/dev/null 2>&1; then
  cfg="$(mktemp)"
  trap 'rm -f "$cfg"' EXIT
  if xorriso -osirrox on -indev "$LATEST" -extract /boot/grub/grub.cfg "$cfg" >/dev/null 2>&1; then
    echo 'GRUB boot entry:'
    grep -m 1 '^[[:space:]]*menuentry ' "$cfg" || true
  else
    echo 'Warning: unable to inspect GRUB boot menu in ISO.' >&2
  fi
  rm -f "$cfg"
  trap - EXIT
fi

echo 'When shutdown says "remove installation medium":'
echo '  1. In THIS terminal (QEMU monitor), type: eject -f barviumcd'
echo '  2. Click the VM window and press Enter.'
echo '  3. After shutdown, QEMU should exit.'
echo 'Type "info block" in the monitor to inspect media state.'

exec qemu-system-x86_64 \
  -m 4096 -smp 2 "${ACCEL[@]}" \
  -drive "file=$LATEST,if=ide,index=2,media=cdrom,readonly=on,id=barviumcd" \
  -boot order=d \
  -monitor stdio
