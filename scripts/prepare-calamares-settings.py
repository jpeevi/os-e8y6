#!/usr/bin/env python3
"""Adapt a packaged Calamares sequence to Ubuntu initramfs-tools.

Never silently fabricate a full installer sequence: fail when the provided
configuration does not contain the expected exec-phase Dracut module.
"""
import argparse
import re
from pathlib import Path

ITEM = re.compile(r'^(\s*)-\s+([\w@-]+)\s*(?:#.*)?$')


def adapt(text: str) -> str:
    lines = text.splitlines(keepends=True)
    active = False
    out = []
    replaced = 0
    has_initramfs = False
    for line in lines:
        raw = line.lstrip()
        if raw.startswith('#'):
            out.append(line)
            continue
        if re.match(r'^sequence\s*:', line):
            active = True
        elif active and line and not line[0].isspace() and not line.startswith('-') and ':' in line:
            active = False
        match = ITEM.match(line.rstrip('\n')) if active else None
        if match and match.group(2) == 'initramfs':
            has_initramfs = True
        if match and match.group(2) == 'dracutlukscfg':
            continue
        if match and match.group(2) == 'dracut':
            replaced += 1
            out.append(f'{match.group(1)}- initramfs\n')
            continue
        out.append(line)
    if replaced != 1:
        raise ValueError(f'Expected exactly one active dracut job, found {replaced}; inspect packaged settings.conf')
    if has_initramfs:
        raise ValueError('initramfs job already active; refusing to insert a duplicate')
    updated = ''.join(out)
    if 'sequence:' not in updated or 'unpackfs' not in updated or 'bootloader' not in updated:
        raise ValueError('Missing required Calamares sequence landmarks')
    return updated


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('settings', type=Path)
    args = parser.parse_args()
    source = args.settings.read_text(encoding='utf-8')
    args.settings.write_text(adapt(source), encoding='utf-8')


if __name__ == '__main__':
    main()
