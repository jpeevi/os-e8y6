"""Static and smoke checks for the v0.5 QEMU launcher."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

class LauncherTests(unittest.TestCase):
    def test_shell_syntax(self):
        subprocess.run(['bash', '-n', str(ROOT / 'run-latest.sh')], check=True)

    def test_launcher_nonroot_and_eject(self):
        code = (ROOT / 'run-latest.sh').read_text()
        self.assertIn('EUID == 0', code)
        self.assertIn('eject -f barviumcd', code)
        self.assertIn('-monitor stdio', code)
        self.assertIn('[[ -r "$LATEST" ]]', code)

if __name__ == '__main__':
    unittest.main()
