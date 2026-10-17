import pathlib, unittest
R=pathlib.Path(__file__).resolve().parents[1]
class SessionDiagnostics0819(unittest.TestCase):
    def test_version(self):
        self.assertEqual((R/'VERSION').read_text().strip(), '0.8.19')
    def test_logout_uses_graceful_protocol(self):
        s=(R/'scripts/e8y6-logout').read_text()
        self.assertIn('logout-requested',s)
        self.assertIn('wmctrl -ic',s)
        self.assertIn('jwm -exit',s)
        self.assertNotIn('kill -9',s)
        supervisor=(R/'scripts/e8y6-session').read_text()
        self.assertIn('logout-requested', supervisor)
        self.assertIn('wait "$CHILD"',supervisor)
        self.assertIn('sleep 2',supervisor)
        self.assertIn("('/usr/local/bin/e8y6-logout')",(R/'scripts/e8y6-power-menu').read_text().replace('[','(').replace(']',')'))
    def test_debug_installed(self):
        s=(R/'scripts/e8y6-debug').read_text()
        self.assertIn('--browser',s)
        self.assertIn('--session',s)
        self.assertIn('--installer',s)
        self.assertNotIn('curl ',s)
        self.assertIn('e8y6-debug e8y6-core-update e8y6-terminal; do',(R/'scripts/build-iso.sh').read_text())
