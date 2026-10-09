from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class V06Tests(unittest.TestCase):
 def test_terminal_replaced(self):
  pkgs=(ROOT/'packages/base.list').read_text()
  self.assertIn('qterminal',pkgs)
  self.assertNotIn('\nxterm\n',pkgs)
 def test_panel_and_network(self):
  self.assertIn('panel_position = top', (ROOT/'config/tint2/tint2rc').read_text())
  self.assertIn('renderer: NetworkManager', (ROOT/'config/network/01-barvium-network.yaml').read_text())
 def test_webapps_are_discovered(self):
  self.assertIn('brave-', (ROOT/'scripts/barvium-webapp-menu').read_text())
 def test_alt_f4_kept(self):
  self.assertIn('barvium-power-menu', (ROOT/'config/skel/.jwmrc').read_text())

 def test_audio_package_and_startup(self):
  packages=(ROOT/'packages/base.list').read_text().splitlines()
  session=(ROOT/'scripts/barvium-session').read_text()
  self.assertIn('pavucontrol', packages)
  self.assertNotIn('volumeicon-alsa', packages)
  self.assertNotIn('volumeicon ', session)
