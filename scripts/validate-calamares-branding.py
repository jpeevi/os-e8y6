#!/usr/bin/env python3
"""Validate Calamares branding/settings in the isolated ISO rootfs.

This checks the structure that previously caused Calamares to abort at startup.
"""
import argparse
from pathlib import Path
import yaml

REQUIRED_STRINGS = ('productName', 'shortProductName', 'version',
                    'shortVersion', 'versionedName', 'shortVersionedName',
                    'bootloaderEntryName')
REQUIRED_BOOL_SETTINGS = ('prompt-install', 'dont-chroot', 'oem-setup',
                          'disable-cancel', 'disable-cancel-during-exec',
                          'hide-back-and-next-during-exec', 'quit-at-end')


def validate(branding_path: Path, settings_path: Path):
    brand = yaml.safe_load(branding_path.read_text(encoding='utf-8'))
    settings = yaml.safe_load(settings_path.read_text(encoding='utf-8'))
    if not isinstance(brand, dict) or not isinstance(settings, dict):
        raise ValueError('Calamares configuration must be YAML mappings')
    if brand.get('componentName') != 'os-e8y6' or settings.get('branding') != 'os-e8y6':
        raise ValueError('Branding component name mismatch')
    strings = brand.get('strings')
    if not isinstance(strings, dict) or any(not isinstance(strings.get(k), str) or not strings[k] for k in REQUIRED_STRINGS):
        raise ValueError('Missing branding strings')
    if strings['productName'] != 'os:e8y6':
        raise ValueError('Public product name must be os:e8y6')
    if brand.get('sidebar') not in ('widget', 'none') or brand.get('navigation') != 'widget':
        raise ValueError('Unsupported Calamares sidebar/navigation settings')
    if not isinstance(brand.get('style'), dict):
        raise ValueError('Missing required Calamares style mapping')
    if not isinstance(brand.get('images'), dict):
        raise ValueError('Missing images mapping')
    for image in brand['images'].values():
        if image and not (branding_path.parent / image).is_file():
            raise ValueError(f'Branding asset does not exist: {image}')
    for key in REQUIRED_BOOL_SETTINGS:
        if not isinstance(settings.get(key), bool):
            raise ValueError(f'Missing/non-boolean Calamares setting: {key}')
    if settings['dont-chroot']:
        raise ValueError('Installer cannot run without chroot')
    if not settings['prompt-install']:
        raise ValueError('Installer requires explicit installation confirmation')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('branding', type=Path)
    p.add_argument('settings', type=Path)
    a = p.parse_args()
    validate(a.branding, a.settings)
    print('Calamares branding and settings valid')


if __name__ == '__main__':
    main()
