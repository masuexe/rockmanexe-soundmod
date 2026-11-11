"""STRM payload bounds, ADPCM state and stereo/loop export invariants."""
from pathlib import Path
import struct
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from nds_stream import decode_stream, convert_stream
from scan_audio import ROM_BASE


def fixture():
    # Full stereo block plus an odd-sized last block with an unused high nibble.
    full = [struct.pack('<hH', 1000, 0) + bytes(508),
            struct.pack('<hH', -2000, 0) + bytes(508)]
    last = [struct.pack('<hH', 3000, 0) + b'\x10\x32\xf4',
            struct.pack('<hH', -4000, 0) + b'\x98\xba\x7c']
    payload = b''.join(full + last)
    payload += bytes(-len(payload) % 4)
    size = 104 + len(payload)
    return (struct.pack('<4sHHIHH', b'STRM', 0xFEFF, 0x100, size, 16, 2)
            + struct.pack('<4sI', b'HEAD', 80)
            + struct.pack('<4B2H16I', 2, 1, 2, 0, 26182, 20,
                          5, 1021, 104, 2, 512, 1016, 7, 5, 0, *([0]*7))
            + struct.pack('<4sI', b'DATA', size-96) + payload)


class StreamTests(unittest.TestCase):
    def test_block_state_resets_stereo_and_unused_nibble(self):
        channels, info = decode_stream(fixture())
        self.assertEqual(info['source_sample_count'], 1021)
        self.assertEqual(list(channels[0][:1016]), [1000]*1016)
        self.assertEqual(list(channels[1][:1016]), [-2000]*1016)
        self.assertEqual(list(channels[0][1016:]), [3000, 3001, 3004, 3008, 3015])
        self.assertEqual(list(channels[1][1016:]), [-4000, -4001, -4004, -4008, -4015])

    def test_nds_saturation_is_symmetric(self):
        raw = bytearray(fixture())
        struct.pack_into('<hH', raw, 104, -32768, 88)
        raw[108:616] = b'\xff'*508
        struct.pack_into('<hH', raw, 616, 32767, 88)
        raw[620:1128] = b'\x77'*508
        c, _ = decode_stream(raw)
        self.assertEqual(set(c[0][:1016]), {-32767})
        self.assertEqual(set(c[1][:1016]), {32767})

    def test_bad_header_payload_and_loop_are_rejected(self):
        changes = [(0,b'BAD!'),(8,struct.pack('<I',1)),(16,b'FAIL'),
                   (24,b'\x00'),(25,b'\x00'),(26,b'\x01'),
                   (32,struct.pack('<I',1021)),(36,struct.pack('<I',5_000_001)),
                   (40,struct.pack('<I',100)),(44,struct.pack('<I',100)),
                   (48,struct.pack('<I',256)),(52,struct.pack('<I',512)),
                   (56,struct.pack('<I',512)),(60,struct.pack('<I',1)),
                   (64,struct.pack('<I',8)),(96,b'FAIL'),(100,struct.pack('<I',1)),
                   (106,struct.pack('<H',89)),(1137,struct.pack('<H',89))]
        for offset, value in changes:
            with self.subTest(offset=offset):
                raw=bytearray(fixture());raw[offset:offset+len(value)]=value
                with self.assertRaises(ValueError):decode_stream(raw)
        with self.assertRaises(ValueError):decode_stream(fixture()[:-1])

    def test_bounded_zero_sdat_padding_is_accepted(self):
        expected, _ = decode_stream(fixture())
        actual, info = decode_stream(fixture() + bytes(4))
        self.assertEqual(actual, expected)
        self.assertEqual(info['declared_bytes'], len(fixture()))
        for suffix in (bytes(5), b'\x00\x00\x00\x01'):
            with self.assertRaises(ValueError):decode_stream(fixture() + suffix)

    def test_nonzero_trailing_padding_is_rejected(self):
        raw=bytearray(fixture());raw[-1]=1
        with self.assertRaisesRegex(ValueError,'padding'):decode_stream(raw)

    def test_export_has_two_ties_distinct_waves_and_no_retrigger(self):
        blob, dep, report=convert_stream(fixture(),70)
        self.assertEqual(report['native_track_volume'],105)
        self.assertEqual(len(dep['samples']),2)
        self.assertEqual(len(dep['tracks']),2)
        for sample in dep['samples']:
            self.assertTrue(sample['flags'] & 0x4000)
            self.assertLess(sample['loop_start'],sample['sample_count'])
        for i,track in enumerate(dep['tracks']):
            ties=[e for e in track['events'] if e['name']=='TIE']
            self.assertEqual([(e['ticks'],e['voice'],e['key']) for e in ties],[(0,i,60)])
            self.assertEqual([e['value'] for e in track['events'] if e['name']=='PAN'],[0 if i==0 else 127])
            self.assertFalse(any(e['name'] in ('NOTE','EOT','FINE') for e in track['events']))
        header=struct.unpack_from('<I',blob)[0]-ROM_BASE
        self.assertEqual(blob[header],2)

    def test_gain_inputs_and_headroom_fail_explicitly(self):
        for volume,gain in [(128,0),(True,0),(70,float('nan')),(70,13),(127,3.5)]:
            with self.subTest(volume=volume,gain=gain):
                with self.assertRaises(ValueError):convert_stream(fixture(),volume,gain)


if __name__=='__main__':unittest.main()
