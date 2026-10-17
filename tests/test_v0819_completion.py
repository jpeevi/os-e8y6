import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class LockCompletion(unittest.TestCase):
    def test_python_syntax(self):
        ast.parse((ROOT / 'scripts/e8y6-lock').read_text())

    def test_authentication_stays_with_pam_locker(self):
        content = (ROOT / 'scripts/e8y6-lock').read_text()
        self.assertIn("'/usr/bin/i3lock'", content)
        self.assertIn("'-n', '-u', '-i'", content)
        self.assertIn('TemporaryDirectory', content)
        self.assertIn('boot=casper', content)
        self.assertNotIn('lockscreen.png', content)

    def test_installer_intact(self):
        script = (ROOT / 'scripts/build-iso.sh').read_text()
        self.assertIn('prepare-calamares-v0811.py', script)
        self.assertIn('calamares-settings-lubuntu', script)

    def test_required_runtime_packages(self):
        items = (ROOT / 'packages/base.list').read_text().splitlines()
        self.assertIn('python3-pil', items)
        self.assertIn('x11-xserver-utils', items)
        self.assertIn('i3lock', items)
