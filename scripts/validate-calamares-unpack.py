#!/usr/bin/env python3
"""Validate os:e8y6's single-squashfs Calamares source against staged ISO files."""
import pathlib
import re
import sys


def validate(config: pathlib.Path, iso_tree: pathlib.Path) -> None:
    body = config.read_text()
    entries = re.findall(r'^\s*-\s*source:\s*["\']?([^"\'\s]+)', body, re.M)
    if len(entries) != 1:
        raise ValueError(f"Expected exactly one Calamares unpack source, found {len(entries)}")
    if not re.search(r'^\s*sourcefs:\s*["\']?squashfs', body, re.M):
        raise ValueError("Calamares unpack source must use squashfs")
    source = entries[0]
    if not source.startswith('/cdrom/casper/'):
        raise ValueError(f"Unexpected Calamares source: {source}")
    staged = iso_tree / source.removeprefix('/cdrom/')
    if not staged.is_file():
        raise FileNotFoundError(f"Calamares source missing in staged ISO: {staged}")
    print(f"Verified installer source: {source}")


if __name__ == '__main__':
    try:
        validate(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))
    except (ValueError, FileNotFoundError, OSError, IndexError) as exc:
        sys.exit(f"ERROR: {exc}")
