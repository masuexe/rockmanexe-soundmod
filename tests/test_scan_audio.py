import importlib.util
from pathlib import Path
import struct
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("scan_audio", ROOT / "scripts/scan_audio.py")
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)


def encode(n):
    result = bytearray()
    while True:
        value = n & 127
        n >>= 7
        if n == 0:
            result.append(value | 128)
            return bytes(result)
        result.append(value)
        n -= 1


def patch(source, target, actions):
    b = b"BPS1" + encode(len(source)) + encode(len(target)) + encode(0) + actions
    b += struct.pack("<II", zlib.crc32(source), zlib.crc32(target))
    return b + struct.pack("<I", zlib.crc32(b))


class DecoderTests(unittest.TestCase):
    def test_all_actions_with_overlap_and_signed_copy_offsets(self):
        # SourceRead ab; literal X; SourceCopy ef, then cd backwards;
        # TargetCopy overlaps while repeating Xefcd, then seeks backwards.
        source = b"abcdefgh"
        target = b"abXefcdXefcdXefcdXefXef"
        actions = encode(4) + encode(1) + b"X"
        actions += encode(6) + encode(8) + encode(6) + encode(9)
        actions += encode((13 - 1) * 4 + 3) + encode(4)
        actions += encode((3 - 1) * 4 + 3) + encode(27)
        self.assertEqual(scan.apply_bps(source, patch(source, target, actions))[0], target)

    def test_wrong_source_rejected(self):
        p = patch(b"a", b"a", encode(0))
        with self.assertRaisesRegex(ValueError, "source checksum"):
            scan.apply_bps(b"b", p)

    def test_corrupt_patch_rejected(self):
        p = bytearray(patch(b"a", b"a", encode(0)))
        p[5] ^= 1
        with self.assertRaisesRegex(ValueError, "patch checksum"):
            scan.apply_bps(b"a", bytes(p))

    def test_copy_outside_source_rejected(self):
        p = patch(b"a", b"aa", encode(6) + encode(0))
        with self.assertRaisesRegex(ValueError, "SourceCopy"):
            scan.apply_bps(b"a", p)

    def test_target_copy_before_output_rejected(self):
        p = patch(b"a", b"a", encode(3) + encode(0))
        with self.assertRaisesRegex(ValueError, "TargetCopy"):
            scan.apply_bps(b"a", p)

    def test_ranges(self):
        self.assertEqual(scan.ranges_from_mask([False, True, True, False, True]),
                         [{"start": 1, "end_exclusive": 3, "size_bytes": 2},
                          {"start": 4, "end_exclusive": 5, "size_bytes": 1}])

    def test_gp_empty_header_with_nonpointer_tone(self):
        data = struct.pack("<BBBBI", 0, 0, 0, 0, 0x40000000)
        header = scan.song_header(data, scan.ROM_BASE)
        self.assertTrue(header["empty"])
        self.assertEqual(header["tone_field_raw"], "0x40000000")

    def test_invalid_track_pointer_rejected(self):
        data = struct.pack("<BBBBII", 1, 0, 0, 0, scan.ROM_BASE, 0xFFFFFFFF)
        self.assertIsNone(scan.song_header(data, scan.ROM_BASE))


@unittest.skipUnless((ROOT / "../roms/exe45.gba").exists() and (ROOT / "../roms/exegp.gba").exists(), "local ROMs unavailable")
class LocalRomTests(unittest.TestCase):
    def test_original_tables_and_literals(self):
        for name, offset, count, nonempty in [("exe45", 0x135214, 499, 352), ("exegp", 0x160658, 170, 86)]:
            data = (ROOT / f"../roms/{name}.gba").read_bytes()
            tables = scan.scan_tables(data)
            self.assertEqual(len(tables), 1)
            table = tables[0]
            self.assertEqual((table["file_offset"], table["entry_count"], table["nonempty_count"]), (offset, count, nonempty))
            self.assertGreater(len(table["table_pointer_occurrences"]), 0)

    @unittest.skipUnless((ROOT / "references/exe45_pvp_0.6.0.bps").exists() and (ROOT / "references/exe45_soundmod.bps").exists(), "local patches unavailable")
    def test_patch_checksums_and_changed_slots(self):
        base = (ROOT / "../roms/exe45.gba").read_bytes()
        self.assertEqual(scan.fingerprint(base)["crc32"], "A646601B")
        targets = []
        for name, crc, nonempty in [("exe45_pvp_0.6.0", "D1240E4B", 364), ("exe45_soundmod", "D0020C1F", 404)]:
            target, info = scan.apply_bps(base, (ROOT / f"references/{name}.bps").read_bytes())
            self.assertEqual(info["target_crc32"], crc)
            self.assertEqual(scan.scan_tables(target)[0]["nonempty_count"], nonempty)
            targets.append(target)
        self.assertEqual(sum(a != s and b != s and a != b for s, a, b in zip(base, *targets)), 59)
        changes = scan.compare_entries(scan.scan_tables(base), scan.scan_tables(targets[0]))[0]
        self.assertEqual([e["index"] for e in changes["changed_entries"]], list(range(69, 81)))


if __name__ == "__main__":
    unittest.main()
