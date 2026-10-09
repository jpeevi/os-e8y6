from pathlib import Path
import unittest
R = Path(__file__).resolve().parents[1]
class V081(unittest.TestCase):
    def test_version(self):
        self.assertEqual((R/'VERSION').read_text().strip(), '0.8.1')
    def test_graphical_installer(self):
        t=(R/'scripts/bravium-install').read_text()
        self.assertIn('yad --question',t)
        self.assertIn('systemd-detect-virt',t)
    def test_panel_diagnostics(self):
        t=(R/'scripts/barvium-session').read_text()
        self.assertIn('panel.log',t)
        self.assertIn('tint2 -c',t)
    def test_calam_settings_gate(self):
        self.assertIn('calamares/settings.conf', (R/'scripts/build-iso.sh').read_text())
