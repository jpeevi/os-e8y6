import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class Release07Tests(unittest.TestCase):
    def test_package_list(self):
        packages = (ROOT / 'packages/base.list').read_text().splitlines()
        for package in ('ufw', 'unattended-upgrades', 'qterminal', 'pavucontrol'):
            self.assertIn(package, packages)
        self.assertNotIn('apt-config-auto-update', packages)
    def test_no_live_host_firewall_mutation(self):
        text = (ROOT / 'scripts/configure-security-chroot.sh').read_text()
        self.assertNotIn('ufw --force enable', text)
        self.assertIn('systemctl enable ufw.service', text)
    def test_iso_identity(self):
        script = (ROOT / 'scripts/build-iso.sh').read_text()
        self.assertIn('os-e8y6-${RELEASE_VERSION}-amd64.iso', script)
        self.assertIn('os:e8y6 0.7', script)
    def test_update_policy(self):
        script = (ROOT / 'scripts/configure-security-chroot.sh').read_text()
        self.assertIn('Automatic-Reboot "false"', script)
        self.assertIn('apt-daily-upgrade.timer', script)

    def test_target_release_preflight(self):
        script = (ROOT / 'scripts/build-iso.sh').read_text()
        self.assertIn('Checking target-release package availability', script)
        self.assertIn('chroot "$ROOTFS" apt-cache policy "$pkg"', script)

class GrubIdentityTests(unittest.TestCase):
    def test_grub_label_comes_from_release_metadata(self):
        script = (ROOT / 'scripts/build-iso.sh').read_text()
        self.assertIn('RELEASE_NAME="os:e8y6"', script)
        self.assertIn('RELEASE_VERSION="0.7"', script)
        self.assertIn('RELEASE_CODENAME="Bravium"', script)
        self.assertIn('Try ${RELEASE_NAME} ${RELEASE_VERSION}', script)
        self.assertIn('Generated ISO contains unexpected GRUB menu label', script)

    def test_launcher_supports_new_iso_names(self):
        script = (ROOT / 'run-latest.sh').read_text()
        self.assertIn("-name 'os-e8y6-*.iso'", script)
        self.assertIn("-name 'barvium-*.iso'", script)
        self.assertIn('GRUB boot entry:', script)
