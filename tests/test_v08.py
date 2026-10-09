from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
class V08Tests(unittest.TestCase):
    def test_version(self):
        self.assertEqual((ROOT / 'VERSION').read_text().strip(), '0.8.1')
        self.assertIn('RELEASE_VERSION="$(cat "$ROOT/VERSION")"', (ROOT / 'scripts/build-iso.sh').read_text())
    def test_install_vm_guard(self):
        src = (ROOT / 'scripts/bravium-install').read_text()
        self.assertIn('systemd-detect-virt --vm', src)
        self.assertIn('VM TEST ONLY', src)
        self.assertIn('pkexec env', src)
    def test_documentation(self):
        self.assertTrue((ROOT / 'AGENTS.md').exists())
        self.assertTrue((ROOT / 'README.md').exists())
        self.assertFalse((ROOT / 'BUILD-ISO.md').exists())
    def test_installer_dependency(self):
        base = (ROOT / 'packages/base.list').read_text().splitlines()
        self.assertIn('calamares', base)
        self.assertIn('calamares-settings-lubuntu', base)
