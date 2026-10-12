#!/usr/bin/env bash
# os:e8y6 early-development tool. No system package removal or ISO construction.
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
STAGING_DIR="$ROOT_DIR/out/staging"
VERSION="$(cat "$ROOT_DIR/VERSION")"

usage() {
  cat <<USAGE
os:e8y6 $VERSION — experimental live ISO builder

Usage: ./build.sh <command>

  version Print release version
  check   Validate the project scaffold and XML configuration
  stage   Prepare a filesystem overlay and metadata under out/staging/
  iso     Build experimental live ISO (requires sudo and host tools)
  help    Show this message

The iso command needs sudo; check and stage do not.
Experimental Calamares installer is VM-restricted; no physical-disk installation is supported.
USAGE
}

check_project() {
  local file
  for file in \
    "$ROOT_DIR/config/skel/.xinitrc" \
    "$ROOT_DIR/config/skel/.profile" \
    "$ROOT_DIR/config/skel/.jwmrc" \
    "$ROOT_DIR/config/etc/issue" \
    "$ROOT_DIR/config/calamares/unpackfs.conf" \
    "$ROOT_DIR/config/calamares/settings.conf" \
    "$ROOT_DIR/config/calamares/modules/shellprocess-kernel.conf" \
    "$ROOT_DIR/config/calamares/modules/shellprocess-installed-session.conf" \
    "$ROOT_DIR/config/calamares/modules/shellprocess-logs.conf" \
    "$ROOT_DIR/config/calamares/initramfs.conf" \
    "$ROOT_DIR/scripts/prepare-calamares-settings.py" \
    "$ROOT_DIR/scripts/prepare-calamares-v0811.py" \
    "$ROOT_DIR/scripts/integrate-installed-session.py" \
    "$ROOT_DIR/scripts/validate-installer.py" \
    "$ROOT_DIR/scripts/validate-calamares-branding.py" \
    "$ROOT_DIR/config/calamares/branding/branding.desc" \
    "$ROOT_DIR/config/calamares/branding/wordmark.svg" \
    "$ROOT_DIR/config/branding/lockscreen.png" \
    "$ROOT_DIR/config/gtk/3.0/settings.ini" \
    "$ROOT_DIR/config/fontconfig/fonts.conf" \
    "$ROOT_DIR/scripts/e8y6-power-menu" \
    "$ROOT_DIR/scripts/e8y6-lock" \
    "$ROOT_DIR/config/zram/zram-generator.conf" \
    "$ROOT_DIR/scripts/validate-calamares-unpack.py" "$ROOT_DIR/scripts/validate-calamares-branding.py" \
    "$ROOT_DIR/packages/base.list" \
    "$ROOT_DIR/packages/browser-e8y6.lock" \
    "$ROOT_DIR/scripts/fetch-browser-package.sh" \
    "$ROOT_DIR/scripts/configure-security-chroot.sh" \
    "$ROOT_DIR/privacy/remove-optional-reporting-chroot.sh" \
    "$ROOT_DIR/telemetry/client.py" \
    "$ROOT_DIR/server/app.py" \
    "$ROOT_DIR/AGENTS.md" \
    "$ROOT_DIR/scripts/build-iso.sh" \
    "$ROOT_DIR/scripts/e8y6-open-browser" \
    "$ROOT_DIR/scripts/e8y6-install" \
    "$ROOT_DIR/scripts/e8y6-session" \
    "$ROOT_DIR/scripts/e8y6-calamares-root" \
    "$ROOT_DIR/scripts/e8y6-live-installer-enable" \
    "$ROOT_DIR/config/polkit/org.os-e8y6.live-install.policy" \
    "$ROOT_DIR/config/polkit/49-e8y6-live-installer.rules"; do
    if [[ ! -f "$file" ]]; then
      printf 'Missing project file: %s\n' "$file" >&2
      exit 1
    fi
  done
  bash -n "$ROOT_DIR/build.sh" "$ROOT_DIR/scripts/build-iso.sh" \
    "$ROOT_DIR/scripts/fetch-browser-package.sh" \
    "$ROOT_DIR/scripts/configure-security-chroot.sh" \
    "$ROOT_DIR/privacy/remove-optional-reporting-chroot.sh" \
    "$ROOT_DIR/scripts/e8y6-install" "$ROOT_DIR/scripts/e8y6-calamares-root"
  sh -n "$ROOT_DIR/scripts/e8y6-session" \
    "$ROOT_DIR/scripts/e8y6-open-browser" \
    "$ROOT_DIR/config/skel/.xinitrc" \
    "$ROOT_DIR/config/skel/.profile" \
    "$ROOT_DIR/scripts/e8y6-live-installer-enable"
  python3 -m py_compile "$ROOT_DIR/scripts/e8y6-power-menu" "$ROOT_DIR/telemetry/client.py" "$ROOT_DIR/server/app.py" "$ROOT_DIR/scripts/validate-calamares-unpack.py" "$ROOT_DIR/scripts/validate-calamares-branding.py"
  sh -n "$ROOT_DIR/config/skel/.xinitrc"

  python3 - "$ROOT_DIR/config/skel/.jwmrc" "$ROOT_DIR/config/polkit/org.os-e8y6.live-install.policy" <<'PYXML'
import sys, xml.etree.ElementTree as ET
for filename in sys.argv[1:]: ET.parse(filename)
print('JWM and polkit XML: valid')
PYXML
  echo 'os:e8y6 scaffold: checks passed.'
}

stage_project() {
  check_project
  # Stages files only in this project tree; never changes host /etc or /usr.
  install -D -m 0644 "$ROOT_DIR/config/skel/.jwmrc" \
    "$STAGING_DIR/rootfs-overlay/etc/skel/.jwmrc"
  install -D -m 0755 "$ROOT_DIR/config/skel/.xinitrc" \
    "$ROOT_DIR/config/skel/.profile" \
    "$STAGING_DIR/rootfs-overlay/etc/skel/.xinitrc"
  install -D -m 0644 "$ROOT_DIR/config/etc/issue" \
    "$STAGING_DIR/rootfs-overlay/etc/issue"
  install -D -m 0644 "$ROOT_DIR/packages/base.list" \
    "$STAGING_DIR/package-lists/base.list"
  install -D -m 0644 "$ROOT_DIR/packages/browser-e8y6.lock" \
    "$STAGING_DIR/package-lists/browser-e8y6.lock"
  install -D -m 0755 "$ROOT_DIR/scripts/fetch-browser-package.sh" \
    "$STAGING_DIR/build-hooks/fetch-browser-package.sh"
  install -D -m 0755 "$ROOT_DIR/scripts/configure-security-chroot.sh" \
    "$STAGING_DIR/build-hooks/configure-security-chroot.sh"
  install -D -m 0755 "$ROOT_DIR/privacy/remove-optional-reporting-chroot.sh" \
    "$STAGING_DIR/build-hooks/remove-optional-reporting-chroot.sh"
  install -D -m 0755 "$ROOT_DIR/telemetry/client.py" \
    "$STAGING_DIR/optional-features/install-counter-client.py"
  install -D -m 0644 "$ROOT_DIR/AGENTS.md" \
    "$STAGING_DIR/docs/AGENTS.md"
  echo 'Staged project files in out/staging/.'
  echo 'No ISO generated and no host packages modified.'
}

printf "\n=== os:e8y6 | v%s | %s ===\n" "$VERSION" "${1:-help}"
case "${1:-help}" in
  version) printf "%s\n" "$VERSION" ;;
  check) check_project ;;
  stage) stage_project ;;
  iso) check_project; exec "$ROOT_DIR/scripts/build-iso.sh" ;;
  help|-h|--help) usage ;;
  *) printf 'Unknown command: %s\n\n' "$1" >&2; usage >&2; exit 2 ;;
esac
