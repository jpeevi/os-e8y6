#!/usr/bin/env bash
# FUTURE USE ONLY: run INSIDE a Barvium build chroot, NEVER on the host.
set -euo pipefail

if (( EUID != 0 )) || [[ "${BARVIUM_BUILD_CHROOT:-}" != "yes" ]]; then
  echo 'Refusing to run: must be root inside a dedicated build chroot with BARVIUM_BUILD_CHROOT=yes.' >&2
  exit 1
fi

if ! command -v apt-get >/dev/null 2>&1; then
  echo 'This hook requires an Ubuntu/Debian APT build root.' >&2
  exit 1
fi

# Official Brave key and deb822 repository instructions:
# https://brave.com/linux/
install -d -m 0755 /usr/share/keyrings /etc/apt/sources.list.d
curl --fail --silent --show-error --location \
  https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg \
  --output /usr/share/keyrings/brave-browser-archive-keyring.gpg
curl --fail --silent --show-error --location \
  https://brave-browser-apt-release.s3.brave.com/brave-browser.sources \
  --output /etc/apt/sources.list.d/brave-browser-release.sources
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends brave-browser
