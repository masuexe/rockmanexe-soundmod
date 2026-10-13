"""Integration tests against the supplied original GP and ChipControl archive."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from prepatch import apply_prepatch,find_prepatch
from target_profiles import target_profile,identify_target,check_layout
from manager_backend import Manager
from original_catalog import catalog_originals
from build_unified import build_catalog
from scan_audio import apply_bps
from test_manager import finish

ROMS=ROOT.parent/'roms';PATCHES=ROOT.parent/'patches'


@unittest.skipUnless((ROMS/'exegp.gba').is_file() and (PATCHES/'MegaManBCC-ChipControl-Ver1.1.0.zip').is_file() and (ROMS/'exe1.gba').is_file(),'local ChipControl inputs unavailable')
class ChipControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.profile=target_profile('exegp-chipcontrol')
        cls.base=(ROMS/'exegp.gba').read_bytes()
        cls.filename,cls.patch=find_prepatch(cls.profile,[PATCHES])
        cls.target,cls.info=apply_prepatch(cls.base,cls.patch,cls.profile)
        cls.donors={'exe1':(ROMS/'exe1.gba').read_bytes()}
        cls.value,cls.reports=catalog_originals(cls.base,cls.target,cls.donors)
        cls.project={'schema_version':1,'target_profile':'exegp-chipcontrol','pools':{
            str(i):{'tracks':['exe1:0','native-exegp:'+str(i)],'selector_shift':0} for i in [1,12,13,14]}}
        cls.output,_,cls.manifest=build_catalog(cls.base,cls.target,cls.value,cls.reports,cls.donors,cls.project,selected_only=True)

    def test_pinned_identity_layout_and_patch_bytes(self):
        self.assertEqual(identify_target(self.target)['key'],'exegp-chipcontrol')
        check_layout(self.target,self.profile['layout'])
        self.assertEqual(self.target[0x160604:0x160BA8],self.base[0x160604:0x160BA8])
        with self.assertRaisesRegex(ValueError,'supported version'):
            apply_prepatch(self.base,self.patch+b'x',self.profile)
        english=find_prepatch({**self.profile,'patch_filename':'MegaManBCC-ChipControl-Ver1.1.0-English.ips'},[PATCHES])[1]
        with self.assertRaises(ValueError):apply_prepatch(self.base,english,self.profile)

    def test_music_writes_do_not_intersect_chipcontrol_records(self):
        for a,b in self.info['write_ranges']:
            for c,d in self.manifest['declared_prefix_ranges']:
                self.assertFalse(a<d and c<b,(hex(a),hex(b),hex(c),hex(d)))
            self.assertEqual(self.output[a:b],self.target[a:b])
        self.assertEqual([r['trigger_id'] for r in self.manifest['hook']['rules']],[1,12,13,14])
        self.assertEqual(len(self.manifest['imports']),1)

    def test_manager_preserves_gp_pools_and_exports_one_original_rom_bps(self):
        with tempfile.TemporaryDirectory() as temp:
            m=Manager(temp,target='exegp')
            try:
                finish(m,m.load(['exe1']))
                gp=copy.deepcopy(self.project);gp['target_profile']='exegp'
                m.save_project(gp)
                m.select_target('exegp-chipcontrol')
                self.assertTrue(m.state()['patch_required'])
                self.assertEqual(m.state()['patch_accept'],'.ips')
                self.assertEqual(m.inputs['pvp'][0],self.filename)
                self.assertEqual(m.project_path.name,'project-exegp.json')
                before=copy.deepcopy(m.project)
                with self.assertRaises(ValueError):m.upload('pvp','wrong.ips',b'PATCHEOF')
                self.assertEqual(m.project,before)
                finish(m,m.load(['exe1']))
                for event,pool in gp['pools'].items():self.assertEqual(m.project['pools'][event],pool)
                job=finish(m,m.export(m.project))
                rom=m.file(job['id'],'unified.gba').read_bytes()
                patch=m.file(job['id'],'unified.bps').read_bytes()
                expected,_,_=build_catalog(self.base,self.target,self.value,self.reports,self.donors,m.project,selected_only=True)
                self.assertEqual(rom,expected)
                self.assertEqual(apply_bps(self.base,patch)[0],rom)
                manifest=json.loads((Path(job['result']['directory'])/'build.json').read_text())
                self.assertEqual(set(manifest['source_patches']),{'chipcontrol'})
                self.assertEqual(manifest['source_patches']['chipcontrol']['format'],'ips')
                m.select_target('exegp');finish(m,m.load(['exe1']))
                for event,pool in gp['pools'].items():self.assertEqual(m.project['pools'][event],pool)
            finally:m.close()


if __name__=='__main__':unittest.main()
