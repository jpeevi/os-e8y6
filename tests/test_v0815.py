import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]

class BrowserIntegration0815(unittest.TestCase):
    def test_pin(self):
        lock = (ROOT/'packages/browser-e8y6.lock').read_text()
        self.assertIn('browser-e8y6_0.1.0-1_amd64.deb',lock)
        self.assertIn('7a3039be1eca331cb590251992aadef842ea958bb13be0cb4961687b5fa575ca',lock)
        self.assertIn('sha256sum -c', (ROOT/'scripts/fetch-browser-package.sh').read_text())
    def test_no_brave_in_build(self):
        self.assertFalse((ROOT/'scripts/install-brave-chroot.sh').exists())
        self.assertFalse((ROOT/'packages/brave.list').exists())
        builder=(ROOT/'scripts/build-iso.sh').read_text()
        self.assertIn('fetch-browser-package.sh',builder)
        self.assertIn('apt-get install -y --no-install-recommends /tmp/browser-e8y6.deb',builder)
        self.assertNotIn('install-brave',builder)
    def test_launch_and_rules(self):
        launcher=(ROOT/'scripts/e8y6-open-browser').read_text()
        self.assertIn('/usr/bin/browser:e8y6',launcher)
        self.assertIn('--profile os-e8y6-main',launcher)
        jwm=ET.parse(ROOT/'config/skel/.jwmrc').getroot()
        self.assertIn('browser:e8y6',[g.findtext('Class') for g in jwm.findall('Group')])
        self.assertIn('e8y6-open-browser',(ROOT/'scripts/e8y6-session').read_text())
    def test_sqlite_driver_is_required_and_verified(self):
        packages = (ROOT/'packages/base.list').read_text().splitlines()
        self.assertIn('libqt6sql6-sqlite', packages)
        builder = (ROOT/'scripts/build-iso.sh').read_text()
        self.assertIn('dpkg-query -W', builder)
        self.assertIn('libqt6sql6-sqlite', builder)
        self.assertIn('libqsqlite[.]so', builder)
        self.assertIn('ldd "$SQLITE_PLUGIN"', builder)

    def test_installer_preserved(self):
        self.assertTrue((ROOT/'config/calamares/settings.conf').exists())
        self.assertEqual((ROOT/'VERSION').read_text().strip(),'0.8.18')
