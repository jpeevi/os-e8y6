import importlib.util
import tempfile
import unittest
from pathlib import Path

R = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('cal0811', R/'scripts/prepare-calamares-v0811.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class Calamares0811(unittest.TestCase):
    def test_brand_and_keep_core_steps(self):
        config = '''sequence:\n- show:\n  - welcome\n  - locale\n  - keyboard\n  - pkgselect\n  - partition\n  - users\n  - summary\n- exec:\n  - partition\n  - mount\n  - unpackfs\n  - fstab\n  - users\n  - initramfs\n  - shellprocess@add386arch\n  - bootloader\nbranding: lubuntu\n'''
        output = mod.adapt_settings(config)
        self.assertIn('branding: os-e8y6', output)
        self.assertNotIn('pkgselect', output)
        self.assertNotIn('shellprocess@add386arch', output)
        self.assertIn('  - bootloader', output)

    def test_missing_core_step_fails(self):
        with self.assertRaises(ValueError):
            mod.adapt_settings('sequence:\n- show:\n  - welcome\nbranding: lubuntu\n')

    def test_cdrom_cleanup_is_optional(self):
        sample = '- "rm /tmp/calamares-root/etc/apt/sources.list.d/cdrom.sources"\n'
        self.assertIn('rm -f ', mod.fix_cleanup(sample))
        self.assertEqual(mod.fix_cleanup(mod.fix_cleanup(sample)), mod.fix_cleanup(sample))

    def test_build_includes_branding_and_grub(self):
        builder = (R/'scripts/build-iso.sh').read_text()
        self.assertIn('prepare-calamares-v0811.py', builder)
        self.assertIn('GRUB_DISTRIBUTOR="os:e8y6"', builder)
        self.assertIn('branding/os-e8y6/branding.desc', builder)
        self.assertEqual((R/'VERSION').read_text().strip(), '0.8.13')

    def test_stage_mock_rootfs(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root)/'etc/calamares'
            (p/'modules').mkdir(parents=True)
            (p/'settings.conf').write_text('''sequence:\n- show:\n  - welcome\n  - locale\n  - keyboard\n  - partition\n  - users\n  - summary\n- exec:\n  - partition\n  - mount\n  - unpackfs\n  - fstab\n  - users\n  - initramfs\n  - bootloader\nbranding: lubuntu\n''')
            (p/'modules/shellprocess_rmcdrom.conf').write_text('''script: "rm /tmp/calamares-root/etc/apt/sources.list.d/cdrom.sources"\n''')
            (p/'modules/shellprocess_logs.conf').write_text('script: calamares-logs-helper /target')
            mod.prepare(Path(root))
            self.assertIn('branding: os-e8y6', (p/'settings.conf').read_text())
            self.assertIn('rm -f ', (p/'modules/shellprocess_rmcdrom.conf').read_text())
