import pathlib, unittest
R=pathlib.Path(__file__).resolve().parents[1]
class CoreUpdateTests(unittest.TestCase):
    def test_manual_update_installed(self):
        self.assertIn('e8y6-core-update e8y6-terminal; do',(R/'scripts/build-iso.sh').read_text())
        self.assertTrue((R/'scripts/e8y6-core-update').exists())
    def test_no_unattended_upgrades(self):
        s=(R/'scripts/configure-security-chroot.sh').read_text()
        self.assertIn('Unattended-Upgrade "0"',s)
        self.assertIn('systemctl mask apt-daily.timer apt-daily-upgrade.timer',s)
        self.assertNotIn('systemctl enable apt-daily.timer',s)
    def test_download_integrity(self):
        s=(R/'scripts/e8y6-core-update').read_text()
        self.assertIn('sha256sum -c -',s)
        self.assertIn('dpkg --compare-versions',s)
        self.assertIn('apt-get upgrade -y --with-new-pkgs',s)
        self.assertIn('boot=casper',s)
    def test_browser_pin(self):
        self.assertIn('BROWSER_VERSION=0.1.3-2',(R/'packages/browser-e8y6.lock').read_text())
