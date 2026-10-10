#!/usr/bin/env bash
# Configures the isolated IMAGE, not the running build host. Do not call `ufw enable` inside a chroot.
set -euo pipefail
[[ -f /etc/barvium-build-rootfs ]] || { echo 'Not a Barvium image build rootfs' >&2; exit 1; }
# No UFW package or default firewall policy in v0.8.8.
# Prevent unattended restarts; APT timers installed by distro use native systemd scheduling.
mkdir -p /etc/apt/apt.conf.d
cat > /etc/apt/apt.conf.d/52ose8y6-updates <<'APT'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
Unattended-Upgrade::Automatic-Reboot "false";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
APT
# Ubuntu security/updates are handled by the distro defaults. Include the signed Brave
# repository by matching its apt source site (validate actual apt policy in the guest).
cat > /etc/apt/apt.conf.d/53ose8y6-brave-updates <<'APT'
Unattended-Upgrade::Origins-Pattern { "site=brave-browser-apt-release.s3.brave.com"; };
APT
systemctl enable apt-daily.timer apt-daily-upgrade.timer
