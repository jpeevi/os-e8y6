import pathlib, unittest, xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parents[1]
class BrandingControls(unittest.TestCase):
    def test_release(self): self.assertEqual((ROOT/'VERSION').read_text().strip(), '0.8.18')
    def test_jwm_keys(self):
        r=ET.parse(ROOT/'config/skel/.jwmrc').getroot()
        keys={(x.attrib.get('mask'),x.attrib.get('key')):x.text for x in r.findall('Key')}
        self.assertIn('e8y6-power-menu', keys['A','F4'])
        self.assertIn('e8y6-lock', keys['4','l'])
    def test_installer_commands(self):
        s=(ROOT/'scripts/build-iso.sh').read_text()
        for cmd in ['e8y6-install','e8y6-calamares-root','e8y6-live-installer-enable']:
            self.assertIn(cmd,s)
    def test_browser_and_installer_untouched(self):
        s=(ROOT/'scripts/build-iso.sh').read_text()
        self.assertIn('prepare-calamares-v0811.py',s)
        self.assertIn('fetch-browser-package.sh',s)
    def test_branding_asset(self):
        ET.parse(ROOT/'config/calamares/branding/wordmark.svg')
        self.assertTrue((ROOT/'config/branding/lockscreen.png').stat().st_size>10000)
    def test_no_legacy_runtime_commands(self):
        s=(ROOT/'scripts/build-iso.sh').read_text()
        self.assertNotIn('bravium-',s)
        self.assertNotIn('barvium-',s)
