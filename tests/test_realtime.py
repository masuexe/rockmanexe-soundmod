import json
import math
from pathlib import Path
import struct
import sys
import tempfile
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from realtime_audio import RealtimeEngine
from original_catalog import PROFILES


class RealtimeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        directory=Path(self.temp.name)
        helper=directory/'helper'
        helper.write_text('''#!/usr/bin/env python3
import sys,os,struct,json
rate=int(sys.argv[5]);song=int(sys.argv[4])
if song==1:
 print('{"sample_rate":1,"channels":2,"format":"f32le"}',flush=True)
 sys.exit(0)
if song==2:
 print('initialization failed',file=sys.stderr);sys.exit(1)
print(json.dumps({'sample_rate':rate,'channels':2,'format':'f32le'}),flush=True)
while True:os.write(1,struct.pack('<ff',.25,-.25)*1024)
''')
        helper.chmod(0o755)
        self.engine=RealtimeEngine(helper,directory/'streams')
    def tearDown(self):
        self.engine.stop();self.temp.cleanup()
    def test_live_pcm_and_stop(self):
        session=self.engine.start(b'ROM',0,3,0)
        block=session.read()
        self.assertTrue(block)
        self.assertEqual(struct.unpack('<ff',block[:8]),(.25,-.25))
        self.engine.stop(session.id)
        self.assertIsNotNone(session.process.poll())
        self.assertIsNone(self.engine.active)
    def test_switch_and_stale_stop_are_isolated(self):
        first=self.engine.start(b'ROM',0,3,0)
        second=self.engine.start(b'ROM',0,3,0)
        self.assertIsNotNone(first.process.poll())
        self.engine.stop(first.id)
        self.assertIs(self.engine.active,second)
        self.assertEqual(len(list(self.engine.directory.glob('*.gba'))),1)
    def test_bad_format_and_initialization_fail_cleanly(self):
        with self.assertRaisesRegex(ValueError,'format'):self.engine.start(b'ROM',0,3,1)
        self.assertIsNone(self.engine.active)
        with self.assertRaisesRegex(ValueError,'initialize'):self.engine.start(b'ROM',0,3,2)
        self.assertIsNone(self.engine.active)
    def test_missing_binary_and_invalid_rate(self):
        with self.assertRaises(ValueError):self.engine.start(b'ROM',0,3,0,0)
        self.engine.binary=Path(self.temp.name)/'missing'
        with self.assertRaisesRegex(ValueError,'Build'):self.engine.start(b'ROM',0,3,0)


@unittest.skipUnless((ROOT/'out/realtime/exe-realtime').is_file() and all((ROOT.parent/'roms'/PROFILES[k]['filename']).is_file() for k in ('exe1','exe6','exegp')), 'built core and local ROMs unavailable')
class RealCoreTests(unittest.TestCase):
    def test_representative_original_roms_stream_before_whole_clip(self):
        with tempfile.TemporaryDirectory() as temp:
            engine=RealtimeEngine(ROOT/'out/realtime/exe-realtime',temp)
            try:
                for key,song in [('exe1',0),('exe6',1),('exegp',1)]:
                    profile=PROFILES[key];data=(ROOT.parent/'roms'/profile['filename']).read_bytes()
                    started=time.monotonic()
                    session=engine.start(data,profile['table_offset'],profile['entry_count'],song)
                    self.assertLess(time.monotonic()-started,5)
                    samples=b''
                    while len(samples)<48000*8:
                        chunk=session.read()
                        self.assertTrue(chunk)
                        samples+=chunk
                    samples=samples[:len(samples)//8*8]
                    floats=struct.unpack('<'+'f'*(len(samples)//4),samples)
                    self.assertTrue(all(math.isfinite(s) for s in floats))
                    self.assertGreater(max(abs(s) for s in floats),.001)
                    engine.stop()
                    self.assertIsNotNone(session.process.poll())
            finally:engine.stop()


if __name__=='__main__':unittest.main()
