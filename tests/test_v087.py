import unittest
from pathlib import Path
import xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
class MinimalRecovery(unittest.TestCase):
 def test_version(self):
  self.assertEqual((R/'VERSION').read_text().strip(),'0.8.9')
 def test_packages(self):
  p=(R/'packages/base.list').read_text().splitlines()
  self.assertIn('jwm',p)
  self.assertIn('calamares',p)
  for item in ('xfwm4','xfce4-panel','tint2','xfce4-session'):
   self.assertNotIn(item,p)
 def test_session(self):
  s=(R/'config/skel/.xinitrc').read_text()
  self.assertIn('jwm',s)
  j=ET.parse(R/'config/skel/.jwmrc').getroot()
  self.assertFalse(j.findall('Tray'))
  self.assertIn('exec:qterminal',(R/'config/skel/.jwmrc').read_text())
 def test_one_shot_browser(self):
  s=(R/'scripts/barvium-session').read_text()
  self.assertEqual(s.count('/usr/local/bin/barvium-open-brave'),1)
  self.assertNotIn('while ',s)
  self.assertNotIn('sleep ',s)
  self.assertNotIn('watchdog',s)
 def test_terminal_only_installer(self):
  s=(R/'scripts/bravium-install').read_text()
  self.assertIn('[[ -t 0 ]]',s)
  self.assertIn('pkexec',s)
  self.assertIn('boot=casper',s)
  self.assertIn('systemd-detect-virt',s)
  self.assertNotIn('yad',s)
 def test_builder(self):
  b=(R/'scripts/build-iso.sh').read_text()
  self.assertIn('config/skel/.jwmrc',b)
  self.assertNotIn('config/xfce4/',b)
  self.assertNotIn('barvium-brave-watchdog',b)
