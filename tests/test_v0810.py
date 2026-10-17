import importlib.util
import tempfile
import unittest
from pathlib import Path

R = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('settingsprep', R/'scripts/prepare-calamares-settings.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class InstallerAudit0810(unittest.TestCase):
    def test_release(self):
        self.assertEqual((R/'VERSION').read_text().strip(), '0.8.19')

    def test_dependencies(self):
        packages = (R/'packages/base.list').read_text().splitlines()
        for name in ('rsync','squashfs-tools','parted','e2fsprogs','dosfstools','grub2-common','grub-efi-amd64-bin','efibootmgr','initramfs-tools'):
            self.assertIn(name, packages)
        self.assertNotIn('dracut', packages)

    def test_adapt_sequence(self):
        original = 'sequence:\n- show:\n  - welcome\n- exec:\n  - unpackfs\n  - dracutlukscfg\n  - dracut\n  - bootloader\nbranding: default\n'
        updated = mod.adapt(original)
        self.assertIn('  - initramfs\n', updated)
        self.assertNotIn('  - dracut\n', updated)
        self.assertNotIn('dracutlukscfg', updated)
        self.assertIn('  - bootloader\n', updated)

    def test_unrecognized_sequence_rejected(self):
        with self.assertRaises(ValueError):
            mod.adapt('sequence:\n  - unpackfs\n  - bootloader\n')

    def test_installer_checks(self):
        script = (R/'scripts/build-iso.sh').read_text()
        self.assertIn('prepare-calamares-settings.py', script)
        self.assertIn('mkfs.vfat', script)
        self.assertIn('update-initramfs', script)
