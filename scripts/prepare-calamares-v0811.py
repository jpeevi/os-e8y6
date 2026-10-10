#!/usr/bin/env python3
"""Small, conservative adaptations of packaged Calamares configuration.

This edits only the isolated ISO rootfs. Existing critical installer jobs are
retained. Extra vendor UI pages and selected vendor-only tasks are removed.
"""
import argparse
import re
from pathlib import Path

# Calamares show steps unrelated to the minimal os:e8y6 installer.
DROP_SHOW = {'pkgselect', 'packages', 'webview', 'webview@lubuntu', 'oemid'}
# Vendor-specific steps, not needed by this minimal Ubuntu-derived system.
DROP_EXEC = {
    'shellprocess@add386arch', 'shellprocess@fixiconkeys_part1',
    'shellprocess@fixiconkeys_part2', 'shellprocess@bug-LP#1829805',
    'shellprocess@oemprep', 'shellprocess@fix-oem-uid',
    'pkgselectprocess', 'packages',
    'shellprocess@fixconkeys_part1', 'shellprocess@fixconkeys_part2',
    'contextualprocess@pkgselect_action',
    'contextualprocess@pkgselect_snap_action',
}
REQUIRED_SHOW = {'welcome', 'locale', 'keyboard', 'partition', 'users', 'summary'}
REQUIRED_EXEC = {'partition', 'mount', 'unpackfs', 'fstab', 'users', 'initramfs', 'bootloader'}


def adapt_settings(text: str) -> str:
    section = None
    steps = {'show': set(), 'exec': set()}
    result = []
    branding_seen = False
    sequence_started = False
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        if re.match(r'^sequence\s*:', line):
            sequence_started = True
        elif sequence_started and line and not line[0].isspace() and ':' in line and not line.startswith('-'):
            section = None
            sequence_started = False
        match = re.match(r'^\s*-\s*(show|exec)\s*:\s*$', line)
        if sequence_started and match:
            section = match.group(1)
            result.append(line)
            continue
        step = re.match(r'^\s*-\s*([A-Za-z0-9_@#.-]+)\s*(?:#.*)?$', line)
        if sequence_started and step and section:
            name = step.group(1)
            if name in (DROP_SHOW if section == 'show' else DROP_EXEC):
                continue
            steps[section].add(name)
        if re.match(r'^branding\s*:', line):
            line = 'branding: os-e8y6\n'
            branding_seen = True
        result.append(line)
    if not branding_seen:
        result.append('branding: os-e8y6\n')
    for phase, required in [('show', REQUIRED_SHOW), ('exec', REQUIRED_EXEC)]:
        absent = required - steps[phase]
        if absent:
            raise ValueError(f'Missing required Calamares {phase} modules: {sorted(absent)}')
    updated = ''.join(result)
    # Calamares 3.3 expects these boolean keys. Preserve packaged values when present.
    required_booleans = {
        'prompt-install': 'true',
        'dont-chroot': 'false',
        'oem-setup': 'false',
        'disable-cancel': 'false',
        'disable-cancel-during-exec': 'false',
        'hide-back-and-next-during-exec': 'true',
        'quit-at-end': 'false',
    }
    for key, default in required_booleans.items():
        if not re.search(r'^' + re.escape(key) + r'\s*:', updated, re.MULTILINE):
            updated += f'{key}: {default}\n'
    return updated


def fix_cleanup(content: str) -> str:
    # Only relax removal of the optional cdrom APT source; leave other commands alone.
    return re.sub(r'(?<![\w-])rm\s+(?!-[^\s]*f)(?=[^\n]*cdrom\.sources)', 'rm -f ', content)


def replace_log_helper(content: str) -> str:
    return content.replace('calamares-logs-helper', 'os-e8y6-installer-logs')


def prepare(rootfs: Path) -> None:
    cfg = rootfs / 'etc/calamares'
    settings = cfg / 'settings.conf'
    if not settings.is_file():
        raise ValueError('settings.conf missing')
    settings.write_text(adapt_settings(settings.read_text(encoding='utf-8')), encoding='utf-8')
    changed = []
    for folder in (cfg / 'modules', rootfs / 'usr/share/calamares/modules'):
        if not folder.is_dir():
            continue
        for filename in folder.glob('*.conf'):
            text = filename.read_text(encoding='utf-8')
            updated = replace_log_helper(fix_cleanup(text))
            if updated != text:
                filename.write_text(updated, encoding='utf-8')
                changed.append(str(filename.relative_to(rootfs)))
    print('Installer cleanup/logging modules adjusted in:', ', '.join(changed) or 'none (no matching jobs)')
    # Verify that an existing Calamares log job points to the safe replacement.
    log_jobs = [f for folder in (cfg / 'modules', rootfs / 'usr/share/calamares/modules')
                if folder.is_dir() for f in folder.glob('*.conf')
                if 'os-e8y6-installer-logs' in f.read_text(encoding='utf-8')]
    if not log_jobs:
        raise ValueError('No Calamares log helper job was rewritten; inspect packaged configuration')
    # Abort if references remain in text-based module configurations.
    for folder in (cfg / 'modules', rootfs / 'usr/share/calamares/modules'):
        if folder.is_dir():
            for filename in folder.glob('*.conf'):
                for line in filename.read_text(encoding='utf-8').splitlines():
                    if 'cdrom.sources' in line and re.search(r'\brm\s+(?!-[^\s]*f)', line):
                        raise ValueError(f'Unsafe cdrom.sources deletion remains in {filename}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('rootfs', type=Path)
    prepare(p.parse_args().rootfs)


if __name__ == '__main__':
    main()
