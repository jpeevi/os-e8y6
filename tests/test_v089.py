import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class InstallerDependencies089(unittest.TestCase):
    def test_release_version(self):
        self.assertEqual((ROOT / 'VERSION').read_text().strip(), '0.8.13')

    def test_rsync_is_required(self):
        packages = (ROOT / 'packages/base.list').read_text().splitlines()
        self.assertIn('rsync', packages)
        self.assertIn('calamares', packages)
        self.assertIn('squashfs-tools', packages)

    def test_build_checks_live_installer_executables(self):
        script = (ROOT / 'scripts/build-iso.sh').read_text()
        self.assertIn('for installer_tool in rsync unsquashfs calamares', script)
        self.assertIn('chroot "$ROOTFS" /usr/bin/env sh', script)
        self.assertIn('Missing required installer executable in image', script)

    def test_installer_keeps_correct_squashfs_source(self):
        conf = (ROOT / 'config/calamares/unpackfs.conf').read_text()
        self.assertIn('/cdrom/casper/filesystem.squashfs', conf)
        self.assertNotIn('minimal.squashfs', conf)
