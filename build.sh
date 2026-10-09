#!/usr/bin/env bash
# Barvium early-development tool. No system package removal or ISO construction.
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
STAGING_DIR="$ROOT_DIR/out/staging"
VERSION="0.7.0-dev"

usage() {
  cat <<USAGE
os:e8y6 $VERSION (Bravium) — experimental live ISO builder

Usage: ./build.sh <command>

  check   Validate the project scaffold and XML configuration
  stage   Prepare a filesystem overlay and metadata under out/staging/
  iso     Build experimental live ISO (requires sudo and host tools)
  help    Show this message

The iso command needs sudo; check and stage do not.
This is a live ISO only; there is no disk installer.
USAGE
}

check_project() {
  local file
  for file in \
    "$ROOT_DIR/config/skel/.xinitrc" \
    "$ROOT_DIR/config/skel/.jwmrc" \
    "$ROOT_DIR/config/etc/issue" \
    "$ROOT_DIR/packages/base.list" \
    "$ROOT_DIR/packages/brave.list" \
    "$ROOT_DIR/scripts/install-brave-chroot.sh" \
    "$ROOT_DIR/scripts/configure-security-chroot.sh" \
    "$ROOT_DIR/privacy/remove-optional-reporting-chroot.sh" \
    "$ROOT_DIR/telemetry/client.py" \
    "$ROOT_DIR/server/app.py" \
    "$ROOT_DIR/PRIVACY.md" \
    "$ROOT_DIR/scripts/build-iso.sh" \
    "$ROOT_DIR/scripts/barvium-power-menu" \
    "$ROOT_DIR/scripts/barvium-open-brave" \
    "$ROOT_DIR/scripts/barvium-brave-watchdog" \
    "$ROOT_DIR/scripts/barvium-session" \
    "$ROOT_DIR/scripts/barvium-net-speed" \
    "$ROOT_DIR/scripts/barvium-webapp-menu" \
    "$ROOT_DIR/config/tint2/tint2rc"; do
    if [[ ! -f "$file" ]]; then
      printf 'Missing project file: %s\n' "$file" >&2
      exit 1
    fi
  done

  bash -n "$ROOT_DIR/build.sh" "$ROOT_DIR/scripts/build-iso.sh" "$ROOT_DIR/scripts/install-brave-chroot.sh" "$ROOT_DIR/scripts/configure-security-chroot.sh" "$ROOT_DIR/privacy/remove-optional-reporting-chroot.sh" \
    "$ROOT_DIR/scripts/barvium-power-menu" \
    "$ROOT_DIR/scripts/barvium-open-brave" \
    "$ROOT_DIR/scripts/barvium-brave-watchdog" \
    "$ROOT_DIR/scripts/barvium-session"
  python3 -m py_compile "$ROOT_DIR/telemetry/client.py" "$ROOT_DIR/server/app.py"
  python3 -m py_compile "$ROOT_DIR/scripts/barvium-net-speed" "$ROOT_DIR/scripts/barvium-webapp-menu"
  sh -n "$ROOT_DIR/config/skel/.xinitrc"

  if command -v python3 >/dev/null 2>&1; then
    python3 - "$ROOT_DIR/config/skel/.jwmrc" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
if root.tag != 'JWM':
    raise SystemExit('Expected top-level <JWM> element')
print('JWM XML: valid')
PY
  else
    echo 'python3 is required to validate the JWM XML.' >&2
    exit 1
  fi

  if command -v jwm >/dev/null 2>&1; then
    # -p uses JWM's own configuration validation; available if installed locally.
    jwm -p -f "$ROOT_DIR/config/skel/.jwmrc"
  else
    echo 'JWM parser check skipped (JWM is not installed on the build host).'
  fi
  echo 'os:e8y6 scaffold: checks passed.'
}

stage_project() {
  check_project
  # Stages files only in this project tree; never changes host /etc or /usr.
  install -D -m 0644 "$ROOT_DIR/config/skel/.jwmrc" \
    "$STAGING_DIR/rootfs-overlay/etc/skel/.jwmrc"
  install -D -m 0755 "$ROOT_DIR/config/skel/.xinitrc" \
    "$STAGING_DIR/rootfs-overlay/etc/skel/.xinitrc"
  install -D -m 0644 "$ROOT_DIR/config/etc/issue" \
    "$STAGING_DIR/rootfs-overlay/etc/issue"
  install -D -m 0644 "$ROOT_DIR/packages/base.list" \
    "$STAGING_DIR/package-lists/base.list"
  install -D -m 0644 "$ROOT_DIR/packages/brave.list" \
    "$STAGING_DIR/package-lists/brave.list"
  install -D -m 0755 "$ROOT_DIR/scripts/install-brave-chroot.sh" \
    "$STAGING_DIR/build-hooks/install-brave-chroot.sh"
  install -D -m 0755 "$ROOT_DIR/scripts/configure-security-chroot.sh" \
    "$STAGING_DIR/build-hooks/configure-security-chroot.sh"
  install -D -m 0755 "$ROOT_DIR/privacy/remove-optional-reporting-chroot.sh" \
    "$STAGING_DIR/build-hooks/remove-optional-reporting-chroot.sh"
  install -D -m 0755 "$ROOT_DIR/telemetry/client.py" \
    "$STAGING_DIR/optional-features/install-counter-client.py"
  install -D -m 0644 "$ROOT_DIR/PRIVACY.md" \
    "$STAGING_DIR/docs/PRIVACY.md"
  echo 'Staged project files in out/staging/.'
  echo 'No ISO generated and no host packages modified.'
}

case "${1:-help}" in
  check) check_project ;;
  stage) stage_project ;;
  iso) check_project; exec "$ROOT_DIR/scripts/build-iso.sh" ;;
  help|-h|--help) usage ;;
  *) printf 'Unknown command: %s\n\n' "$1" >&2; usage >&2; exit 2 ;;
esac
