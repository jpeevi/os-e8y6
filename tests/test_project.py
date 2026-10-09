"""Basic offline structural checks for the Barvium starter project."""
from pathlib import Path
import subprocess
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class ProjectTests(unittest.TestCase):
    def test_jwm_xml_parses(self):
        jwm = ET.parse(ROOT / "config/skel/.jwmrc").getroot()
        self.assertEqual(jwm.tag, "JWM")
        self.assertEqual(len(jwm.findall("Tray")), 0, "No taskbar should be configured")
        menu = jwm.find("RootMenu")
        self.assertIsNotNone(menu)
        self.assertEqual(menu.attrib.get("onroot"), "3")

    def test_three_apps_are_present(self):
        jwm = ET.parse(ROOT / "config/skel/.jwmrc").getroot()
        commands = [item.text.strip() for item in jwm.findall("./RootMenu/Program")]
        self.assertEqual(commands[:3], ["/usr/local/bin/barvium-open-brave", "pcmanfm", "qterminal"])

    def test_no_graphical_login_manager(self):
        packages = [line.strip() for line in (ROOT / "packages/base.list").read_text().splitlines()
                    if line.strip() and not line.startswith("#")]
        for forbidden in ("gdm3", "lightdm", "sddm", "ubuntu-desktop", "xubuntu-desktop", "xfce4"):
            self.assertNotIn(forbidden, packages)

    def test_build_check(self):
        result = subprocess.run(["bash", str(ROOT / "build.sh"), "check"],
                                capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_build_script_advertises_experimental_iso(self):
        output = subprocess.run(["bash", str(ROOT / "build.sh"), "help"],
                                capture_output=True, text=True, cwd=ROOT, check=True).stdout
        self.assertIn("live ISO", output)
        self.assertIn("no disk installer", output)


if __name__ == "__main__":
    unittest.main()
