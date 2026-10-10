import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path

R = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cal13', R/'scripts/prepare-calamares-v0811.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class InstallerLogs(unittest.TestCase):
    def test_vendor_jobs_removed(self):
        base = (R/'tests/test_v0811.py').read_text()
        self.assertIn('contextualprocess@pkgselect_action', mod.DROP_EXEC)
        self.assertIn('shellprocess@fixconkeys_part1', mod.DROP_EXEC)
    def test_replace_helper(self):
        self.assertEqual(mod.replace_log_helper('script: calamares-logs-helper /target'),
                         'script: os-e8y6-installer-logs /target')
    def test_optional_iso_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)/'target'
            (target/'etc').mkdir(parents=True)
            result = subprocess.run(['sh', str(R/'scripts/os-e8y6-installer-logs'), str(target)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            self.assertTrue((target/'var/log/installer').is_dir())
    def test_mock_config_rewrite(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            p=root/'etc/calamares/modules';p.mkdir(parents=True)
            (p.parent/'settings.conf').write_text('''sequence:
- show:
  - welcome
  - locale
  - keyboard
  - partition
  - users
  - summary
- exec:
  - partition
  - mount
  - unpackfs
  - fstab
  - users
  - initramfs
  - shellprocess@fixconkeys_part1
  - contextualprocess@pkgselect_action
  - bootloader
branding: lubuntu
''')
            (p/'shellprocess_logs.conf').write_text('script: calamares-logs-helper /target')
            mod.prepare(root)
            cfg=(p.parent/'settings.conf').read_text()
            self.assertNotIn('fixconkeys_part1',cfg)
            self.assertNotIn('pkgselect_action',cfg)
            self.assertIn('os-e8y6-installer-logs', (p/'shellprocess_logs.conf').read_text())
