"""Empty-stack LOOPEND fallthrough does not fabricate repeats or relax calls."""
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from nds_music import SoundArchive, nds_sdat, trace_sequence


class LoopFallthroughTests(unittest.TestCase):
    def test_empty_stack_command_remains_executed_before_finite_end(self):
        raw=b'\xFC\x3C\x64\x0C\xFF'
        for analysis in (False,True):
            t=trace_sequence(raw,analysis_only=analysis)[0]
            self.assertEqual(t['termination'],'end')
            self.assertEqual(t['end_ticks'],12)
            a=t['actions'][0]
            self.assertEqual((a['name'],a['offset'],a['next'],a['ticks']),('loop_end',0,1,0))
            self.assertEqual(a['loop_end_fallthrough'],'empty_stack')
            self.assertEqual([a['ticks'] for a in t['actions'] if a['name']=='note'],[0])

    def test_finished_counted_loop_and_return_do_not_restart_at_extra_loopend(self):
        raw=bytearray(b'\xC7\x00\xD4\x02\x95\x10\x00\x00\xFC\xFC\xFF')
        raw.extend(bytes(16-len(raw)))
        raw.extend(b'\x3C\x64\x0C\x80\x0C\xFD')
        t=trace_sequence(bytes(raw),analysis_only=True)[0]
        self.assertEqual(t['termination'],'end')
        self.assertEqual(t['end_ticks'],24)
        self.assertEqual([a['ticks'] for a in t['actions'] if a['name']=='note'],[0,12])
        neutral=[a for a in t['actions'] if a.get('loop_end_fallthrough')]
        self.assertEqual([(a['offset'],a['ticks']) for a in neutral],[(9,24)])

    def test_zero_time_cycle_active_call_and_return_guards_remain(self):
        active_call=b'\x95\x04\x00\x00\xFC\xFD'
        cases=[(b'\xFC\x94\x00\x00\x00','Zero-time'),
               (active_call,'loop end without start'),(b'\xFD','return without call'),
               (b'\xD4\x01'*4+b'\xFF','stack exceeds three')]
        for raw,message in cases:
            with self.subTest(raw=raw),self.assertRaisesRegex(ValueError,message):
                trace_sequence(raw,analysis_only=True)

    @unittest.skipUnless(Path('/home/harp/projects/nds/roms/ssr1d.nds').exists(),'local source ROM')
    def test_sf1_hokora_keeps_finite_seventh_track_and_original_loop_periods(self):
        source=Path('/home/harp/projects/nds/roms/ssr1d.nds').read_bytes()
        archive=SoundArchive(nds_sdat(source,667))
        tracks=trace_sequence(archive.sequence(20)[0],analysis_only=True)
        self.assertEqual([t['track'] for t in tracks],list(range(7)))
        self.assertEqual([t['termination'] for t in tracks],['loop']*6+['end'])
        self.assertEqual([t['loop_ticks'] for t in tracks[:6]],[3072,3072,3072,1536,1536,1536])
        t=tracks[6]
        self.assertEqual(t['end_ticks'],1536)
        self.assertEqual(sum(a['name']=='note' for a in t['actions']),256)
        self.assertEqual([(a['offset'],a['ticks']) for a in t['actions'] if a.get('loop_end_fallthrough')],[(2500,1536)])
        self.assertEqual((t['actions'][-1]['name'],t['actions'][-1]['offset']),('end',2501))


if __name__=='__main__':unittest.main()
