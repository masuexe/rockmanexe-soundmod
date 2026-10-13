"""Regression and cross-game export checks for the shared target backend."""
import copy
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from original_catalog import catalog_originals, PROFILES
from target_profiles import target_profile, check_layout, selector_value
from build_unified import build_catalog, resolve_pools
from manager_backend import Manager
from scan_audio import apply_bps, fingerprint, ROM_BASE
from test_manager import finish

ROMS = ROOT.parent/'roms'
PATCHES = ROOT.parent/'patches'


class LayoutTests(unittest.TestCase):
    def test_profile_copies_do_not_modify_shared_layout(self):
        profile = target_profile('exegp')
        profile['layout']['table_references'].clear()
        self.assertEqual(len(target_profile('exegp')['layout']['table_references']),7)
        self.assertEqual(target_profile('exe45-pvp')['audio_layout'],target_profile('bn45-us-pvp')['audio_layout'])

    def test_clock_mixer_low_byte_covers_all_values(self):
        layout = target_profile('exegp')['layout']
        self.assertEqual(len({selector_value(layout,i) for i in range(256)}),256)
        self.assertEqual(selector_value(layout,1),33)
        self.assertEqual(selector_value(layout,2),66)
        self.assertEqual(selector_value(target_profile('exe45-pvp')['layout'],255),255)


@unittest.skipUnless(all((ROMS/p).is_file() for p in ['exe45.gba','exegp.gba','exe1.gba']) and all((PATCHES/p).is_file() for p in ['exe45_pvp_0.6.0.bps','bn45_us_pvp_0.6.0.bps']), 'local target inputs unavailable')
class MultiTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gp=(ROMS/'exegp.gba').read_bytes()
        cls.donors={'exe1':(ROMS/'exe1.gba').read_bytes(),'exegp':cls.gp}
        cls.value,cls.reports=catalog_originals(cls.gp,cls.gp,cls.donors)
        cls.project={'schema_version':1,'target_profile':'exegp','pools':{'1':{'tracks':['native-exegp:1','exe1:0','exegp:1']}}}
        cls.output,_,cls.manifest=build_catalog(cls.gp,cls.gp,cls.value,cls.reports,cls.donors,cls.project,selected_only=True)

    def test_exe45_both_versions_remain_byte_identical(self):
        base=(ROMS/'exe45.gba').read_bytes()
        playlist={'schema_version':1,'pools':{'55':{'tracks':['exegp:1']},'98':{'tracks':['pvp:98','exegp:1']}}}
        for filename,sha in [('exe45_pvp_0.6.0.bps','a33019c572fed9831062197d09bfabf4d72b99f5f9afd4b504fe7b982ab5e212'),('bn45_us_pvp_0.6.0.bps','ac8e91bb9ba07bd34aa7b8b23f30f46781e3585d4e7f350a5139347af9fb0373')]:
            target,_=apply_bps(base,(PATCHES/filename).read_bytes())
            value,reports=catalog_originals(base,target,{'exegp':self.gp})
            output,_,_=build_catalog(base,target,value,reports,{'exegp':self.gp},playlist,selected_only=True)
            self.assertEqual(fingerprint(output)['sha256'],sha)

    def test_gp_table_effects_and_unmodified_prefix_preserved(self):
        layout=target_profile('exegp')['layout'];table=self.manifest['target_table_file_offset']
        self.assertEqual(self.output[table:table+170*8],self.gp[layout['table_offset']:layout['table_offset']+170*8])
        expected=bytearray(self.gp)
        for start,end in self.manifest['declared_prefix_ranges']:expected[start:end]=self.output[start:end]
        self.assertEqual(self.output[:len(self.gp)],expected)
        for offset in layout['table_references']:
            self.assertEqual(struct.unpack_from('<I',self.output,offset)[0],ROM_BASE+table)
        for key in ('exe1:0','exegp:1'):
            index=next(r['target_index'] for r in self.value['entries'] if r['key']==key)
            self.assertEqual(struct.unpack_from('<IHH',self.output,table+index*8)[1:],(0,0))
        self.assertEqual(self.value['target_track_capacity'],10)
        self.assertTrue(next(r for r in self.value['entries'] if r['key']=='exegp:5')['playlist_eligible'])
        self.assertEqual(len(self.manifest['imports']),2)

    def test_wrong_game_projects_and_catalogs_rejected(self):
        project=copy.deepcopy(self.project);project['target_profile']='exe45-pvp'
        with self.assertRaisesRegex(ValueError,'different target'):resolve_pools(project,self.value)
        catalog=copy.deepcopy(self.value);catalog['target_profile']='exe45-pvp'
        with self.assertRaisesRegex(ValueError,'different target'):build_catalog(self.gp,self.gp,catalog,self.reports,self.donors,self.project)
        with self.assertRaisesRegex(ValueError,'not native target music'):
            resolve_pools({'schema_version':1,'pools':{'100':{'tracks':['exe1:0']}}},self.value)

    def test_changed_table_literal_rejected_before_patching(self):
        data=bytearray(self.gp);data[0x2FFC]^=1
        with self.assertRaisesRegex(ValueError,'table reference'):check_layout(data,target_profile('exegp')['layout'])

    def test_saved_gp_title_project_gains_events_without_changing_pools(self):
        with tempfile.TemporaryDirectory() as temp:
            m = Manager(temp, target='exegp')
            try:
                old = copy.deepcopy(self.project)
                old['pools']['1']['tracks'] = ['exe1:0', 'exe1:0', 'native-exegp:1']
                old['pools']['1']['selector_shift'] = 2
                old['pools']['12'] = {'tracks':['exegp:5'], 'selector_shift':3}
                m.project_path.write_text(json.dumps(old))
                m.select_target('exegp')
                finish(m, m.load(['exe1','exegp']))
                self.assertEqual(len(m.project['pools']),16)
                for trigger, pool in old['pools'].items():
                    self.assertEqual(m.project['pools'][trigger],pool)
                self.assertEqual(m.project['pools']['13']['tracks'],['native-exegp:13'])
                self.assertIn('Added 14 native music events',m.project_notice)
                m.save_project(m.project)
                m.select_target('exegp')
                finish(m, m.load(['exe1','exegp']))
                self.assertEqual(m.project_notice,'')
                self.assertEqual(m.project['pools']['12'],old['pools']['12'])
            finally:
                m.close()

    def test_gp_communication_group_exports_all_native_choices(self):
        group = self.value['event_groups']['communication']
        self.assertEqual(group['events'],[12,13,14])
        # Native communication selection: RNG -> modulo 3 -> add 12.
        self.assertEqual(self.gp[0x489CC:0x489D8].hex(),'032105f00ff90c300004000c')
        project = {'schema_version':1,'target_profile':'exegp','pools':{
            str(i):{'tracks':['exe1:0','native-exegp:13']} for i in group['events']}}
        output, _, manifest = build_catalog(self.gp,self.gp,self.value,self.reports,self.donors,project,selected_only=True)
        self.assertEqual([r['trigger_id'] for r in manifest['hook']['rules']],group['events'])
        self.assertEqual(len(manifest['imports']),1)
        table = manifest['target_table_file_offset']
        self.assertEqual(output[table:table+170*8],self.gp[0x160658:0x160658+170*8])

    def test_manager_target_switch_export_and_project_isolation(self):
        with tempfile.TemporaryDirectory() as temp:
            m=Manager(temp)
            try:
                finish(m,m.load(['exegp']))
                jp=copy.deepcopy(m.project);jp['pools']['55']['tracks']=['exegp:1'];m.save_project(jp)
                m.select_target('exegp')
                self.assertNotIn('pvp',m.inputs)
                finish(m,m.load(['exe1','exegp']))
                self.assertEqual(m.project['target_profile'],'exegp')
                self.assertEqual(len(m.project['pools']),16)
                job=finish(m,m.export(self.project))
                rom=m.file(job['id'],'unified.gba').read_bytes()
                self.assertEqual(rom,self.output)
                patch=m.file(job['id'],'unified.bps').read_bytes()
                self.assertEqual(apply_bps(self.gp,patch)[0],rom)
                manifest=json.loads((Path(job['result']['directory'])/'build.json').read_text())
                self.assertEqual(manifest['source_patches'],{})
                with self.assertRaises(ValueError):m.save_project(jp)
                m.select_target('exe45-pvp');finish(m,m.load(['exegp']))
                self.assertEqual(m.project['pools']['55']['tracks'],['exegp:1'])
                m.select_target('exegp')
            finally:m.close()
            restored=Manager(temp)
            try:
                self.assertEqual(restored.selected_target,'exegp')
                self.assertEqual(restored.project['pools'],self.project['pools'])
            finally:restored.close()


if __name__=='__main__':unittest.main()
