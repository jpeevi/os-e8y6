import tempfile
import unittest
from pathlib import Path
import importlib.util

R = Path(__file__).resolve().parents[1]

class Minimal088(unittest.TestCase):
    def test_clean_package_set(self):
        packages = set((R/'packages/base.list').read_text().splitlines())
        for package in ('ufw', 'pavucontrol', 'htop', 'btop', 'xfce4-panel', 'tint2', 'thunar', 'pcmanfm'):
            self.assertNotIn(package, packages)
        for package in ('jwm', 'qterminal', 'calamares', 'squashfs-tools', 'systemd-zram-generator'):
            self.assertIn(package, packages)
    def test_zram_settings(self):
        z = (R/'config/zram/zram-generator.conf').read_text()
        self.assertIn('zram-size = ram / 2', z)
        self.assertIn('compression-algorithm = zstd', z)
    def test_installer_staged_from_own_config(self):
        b = (R/'scripts/build-iso.sh').read_text()
        self.assertIn('config/calamares/unpackfs.conf', b)
        self.assertIn('validate-calamares-unpack.py', b)
        self.assertIn('config/zram/zram-generator.conf', b)
    def test_single_squashfs_references(self):
        conf = (R/'config/calamares/unpackfs.conf').read_text()
        self.assertIn('/cdrom/casper/filesystem.squashfs', conf)
        self.assertNotIn('minimal.squashfs', conf)
    def test_squashfs_validator(self):
        spec = importlib.util.spec_from_file_location('unpack_validator', R/'scripts/validate-calamares-unpack.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as d:
            image = Path(d)
            (image/'casper').mkdir()
            (image/'casper/filesystem.squashfs').write_bytes(b'mock')
            module.validate(R/'config/calamares/unpackfs.conf', image)
            (image/'casper/filesystem.squashfs').unlink()
            with self.assertRaises(FileNotFoundError):
                module.validate(R/'config/calamares/unpackfs.conf', image)
