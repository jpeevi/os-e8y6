"""Offline privacy and opt-in tests (no external HTTP)."""
import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class PrivacyTests(unittest.TestCase):
    def test_client_requires_https_and_has_no_default_request(self):
        client = load_module("counterclient", ROOT / "telemetry/client.py")
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                client.report("http://localhost:8000", "0.3.0-dev", Path(d) / "sent")

    def test_client_one_send_and_no_device_id(self):
        client = load_module("counterclient", ROOT / "telemetry/client.py")
        class Reply:
            status = 204
            def __enter__(self): return self
            def __exit__(self, *args): return None
        with tempfile.TemporaryDirectory() as d, patch.object(client.urllib.request, 'urlopen', return_value=Reply()) as request:
            marker = Path(d) / 'sent'
            client.report('https://example.org', '0.3.0-dev', marker)
            client.report('https://example.org', '0.3.0-dev', marker)
            self.assertEqual(request.call_count, 1)
            body = request.call_args.args[0].data.decode()
            self.assertEqual(body, '{"event": "install_completed", "version": "0.3.0-dev"}')

    def test_privacy_script_fails_without_build_rootfs_marker(self):
        import subprocess
        result = subprocess.run(['bash', str(ROOT / 'privacy/remove-optional-reporting-chroot.sh')],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Refusing to modify system', result.stderr)

if __name__ == '__main__': unittest.main()
