import copy
import json
from pathlib import Path
import struct
import sys
import tempfile
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from target_profiles import TARGETS,identify_target,valid_manifest_target
from scan_audio import apply_bps,fingerprint
from original_catalog import catalog_originals
from build_unified import build_catalog,build
from manager_backend import Manager

PATCH=ROOT.parent/'patches/bn45_us_pvp_0.6.0.bps'
BASE=ROOT.parent/'roms/exe45.gba'
GP=ROOT.parent/'roms/exegp.gba'


class TargetManifestTests(unittest.TestCase):
    def test_manifest_identity_must_match_profile_not_just_an_allowed_hash(self):
        manifest={'target_profile':'bn45-us-pvp','target_base_fingerprint':copy.deepcopy(TARGETS['bn45-us-pvp']['fingerprint'])}
        self.assertTrue(valid_manifest_target(manifest))
        manifest['target_profile']='exe45-pvp'
        self.assertFalse(valid_manifest_target(manifest))
        manifest['target_profile']='bn45-us-pvp'
        manifest['target_base_fingerprint']['crc32']='00000000'
        self.assertFalse(valid_manifest_target(manifest))


@unittest.skipUnless(all(p.is_file() for p in (PATCH,BASE,GP,ROOT/'references/exe45_pvp_0.6.0.bps')), 'English patch and local ROMs unavailable')
class EnglishPvPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=BASE.read_bytes();cls.gp=GP.read_bytes()
        cls.us,cls.info=apply_bps(cls.base,PATCH.read_bytes())
        cls.jp,_=apply_bps(cls.base,(ROOT/'references/exe45_pvp_0.6.0.bps').read_bytes())
        cls.value,cls.reports=catalog_originals(cls.base,cls.us,{'exegp':cls.gp})
        cls.playlist={'schema_version':1,'pools':{'55':{'tracks':['exegp:1'],'selector_shift':0},'98':{'tracks':['pvp:98','exegp:1'],'selector_shift':0}}}
        cls.output,cls.catalog,cls.manifest=build_catalog(cls.base,cls.us,cls.value,cls.reports,{'exegp':cls.gp},cls.playlist,selected_only=True)
    def test_same_original_source_and_exact_target(self):
        self.assertEqual(self.info['source_crc32'],'A646601B')
        self.assertEqual(identify_target(self.us)['key'],'bn45-us-pvp')
        modified=bytearray(self.us);modified[0x504]^=1
        with self.assertRaises(ValueError):identify_target(bytes(modified))
    def test_verified_shared_audio_code_and_native_music(self):
        for start,end in [(0x504,0x508),(0xEE344,0xEEA80),(0x7954,0x7970),(0x4479A,0x447B0),(0xC7A3C,0xC7A48)]:
            self.assertEqual(self.us[start:end],self.jp[start:end])
        music=[r for r in self.value['entries'] if r['source']=='pvp' and r['playlist_eligible']]
        self.assertEqual(len(music),48)
        for row in music:
            offset=0x135214+row['source_index']*8
            self.assertEqual(self.us[offset:offset+8],self.jp[offset:offset+8])
        self.assertEqual(self.us[0xC7A3F],98)
    def test_english_prefix_and_its_own_effect_pointers_preserved(self):
        expected=bytearray(self.us)
        for start,end in self.manifest['declared_prefix_ranges']:expected[start:end]=self.output[start:end]
        self.assertEqual(self.output[:len(self.us)],expected)
        table=self.manifest['target_table_file_offset']
        self.assertEqual(self.output[table:table+499*8],self.us[0x135214:0x1361AC])
        for index in range(69,81):
            self.assertEqual(self.output[table+index*8:table+(index+1)*8],self.us[0x135214+index*8:0x135214+(index+1)*8])
        self.assertNotEqual(self.us[0x135214+69*8:0x135214+70*8],self.jp[0x135214+69*8:0x135214+70*8])
        self.assertEqual(self.manifest['target_profile'],'bn45-us-pvp')
        self.assertTrue(valid_manifest_target(self.manifest))
    def test_manager_load_export_and_bps_round_trip(self):
        with tempfile.TemporaryDirectory() as temp:
            m=Manager(temp,pvp_patch=PATCH)
            try:
                def finish(job):
                    while m.job(job['job_id'])['status']=='running':time.sleep(.02)
                    value=m.job(job['job_id']);self.assertEqual(value['status'],'done',value);return value
                finish(m.load(['exegp']))
                self.assertIn('English',m.state()['target_label'])
                job=finish(m.export(self.playlist))
                rom=m.file(job['id'],'unified.gba').read_bytes();patch=m.file(job['id'],'unified.bps').read_bytes()
                self.assertEqual(apply_bps(self.base,patch)[0],rom)
                self.assertEqual(rom,self.output)
                manifest=json.loads((Path(job['result']['directory'])/'build.json').read_text())
                self.assertEqual(manifest['target_profile'],'bn45-us-pvp')
            finally:m.close()
    @unittest.skipUnless((ROOT/'references/exe45_soundmod.bps').is_file(), 'legacy Soundmod patch unavailable')
    def test_legacy_soundmod_builder_accepts_english_target(self):
        sound,_=apply_bps(self.base,(ROOT/'references/exe45_soundmod.bps').read_bytes())
        output,value,manifest=build(self.base,self.us,sound,self.gp,json.loads((ROOT/'config/playlist.json').read_text()))
        self.assertEqual(manifest['target_profile'],'bn45-us-pvp')
        table=manifest['target_table_file_offset']
        self.assertEqual(output[table:table+499*8],self.us[0x135214:0x1361AC])


if __name__=='__main__':unittest.main()
