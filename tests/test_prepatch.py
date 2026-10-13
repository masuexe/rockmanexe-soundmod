"""IPS format edge cases and pinned pre-patch discovery."""
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepatch import apply_ips, apply_prepatch, find_prepatch
from target_profiles import target_profile


def record(address, data):
    return address.to_bytes(3,'big')+len(data).to_bytes(2,'big')+data


class IPSTests(unittest.TestCase):
    def test_literal_rle_extension_and_provenance(self):
        patch=b'PATCH'+record(1,b'XY')+b'\x00\x00\x06\0\0\0\x03Z'+b'EOF'
        rom,info=apply_ips(b'abc',patch)
        self.assertEqual(rom,b'aXY\0\0\0ZZZ')
        self.assertEqual(info['write_ranges'],[[1,3],[6,9]])
        self.assertEqual(info['format'],'ips')
        self.assertEqual(info['target_fingerprint']['size_bytes'],9)

    def test_optional_final_size_shrinks_or_extends(self):
        for size,expected in [(2,b'ab'),(5,b'abc\0\0')]:
            self.assertEqual(apply_ips(b'abc',b'PATCHEOF'+size.to_bytes(3,'big'))[0],expected)

    def test_malformed_inputs_rejected(self):
        for patch in [b'',b'BPS1',b'PATCH',b'PATCH\0',b'PATCH\0\0\0\0\x02x',
                      b'PATCH\0\0\0\0\0\0',b'PATCH\0\0\0\0\0\0\0Z',b'PATCHEOFx']:
            with self.subTest(patch=patch), self.assertRaises(ValueError):apply_ips(b'abc',patch)

    def test_zip_member_read_without_extracting_files(self):
        profile=target_profile('exegp-chipcontrol')
        with tempfile.TemporaryDirectory() as temp:
            with ZipFile(Path(temp)/profile['patch_archive'],'w') as z:
                z.writestr(profile['patch_filename'],b'PATCHEOF')
                z.writestr('../outside.txt',b'ignored')
            self.assertEqual(find_prepatch(profile,[temp]),(profile['patch_filename'],b'PATCHEOF'))
            self.assertEqual(len(list(Path(temp).iterdir())),1)
            (Path(temp)/profile['patch_filename']).write_bytes(b'loose')
            self.assertEqual(find_prepatch(profile,[temp])[1],b'loose')

    def test_wrong_base_rejected_before_ips_decoding(self):
        with self.assertRaisesRegex(ValueError,'Original ROM'):
            apply_prepatch(b'abc',b'PATCHEOF',target_profile('exegp-chipcontrol'))


if __name__=='__main__':unittest.main()
