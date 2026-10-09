#!/usr/bin/env python3
"""Optional, manual, one-time anonymous install completion report.
No import-time side effects, persistent IDs, machine identifiers, or background timers.
"""
import argparse
import json
import os
from pathlib import Path
import urllib.request

ALLOWED_VERSIONS = {"0.3.0-dev"}

def report(endpoint: str, version: str, marker: Path) -> str:
    if version not in ALLOWED_VERSIONS:
        raise ValueError("Unsupported Barvium version")
    if not endpoint.startswith("https://"):
        raise ValueError("HTTPS endpoint required")
    if marker.exists():
        return "Already reported on this installation; nothing sent."
    payload = json.dumps({"event": "install_completed", "version": version}).encode("utf-8")
    req = urllib.request.Request(endpoint.rstrip("/") + "/v1/install", data=payload,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=10) as response:
        if response.status != 204:
            raise RuntimeError(f"Unexpected response status: {response.status}")
    marker.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    marker.touch(mode=0o600, exist_ok=True)
    return "Optional install event sent."

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint", required=True, help="your HTTPS server origin, e.g. https://stats.example.org")
    parser.add_argument("--version", default="0.3.0-dev")
    parser.add_argument("--consent", action="store_true", help="explicitly authorize sending the event")
    parser.add_argument("--marker", type=Path, default=Path.home() / ".local/state/barvium/install-reported")
    args = parser.parse_args()
    print('Data: {"event":"install_completed","version":"%s"}' % args.version)
    print("Your server may see your public IP while you connect; no hardware identifiers are sent.")
    if not args.consent:
        print("No request sent. Re-run with --consent only if you agree.")
        return
    print(report(args.endpoint, args.version, args.marker))

if __name__ == "__main__":
    main()
