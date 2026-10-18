"""Key-selection and NSZ validation tests using synthetic keys only."""
from binascii import crc32
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

APP = Path(__file__).resolve().parents[1] / "Interactive ASM Cheats Updater"
sys.path.insert(0, str(APP))
from utilities.key_file import select_key_file, read_keys
with patch.object(sys, "argv", ["compatibility-tests"]):
    from utilities.game_package import GamePackage
from utilities.exception import GamePackageError
from nsz.nut import Keys


class KeyCompatibility(unittest.TestCase):
    def test_prod_keys_priority_and_legacy_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'app'; root.mkdir()
            home = Path(tmp) / 'home'; (home / '.switch').mkdir(parents=True)
            legacy = root / 'keys.txt'; legacy.write_text('legacy')
            self.assertEqual(select_key_file(root, home), legacy)
            user = home / '.switch' / 'prod.keys'; user.write_text('user')
            self.assertEqual(select_key_file(root, home), user)
            local = root / 'prod.keys'; local.write_text('explicit')
            self.assertEqual(select_key_file(root, home), local)

    def test_key_parser_accepts_new_generations_case_bom_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'prod.keys'
            path.write_text('\ufeffMASTER_KEY_14 = ' + '01'*16 + ' # test only\n'
                            'master_key_15 = ' + '02'*16 + '\n', encoding='utf-8')
            self.assertEqual(read_keys(path), {'master_key_14': bytes([1])*16,
                                               'master_key_15': bytes([2])*16})
            for text in ['master_key_14 = 123', 'master_key_14 = xyz',
                         'master_key_14 = 01\nmaster_key_14 = 02']:
                path.write_text(text)
                with self.assertRaises(ValueError):
                    read_keys(path)

    def test_nsz_14_15_are_known_and_invalid_keys_still_fail(self):
        for name in ['master_key_14', 'master_key_15']:
            self.assertIn(name, Keys.crc32_checksum)
            with patch.dict(Keys.keys, {name: '00'*16}, clear=True), \
                 patch.object(Keys.Print, 'info') as info, patch.object(Keys.Print, 'error'):
                with self.assertRaisesRegex(IOError, 'crc32 mismatch'):
                    Keys.getKey(name)
                info.assert_not_called()

    def test_nsz_uses_selected_file_and_resets_previous_key_state(self):
        package = GamePackage.__new__(GamePackage)
        with tempfile.TemporaryDirectory() as tmp:
            package.key_file = Path(tmp) / 'prod.keys'
            package.key_file.write_text('master_key_14 = ' + '01'*16)
            package.keys = {'outdated_key': bytes(16)}
            with patch.dict(Keys.keys, {'stale_key': '00'}, clear=True), \
                 patch.object(Keys, 'titleKeks', ['stale']), \
                 patch.object(Keys, 'keyAreaKeys', ['stale']), \
                 patch.object(Keys, 'load', return_value=True) as load:
                package.load_nsz_keys()
                load.assert_called_once_with(str(package.key_file))
                self.assertEqual(Keys.keys, {'master_key_14': '01'*16})
                self.assertEqual(package.keys, {'master_key_14': bytes([1])*16})
                self.assertEqual(Keys.titleKeks, [])
                self.assertEqual(Keys.keyAreaKeys, [])
            with patch.object(Keys, 'load', return_value=False):
                with self.assertRaises(GamePackageError):
                    package.load_nsz_keys()

    def test_normalized_keys_reach_actual_nsz_loader(self):
        # Dummy values and matching test checksums exercise derivation without
        # using any real keys. Production checksum validation stays enabled.
        names = ['aes_kek_generation_source', 'aes_key_generation_source',
                 'titlekek_source', 'key_area_key_application_source',
                 'key_area_key_ocean_source', 'key_area_key_system_source',
                 'master_key_14', 'master_key_15']
        dummy = {name: bytes([i+1])*16 for i, name in enumerate(names)}
        checksums = {name: crc32(value) for name, value in dummy.items()}
        with tempfile.TemporaryDirectory() as tmp:
            key_file = Path(tmp) / 'prod.keys'
            key_file.write_text('\ufeff' + '\n'.join(
                name.upper() + ' = ' + value.hex() + ' # dummy only'
                for name, value in dummy.items()), encoding='utf-8')
            package = GamePackage(SimpleNamespace(root_path=tmp, logger=Mock(), msg_map={}))
            with patch.dict(Keys.keys, {}, clear=True), \
                 patch.object(Keys, 'titleKeks', []), \
                 patch.object(Keys, 'keyAreaKeys', []), \
                 patch.dict(Keys.crc32_checksum, checksums):
                package.load_nsz_keys()
                self.assertEqual(package.keys, dummy)
                self.assertEqual(Keys.getMasterKey(0x14), dummy['master_key_14'])
                self.assertEqual(Keys.getMasterKey(0x15), dummy['master_key_15'])
                self.assertTrue(Keys.keys_loaded)


if __name__ == '__main__':
    unittest.main()
