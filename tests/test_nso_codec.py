"""Synthetic raw/LZ4/ZBIC loader and GUI callback regression tests."""
import hashlib
from pathlib import Path
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

APP = Path(__file__).resolve().parents[1] / "Interactive ASM Cheats Updater"
sys.path.insert(0, str(APP))
import lz4.block
import zbic
from utilities.nso_codec import decompress_nso, parse_nso, ConversionError, MAX_DECODED
from utilities.main_file import MainNSOStruct, bytes_to_int
from utilities.exception import MainNSOError


def fixture(codec='raw', mask=7):
    blocks = [bytes.fromhex('02000014') * 16, b'hello strings\0' * 8, b'data' * 12]
    raw = bytearray(256)
    raw[:4] = b'NSO0'
    raw.extend(b'fixture\0')
    struct.pack_into('<I', raw, 28, 256)
    struct.pack_into('<I', raw, 44, 8)
    struct.pack_into('<I', raw, 60, 64)
    raw[64:96] = hashlib.sha256(b''.join(blocks)).digest()
    flags = 0x38 | (0x80 if codec == 'zbic' else 0)
    for i, block in enumerate(blocks):
        compressed = codec != 'raw' and mask & (1 << i)
        encoded = block
        if compressed:
            flags |= 1 << i
            encoded = (zbic.compress(block) if codec == 'zbic' else
                       lz4.block.compress(block, store_size=False))
        struct.pack_into('<III', raw, 16+16*i, len(raw), i*4096, len(block))
        struct.pack_into('<I', raw, 96+4*i, len(encoded))
        raw[160+32*i:192+32*i] = hashlib.sha256(block).digest()
        raw.extend(encoded)
    struct.pack_into('<I', raw, 12, flags)
    return bytes(raw), blocks


class NSOCompatibility(unittest.TestCase):
    def test_raw_lz4_zbic_and_every_mixed_mask(self):
        for codec in ['raw', 'lz4', 'zbic']:
            for mask in range(8):
                with self.subTest(codec=codec, mask=mask):
                    raw, blocks = fixture(codec, mask)
                    decoded = decompress_nso(raw)
                    parsed = parse_nso(decoded, MAX_DECODED)
                    self.assertEqual([s.data for s in parsed.segments], blocks)
                    self.assertEqual([s.rva for s in parsed.segments], [0, 4096, 8192])
                    self.assertEqual(parsed.bss, 64)
                    self.assertEqual(parsed.name, b'fixture\0')
                    self.assertEqual(decoded[64:96], raw[64:96])
                    self.assertEqual(struct.unpack_from('<I', decoded, 12)[0], 0x38)

    def test_loader_modification_save_reload_preserves_source(self):
        for codec in ['raw', 'lz4', 'zbic']:
            with self.subTest(codec=codec), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'main'
                raw, blocks = fixture(codec)
                path.write_bytes(raw)
                info = SimpleNamespace(logger=Mock(), msg_map={
                    'NOT NSO File': "['Not NSO']",
                    'NSO file decompressed': "['Decoded']"}, back_path=tmp, tool_path=tmp)
                loader = MainNSOStruct(str(path), info)
                self.assertEqual(loader.is_Compressed(), codec != 'raw')
                self.assertTrue(loader.process_file())
                self.assertEqual(bytes(loader.mainFuncFile), blocks[0])
                self.assertEqual(loader.ModuleId, raw[64:72].hex())
                self.assertEqual(bytes_to_int(loader.codeCaveStart), len(blocks[0]))
                self.assertEqual(bytes_to_int(loader.codeCaveEnd), 4096)
                loader.modify(4, b'ABCD')
                saved = loader.export_bytes()
                parsed = parse_nso(saved, MAX_DECODED)
                self.assertEqual(parsed.segments[0].data[4:8], b'ABCD')
                self.assertEqual(parsed.segments[1].data, blocks[1])
                self.assertEqual(saved[64:96], raw[64:96])
                self.assertEqual(path.read_bytes(), raw)
                self.assertEqual(list(Path(tmp).iterdir()), [path])

    def test_invalid_data_and_allocation_are_rejected(self):
        raw, _ = fixture('zbic')
        cases = [raw[:100], raw[:-1]]
        bad_hash = bytearray(raw); bad_hash[160] ^= 1; cases.append(bad_hash)
        wrong_codec = bytearray(raw); wrong_codec[12] &= ~0x80; cases.append(wrong_codec)
        huge = bytearray(raw); struct.pack_into('<I', huge, 24, MAX_DECODED+1); cases.append(huge)
        overlap = bytearray(raw); struct.pack_into('<I', overlap, 32, 256); cases.append(overlap)
        for bad in cases:
            with self.subTest(size=len(bad)), self.assertRaises(ConversionError):
                decompress_nso(bad)

    def test_bad_zbic_never_overwrites_main(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'main'
            raw, _ = fixture('zbic')
            raw = raw[:-1]
            path.write_bytes(raw)
            info = SimpleNamespace(logger=Mock(), msg_map={}, back_path=tmp, tool_path=tmp)
            with self.assertRaises(MainNSOError):
                MainNSOStruct(str(path), info).process_file()
            self.assertEqual(path.read_bytes(), raw)

    def test_zbic_missing_dependency_is_actionable(self):
        import builtins
        real_import = builtins.__import__
        def no_zbic(name, *args, **kwargs):
            if name == 'zbic':
                raise ImportError('not installed')
            return real_import(name, *args, **kwargs)
        raw, _ = fixture('zbic')
        with patch('builtins.__import__', side_effect=no_zbic):
            with self.assertRaisesRegex(ConversionError, 'pip install zbic'):
                decompress_nso(raw)


class GUICallbackCompatibility(unittest.TestCase):
    def test_zbic_load_modify_and_save_callbacks(self):
        with patch.object(sys, "argv", ["compatibility-tests"]):
            from utilities.interface import CodeUpdaterInterface
        import config
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'main'
            saved_path = Path(tmp) / 'main-saved'
            raw, _ = fixture('zbic')
            path.write_bytes(raw)
            gui = CodeUpdaterInterface.__new__(CodeUpdaterInterface)
            gui.msg_map = config.localization['loc_EN']['msg_map']
            gui.hints_map = config.localization['loc_EN']['hints_map']
            gui.globalInfo = SimpleNamespace(logger=Mock(), msg_map=gui.msg_map,
                                             back_path=tmp, tool_path=tmp)
            gui.supported_package_type = ['.nsp', '.xci', '.nsz', '.xcz']
            gui.input_cheats_script = Mock()
            gui.output_cheats_script = Mock()
            gui.code = SimpleNamespace(code_struct={})
            with patch('utilities.interface.messagebox.showinfo'), \
                 patch('utilities.interface.filedialog.asksaveasfilename', return_value=str(saved_path)):
                gui.load_file(str(path), is_old_file=True)
                gui.load_file(str(path), is_old_file=False)
                gui.new_main_file.modify(4, b'ABCD')
                gui.sav_nso()
            self.assertTrue(gui.old_is_NSO_file)
            self.assertTrue(gui.new_is_NSO_file)
            parsed = parse_nso(saved_path.read_bytes(), MAX_DECODED)
            self.assertEqual(parsed.segments[0].data[4:8], b'ABCD')
            self.assertEqual(path.read_bytes(), raw)



if __name__ == "__main__":
    unittest.main()
