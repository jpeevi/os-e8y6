import pathlib, unittest, xml.etree.ElementTree as ET
ROOT = pathlib.Path(__file__).resolve().parents[1]
class WindowPowerLock0818(unittest.TestCase):
    def test_power_title_and_no_heading(self):
        s=(ROOT/'scripts/e8y6-power-menu').read_text()
        self.assertIn("title='Power'", s)
        self.assertNotIn("Gtk.Label(label='os:e8y6')",s)
        self.assertIn('fcntl.flock',s)
    def test_lock_auth_and_livecd_guard(self):
        s=(ROOT/'scripts/e8y6-lock').read_text()
        self.assertIn('boot=casper',s)
        self.assertIn("'/usr/bin/i3lock'", s)
        self.assertIn("'-n', '-u', '-i'", s)
        self.assertNotIn('passwd -',s)
    def test_window_groups_and_shortcuts(self):
        r=ET.parse(ROOT/'config/skel/.jwmrc').getroot()
        groups=r.findall('Group')
        for cls in ['browser:e8y6','qterminal','calamares']:
            self.assertTrue(any(g.findtext('Class')==cls and 'maximized' in [o.text for o in g.findall('Option')] for g in groups))
        self.assertTrue(any('e8y6-power-menu' in (k.text or '') for k in r.findall('Key')))
