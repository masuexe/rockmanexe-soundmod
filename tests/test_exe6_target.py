"""Pinned Japanese EXE6 target adapters and original-ROM exports."""
import copy
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from target_profiles import target_profile,identify_target,check_layout,selector_value
from original_catalog import catalog_originals
from build_unified import build_catalog,resolve_pools
from manager_backend import Manager
from scan_audio import apply_bps,ROM_BASE
from test_manager import finish

ROMS=ROOT.parent/'roms'


class FrameSelectorTests(unittest.TestCase):
    def test_counter_wrap_and_low_byte_coverage(self):
        layout=target_profile('exe6')['layout']
        self.assertEqual(len({selector_value(layout,i) for i in range(256)}),256)
        self.assertEqual(selector_value(layout,0x10001),selector_value(layout,1))
        self.assertEqual(selector_value(layout,0x10000),0)


@unittest.skipUnless(all((ROMS/(k+'.gba')).is_file() for k in ['exe6','exe6f','exe1','exegp']),'local EXE6 inputs unavailable')
class EXE6TargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources={k:(ROMS/(k+'.gba')).read_bytes() for k in ['exe1','exegp']}
        cls.targets={}
        for key in ['exe6','exe6f']:
            base=(ROMS/(key+'.gba')).read_bytes();value,reports=catalog_originals(base,base,cls.sources)
            project={'schema_version':1,'target_profile':key,'pools':{
                '1':{'tracks':['exe1:0']},'21':{'tracks':['native-exe6:21','exegp:1']}}}
            output,_,manifest=build_catalog(base,base,value,reports,cls.sources,project,selected_only=True)
            cls.targets[key]=(base,value,reports,project,output,manifest)

    def test_exact_identity_and_driver_preconditions(self):
        for key,(base,*_) in self.targets.items():
            with self.subTest(key=key):
                self.assertEqual(identify_target(base)['key'],key)
                layout=target_profile(key)['layout'];check_layout(base,layout)
                altered=bytearray(base);altered[layout['entry_offset']]^=1
                with self.assertRaises(ValueError):identify_target(altered)
                with self.assertRaises(ValueError):check_layout(altered,layout)

    def test_native_music_effects_and_foreign_capacity(self):
        for key,(_,value,*_) in self.targets.items():
            with self.subTest(key=key):
                self.assertEqual(value['target_track_capacity'],8)
                self.assertEqual([r['source_index'] for r in value['entries'] if r['source']=='native-exe6' and r['playlist_eligible']],list(range(1,38)))
                rows={r['key']:r for r in value['entries']}
                self.assertFalse(rows['exegp:5']['playlist_eligible'])
                self.assertEqual(rows['exegp:5']['availability'],'exceeds_target_track_capacity')
                self.assertIn('Communication',value['event_labels']['21'])
                with self.assertRaises(ValueError):resolve_pools({'schema_version':1,'pools':{'100':{'tracks':['exe1:0']}}},value)

    def test_native_prefix_table_and_original_queue_preserved(self):
        for key,(base,_,_,_,output,manifest) in self.targets.items():
            with self.subTest(key=key):
                layout=target_profile(key)['layout'];expected=bytearray(base)
                for a,b in manifest['declared_prefix_ranges']:expected[a:b]=output[a:b]
                self.assertEqual(output[:len(base)],expected)
                self.assertEqual(output[0x5D4:0x8B2],base[0x5D4:0x8B2])
                table=manifest['target_table_file_offset'];native=layout['table_offset']
                self.assertEqual(output[table:table+474*8],base[native:native+474*8])
                for offset in layout['table_references']:self.assertEqual(struct.unpack_from('<I',output,offset)[0],ROM_BASE+table)
                self.assertEqual(len(manifest['imports']),2)

    def test_communication_descriptors_and_selection_are_verified(self):
        for key,(base,*_) in self.targets.items():
            with self.subTest(key=key):
                table=struct.unpack_from('<I',base,0xAF2C)[0]-ROM_BASE
                self.assertEqual({base[table+i*16+2] for i in range(164)},{21})
                self.assertEqual(base[0x93F4:0x9406].hex(),'0821084201d0152001e0e86b8078632801d0')

    def test_projects_reject_other_variants_and_games(self):
        _,value,_,project,_,_=self.targets['exe6']
        for other in ['exe6f','exegp','exe45-pvp']:
            draft=copy.deepcopy(project);draft['target_profile']=other
            with self.assertRaises(ValueError):resolve_pools(draft,value)

    def test_manager_exports_both_variants_and_keeps_projects_separate(self):
        with tempfile.TemporaryDirectory() as temp:
            m=Manager(temp,target='exe6')
            try:
                for key,(base,_,_,project,_,_) in self.targets.items():
                    m.select_target(key);finish(m,m.load(['exe1','exegp']))
                    self.assertFalse(m.state()['patch_required']);self.assertNotIn('pvp',m.inputs)
                    self.assertEqual(len(m.project['pools']),37)
                    for event,pool in project['pools'].items():m.project['pools'][event]=copy.deepcopy(pool)
                    job=finish(m,m.export(m.project));rom=m.file(job['id'],'unified.gba').read_bytes()
                    self.assertEqual(apply_bps(base,m.file(job['id'],'unified.bps').read_bytes())[0],rom)
                    manifest=json.loads((Path(job['result']['directory'])/'build.json').read_text())
                    self.assertEqual(manifest['source_patches'],{})
                    self.assertEqual(manifest['target_profile'],key)
                    self.assertEqual(m.project_path.name,f'project-{key}.json')
                m.select_target('exe6');finish(m,m.load(['exe1','exegp']))
                self.assertEqual(m.project['pools']['21'],self.targets['exe6'][3]['pools']['21'])
            finally:m.close()


if __name__=='__main__':unittest.main()
