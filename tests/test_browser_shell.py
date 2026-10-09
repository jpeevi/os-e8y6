from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
class BrowserShellTests(unittest.TestCase):
    def test_alt_f4_power_menu(self):
        root = ET.parse(ROOT/'config/skel/.jwmrc').getroot()
        keys = [x for x in root.findall('Key') if x.attrib.get('mask')=='A' and x.attrib.get('key')=='F4']
        self.assertEqual(len(keys),1)
        self.assertIn('barvium-power-menu',keys[0].text)
    def test_panel_and_main_browser_borderless(self):
        root = ET.parse(ROOT/'config/skel/.jwmrc').getroot()
        self.assertTrue((ROOT/'config/tint2/tint2rc').exists())
        groups = root.findall('Group')
        self.assertTrue(any(g.findtext('Class')=='BarviumMain' and 'noborder' in [x.text for x in g.findall('Option')] for g in groups))
    def test_build_copies_runtime_scripts(self):
        builder = (ROOT/'scripts/build-iso.sh').read_text()
        self.assertIn('barvium-power-menu barvium-open-brave barvium-brave-watchdog', builder)
        self.assertIn('os-e8y6-${RELEASE_VERSION}-amd64.iso', builder)
    def test_network_manager_present(self):
        self.assertIn('network-manager', (ROOT/'packages/base.list').read_text())
        self.assertIn('nmtui', (ROOT/'config/skel/.jwmrc').read_text())
