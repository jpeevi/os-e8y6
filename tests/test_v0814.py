import unittest
from pathlib import Path
import yaml
ROOT=Path(__file__).resolve().parents[1]
class NativeInstaller0814(unittest.TestCase):
 def test_native_sequence(self):
  settings=yaml.safe_load((ROOT/'config/calamares/settings.conf').read_text())
  self.assertEqual(settings['branding'],'os-e8y6')
  show=settings['sequence'][0]['show']; execs=settings['sequence'][1]['exec']
  for name in ('welcome','locale','keyboard','partition','users','summary'):
   self.assertIn(name,show)
  for name in ('partition','mount','unpackfs','machineid','fstab','users','initramfs','grubcfg','bootloader','shellprocess@installed-session','shellprocess@logs','umount'):
   self.assertIn(name,execs)
  for name in ('pkgselect','dracut','contextualprocess','shellprocess@rmcdrom'):
   self.assertNotIn(name,str(settings))
 def test_restore_verified_vendor_settings(self):
  self.assertIn('calamares-settings-lubuntu',(ROOT/'packages/base.list').read_text())
  script=(ROOT/'scripts/build-iso.sh').read_text()
  self.assertIn('prepare-calamares-v0811.py',script)
  self.assertIn('integrate-installed-session.py',script)
 def test_installed_login_cleanup(self):
  job=yaml.safe_load((ROOT/'config/calamares/modules/shellprocess-installed-session.conf').read_text())
  self.assertFalse(job['dontChroot'])
  self.assertIn('autologin.conf',str(job['script']))
  self.assertIn('userdel -r e8y6',str(job['script']))
  profile=(ROOT/'config/skel/.profile').read_text()
  self.assertIn('/dev/tty1',profile)
  self.assertIn('exec startx',profile)
 def test_brave_wait_not_poll(self):
  session=(ROOT/'scripts/e8y6-session').read_text()
  self.assertEqual(session.count('/usr/local/bin/e8y6-open-browser'),1)
  self.assertIn('while :; do',session)
  self.assertNotIn('pgrep',session)
 def test_timezones(self):
  sequence=yaml.safe_load((ROOT/'config/calamares/settings.conf').read_text())['sequence']
  self.assertIn('locale',sequence[0]['show'])
  self.assertIn('locale',sequence[1]['exec'])
