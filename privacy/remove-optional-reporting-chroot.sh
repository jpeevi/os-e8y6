#!/usr/bin/env bash
# Run ONLY inside an isolated Barvium build rootfs, never on the development host.
set -euo pipefail
if [[ ! -f /etc/barvium-build-rootfs ]]; then
  echo 'Refusing to modify system: missing /etc/barvium-build-rootfs build marker.' >&2
  exit 1
fi
if [[ ! -f /etc/debian_version ]]; then
  echo 'Not an Ubuntu/Debian root filesystem.' >&2; exit 1
fi
export DEBIAN_FRONTEND=noninteractive
# Best effort: package names differ by Ubuntu image and some may not be installed.
for pkg in ubuntu-report ubuntu-insights whoopsie apport popularity-contest; do
  if dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null | grep -qx 'install ok installed'; then
    apt-get purge -y "$pkg"
  fi
done
# Default-off crash reporting, even if apport returns as a dependency.
mkdir -p /etc/default
printf 'enabled=0\n' > /etc/default/apport
printf 'Optional reporting components removed or disabled where installed.\n'
