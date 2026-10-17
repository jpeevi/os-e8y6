#!/usr/bin/env bash
# Only modifies the isolated image rootfs; updates are exclusively user initiated.
set -euo pipefail
[[ -f /etc/e8y6-build-rootfs ]] || { echo 'Not an os:e8y6 image build rootfs' >&2; exit 1; }
mkdir -p /etc/apt/apt.conf.d
cat > /etc/apt/apt.conf.d/52ose8y6-updates <<'APT'
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Download-Upgradeable-Packages "0";
APT::Periodic::Unattended-Upgrade "0";
Unattended-Upgrade::Automatic-Reboot "false";
APT
# Mask timers, including any enabled by Ubuntu package presets, in the image.
systemctl mask apt-daily.timer apt-daily-upgrade.timer
