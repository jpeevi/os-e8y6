#!/usr/bin/env bash
# Fetch only the pinned, checksum-verified browser release to an isolated build cache.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=../packages/browser-e8y6.lock
source "$ROOT/packages/browser-e8y6.lock"
CACHE="${1:?Usage: fetch-browser-package.sh CACHE_DIRECTORY}"
mkdir -p "$CACHE"
TARGET="$CACHE/browser-e8y6_${BROWSER_VERSION}_amd64.deb"
if [[ -f "$TARGET" ]] && echo "$BROWSER_SHA256  $TARGET" | sha256sum -c --status; then
  echo "$TARGET"; exit 0
fi
rm -f "$TARGET"
TEMP="$(mktemp "$CACHE/.browser-e8y6.XXXXXXXX")"
trap 'rm -f "$TEMP"' EXIT
curl --fail --location --retry 3 --silent --show-error --output "$TEMP" "$BROWSER_URL"
echo "$BROWSER_SHA256  $TEMP" | sha256sum -c --status || { echo 'Browser SHA-256 mismatch' >&2; exit 1; }
[[ "$(dpkg-deb -f "$TEMP" Package)" == browser-e8y6 ]] || exit 1
[[ "$(dpkg-deb -f "$TEMP" Version)" == "$BROWSER_VERSION" ]] || exit 1
[[ "$(dpkg-deb -f "$TEMP" Architecture)" == amd64 ]] || exit 1
mv "$TEMP" "$TARGET"
echo "$TARGET"
