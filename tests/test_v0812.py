import importlib.util
import tempfile
import unittest
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


v = load('validate_branding', 'validate-calamares-branding.py')
prep = load('prepare0811', 'prepare-calamares-v0811.py')


class Stabilization0812(unittest.TestCase):
    def test_real_branding_shape(self):
        content = yaml.safe_load((ROOT / 'config/calamares/branding/branding.desc').read_text())
        self.assertIsInstance(content['style'], dict)
        self.assertEqual(content['navigation'], 'widget')
        self.assertEqual(content['strings']['productName'], 'os:e8y6')
        self.assertEqual(content['strings']['version'], '0.8.18')

    def test_missing_style_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            brand = yaml.safe_load((ROOT / 'config/calamares/branding/branding.desc').read_text())
            brand.pop('style')
            (folder/'branding.desc').write_text(yaml.safe_dump(brand))
            (folder/'wordmark.svg').write_text('svg')
            (folder/'settings.conf').write_text(yaml.safe_dump(yaml.safe_load(self.example_settings())))
            with self.assertRaisesRegex(ValueError, 'style'):
                v.validate(folder/'branding.desc', folder/'settings.conf')

    @staticmethod
    def example_settings():
        return prep.adapt_settings('''sequence:
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
  - bootloader
branding: lubuntu
''')

    def test_full_branding_validates(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder/'branding.desc').write_text((ROOT/'config/calamares/branding/branding.desc').read_text())
            (folder/'wordmark.svg').write_bytes((ROOT/'config/calamares/branding/wordmark.svg').read_bytes())
            (folder/'settings.conf').write_text(self.example_settings())
            v.validate(folder/'branding.desc', folder/'settings.conf')

    def test_missing_settings_added_idempotently(self):
        configured = prep.adapt_settings(self.example_settings())
        parsed = yaml.safe_load(configured)
        for name in v.REQUIRED_BOOL_SETTINGS:
            self.assertIsInstance(parsed[name], bool)
        self.assertEqual(configured.count('quit-at-end:'), 1)
        self.assertEqual(configured.count('prompt-install:'), 1)

    def test_jwm_brave_movement_rules(self):
        import xml.etree.ElementTree as ET
        root = ET.parse(ROOT/'config/skel/.jwmrc').getroot()
        group = next(g for g in root.findall('Group') if g.findtext('Class') == 'browser:e8y6')
        opts = {element.text for element in group.findall('Option')}
        for opt in ('maximized', 'noborder', 'notitle', 'nomove', 'noresize', 'nodrag'):
            self.assertIn(opt, opts)

    def test_build_enforces_branding_validation(self):
        builder = (ROOT/'scripts/build-iso.sh').read_text()
        self.assertIn('validate-calamares-branding.py', builder)
        self.assertEqual((ROOT/'VERSION').read_text().strip(), '0.8.18')


if __name__ == '__main__':
    unittest.main()
