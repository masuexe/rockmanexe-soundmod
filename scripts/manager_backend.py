"""Local manager services. All builds reuse the version-pinned unified backend."""
from concurrent.futures import ThreadPoolExecutor
import copy
import json
from pathlib import Path
import threading
import uuid

from build_unified import build_catalog, resolve_pools
from render_preview import capture_preview
from realtime_audio import RealtimeEngine
from scan_audio import apply_bps, fingerprint
from transplant_song import make_bps
from unified_catalog import write_catalog
from original_catalog import catalog_originals, PROFILES, identify
from target_profiles import TARGETS, target_profile, identify_target
from prepatch import apply_prepatch, find_prepatch, prepatch_available
from nds_catalog import (NDS_DIRECTORY, NDS_PROFILES, SONGS, identify_nds, discover_nds,
                         add_nds_catalog, prepare_nds_catalog, annotate_nds_manifest)
from nds_conversion_cache import NdsConversionCache

ROOT = Path(__file__).resolve().parents[1]
ROM_DIRECTORY = ROOT.parent / 'roms'
PATCH_DIRECTORY = ROOT.parent / 'patches'
DEFAULT_PVP_PATCH = PATCH_DIRECTORY / 'exe45_pvp_0.6.0.bps'
if not DEFAULT_PVP_PATCH.is_file(): DEFAULT_PVP_PATCH = ROOT / 'references/exe45_pvp_0.6.0.bps'
INPUTS = {'base': ROM_DIRECTORY / 'exe45.gba', 'pvp': DEFAULT_PVP_PATCH}
INPUTS.update({f'rom:{key}': ROM_DIRECTORY / profile['filename'] for key, profile in PROFILES.items()})
INPUTS.update({f'rom:{key}': NDS_DIRECTORY / profile['filename'] for key, profile in NDS_PROFILES.items()})
SOURCE_PROFILES = {**PROFILES, **NDS_PROFILES}



class Manager:
    def __init__(self, directory=None, preload=True, mgba='/usr/games/mgba', realtime=None, pvp_patch=None, target=None):
        if pvp_patch is not None and target is not None:
            raise ValueError('Use either a target preset or a custom pre-patch, not both')
        self.directory = Path(directory or ROOT / 'out/manager')
        self.directory.mkdir(parents=True, exist_ok=True)
        self.mgba = mgba
        self.realtime = RealtimeEngine(realtime or ROOT / 'out/realtime/exe-realtime', self.directory / 'realtime')
        self.lock = threading.RLock()
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.inputs = {}
        self.revision = 0
        self.value = None
        self.decoded = None
        self.jobs = {}
        self.active = None
        self.preview_cache = {}
        self.nds_cache = NdsConversionCache(self.directory / 'nds-cache')
        self.nds_sources = {}
        self.live_request = 0
        self.default_project = self._default_project(target_profile('exe45-pvp'))
        self.project_notice = ''
        self.project = copy.deepcopy(self.default_project)
        self.names_path = self.directory / 'track-names.json'
        self.project_path = self.directory / 'project.json'
        self.target_path = self.directory / 'target.json'
        self.selected_target = 'exe45-pvp'
        self.names = json.loads(self.names_path.read_text()) if self.names_path.exists() else {}
        if self.project_path.exists():
            self.project = json.loads(self.project_path.read_text())
        self.source_paths = {}
        self.selection_path = self.directory / 'sources.json'
        saved = json.loads(self.selection_path.read_text()) if self.selection_path.exists() else None
        if preload:
            for role in ('base', 'pvp'):
                path = INPUTS[role]
                if path.exists(): self.inputs[role] = (path.name, path.read_bytes())
            for key, profile in PROFILES.items():
                uploaded = self.directory / 'uploaded-roms' / profile['filename']
                path = uploaded if uploaded.exists() else INPUTS['rom:' + key]
                if path.exists(): self.source_paths[key] = (path.name, path)
            self.source_paths.update(discover_nds(NDS_DIRECTORY, self.directory / 'uploaded-roms'))
        if pvp_patch is not None:
            patch_path = Path(pvp_patch)
            self.inputs['pvp'] = (patch_path.name,patch_path.read_bytes())
        self.selected_sources = set(saved['sources']) if saved and isinstance(saved.get('sources'), list) else set(self.source_paths) & PROFILES.keys()
        self.selected_sources.intersection_update(SOURCE_PROFILES)

        saved_target = json.loads(self.target_path.read_text()).get('target') if self.target_path.exists() else None
        if target is not None:
            self.select_target(target, persist=False)
        elif pvp_patch is not None and 'base' in self.inputs:
            decoded, _ = apply_bps(self.inputs['base'][1],self.inputs['pvp'][1])
            self.selected_target = identify_target(decoded)['key']
        elif saved_target in TARGETS and preload:
            self.select_target(saved_target, persist=False)
        if self.selected_target not in ('exe6', 'exe6f'):
            self.selected_sources.difference_update(NDS_PROFILES)

    def select_target(self, key, persist=True):
        if key not in TARGETS: raise ValueError('Choose a supported target ROM')
        with self.lock:
            if self.active: raise ValueError('Wait for the current task before changing targets')
            profile = target_profile(key)
            base_path = ROM_DIRECTORY / profile['filename']
            base = base_path.read_bytes() if base_path.is_file() else None
            if base is not None and fingerprint(base)['sha256'] != profile['base_sha256']:
                raise ValueError('Target input ROM does not match the supported revision')
            replacement = {'base':(base_path.name,base)} if base is not None else {}
            if profile['patch_filename']:
                patch_input = find_prepatch(profile,[PATCH_DIRECTORY,ROOT / 'references'])
                if patch_input:
                    if base is not None: apply_prepatch(base,patch_input[1],profile)
                    replacement['pvp'] = patch_input
            project_path = self.directory / profile.get('project_filename',
                'project.json' if profile['audio_layout']=='exe45-audio-v1' else f'project-{key}.json')
            default_project = self._default_project(profile)
            project = json.loads(project_path.read_text()) if project_path.exists() else copy.deepcopy(default_project)
            self.selected_target = key
            if key not in ('exe6', 'exe6f'):
                self.selected_sources.difference_update(NDS_PROFILES)
            self.inputs = replacement
            self._invalidate()
            self.project_path, self.default_project, self.project = project_path, default_project, project
            self.project_notice = ''
            if persist:
                temporary = self.target_path.with_suffix('.tmp')
                temporary.write_text(json.dumps({'schema_version':1,'target':key},indent=2)+'\n')
                temporary.replace(self.target_path)
        return self.state()

    @staticmethod
    def _default_project(profile, value=None):
        layout = profile['layout']
        events = layout['default_events']
        if events is None:
            events = [r['source_index'] for r in value['entries'] if r['source']==layout['native_source'] and r['playlist_eligible']] if value else [layout['preview_trigger']]
        pools = {str(i):{'tracks':[f"{layout['native_source']}:{i}"],'selector_shift':0} for i in events}
        if value:
            for key, scene in layout.get('scene_events',{}).items():
                pools[key] = {'tracks':[f"{layout['native_source']}:{scene['native_event']}"],'selector_shift':0}
        return {'schema_version':1,'target_profile':profile['key'],'pools':pools}

    def _invalidate(self):
        self.revision += 1
        self.value = self.decoded = None
        self.nds_sources = {}
        self.inputs = {key:value for key,value in self.inputs.items() if not key.startswith('rom:')}
        self.preview_cache.clear()
        self.realtime.stop()

    def select_sources(self, sources):
        with self.lock:
            if self.active: raise ValueError('Wait for the current task before changing sources')
            if not isinstance(sources, list) or any(not isinstance(key, str) or key not in self.source_paths for key in sources):
                raise ValueError('Select available original ROM sources')
            if self.selected_target not in ('exe6', 'exe6f') and any(key in NDS_PROFILES for key in sources):
                raise ValueError('NDS music currently requires Japanese EXE6 Gregar or Falzar')
            selected = set(sources)
            if selected != self.selected_sources:
                self.selected_sources = selected
                self._invalidate()
            temporary = self.selection_path.with_suffix('.tmp')
            temporary.write_text(json.dumps({'schema_version':1,'sources':sorted(selected)}, indent=2) + '\n')
            temporary.replace(self.selection_path)
        return self.state()

    def _reconcile_project(self, value, draft):
        eligible = {row['key'] for row in value['entries'] if row['playlist_eligible']}
        profile = target_profile(value['target_profile'])
        unchanged_default = draft == self.default_project
        self.default_project = self._default_project(profile,value)
        project = copy.deepcopy(self.default_project if unchanged_default else draft)
        previous = project.get('target_profile')
        if previous and (previous not in TARGETS or TARGETS[previous]['audio_layout'] != profile['audio_layout']):
            project = copy.deepcopy(self.default_project)
        project['target_profile'] = profile['key']
        removed = fallback = 0
        added = 0
        try:
            # Catalog-derived events become known only after loading the ROM.
            # Older saved projects may contain just the preview/title event.
            if profile['layout']['default_events'] is None:
                for trigger, pool in self.default_project['pools'].items():
                    if trigger not in project['pools']:
                        scene = value.get('scene_events',{}).get(trigger)
                        inherited = project['pools'].get(str(scene['native_event'])) if scene else None
                        project['pools'][trigger] = copy.deepcopy(inherited or pool)
                        added += 1
            for trigger, pool in project['pools'].items():
                old = pool['tracks']
                if not isinstance(old, list): raise ValueError('Invalid tracks list')
                tracks = [key for key in old if isinstance(key, str) and key in eligible]
                removed += len(old) - len(tracks)
                if tracks != old: pool['selector_shift'] = 0
                if not tracks:
                    scene = value.get('scene_events',{}).get(trigger)
                    native_event = scene['native_event'] if scene else int(trigger)
                    tracks = [f"{value['native_source']}:{native_event}"]
                    pool['selector_shift'] = 0
                    fallback += 1
                pool['tracks'] = tracks
            resolve_pools(project, value)
        except (ValueError, KeyError, TypeError, AttributeError):
            self.project = copy.deepcopy(self.default_project)
            self.project_notice = 'Invalid previous pools: native playback defaults restored. Save to keep the new project.'
        else:
            self.project = {'schema_version':1,'target_profile':profile['key'],'pools':project['pools']}
            self.project_notice = f'Removed {removed} unavailable playlist entries; {fallback} empty pools restored to native target music. Save to keep these changes.' if removed or fallback else ''
            if added:
                kind = 'music events' if value.get('scene_events') else 'native music events'
                self.project_notice += (' ' if self.project_notice else '') + f'Added {added} {kind}; existing pools retained. Save to keep these changes.'

    def state(self):
        with self.lock:
            value = copy.deepcopy(self.value)
            if value:
                for row in value['entries']:
                    row['name'] = self.names.get(row['key'], row.get('name') or '')
            project = copy.deepcopy(self.project)
            known = {r['key'] for r in value['entries']} if value else set(self.names)
            project['names'] = {key:name for key,name in self.names.items() if key in known}
            return {'inputs': {role: {'filename': value[0], 'size_bytes': len(value[1])} for role, value in self.inputs.items()},
                    'revision': self.revision, 'catalog': value, 'project': project,
                    'selected_target':self.selected_target,
                    'target_options':[{'key':key,'label':profile['label'],'available':(ROM_DIRECTORY/profile['filename']).is_file() and prepatch_available(profile,[PATCH_DIRECTORY,ROOT/'references'])} for key,profile in TARGETS.items()],
                    'patch_required':bool(TARGETS[self.selected_target]['patch_filename']),
                    'patch_label':TARGETS[self.selected_target].get('patch_label','PvP BPS pre-patch'),
                    'patch_accept':'.ips' if TARGETS[self.selected_target].get('patch_format')=='ips' else '.bps',
                    'active_job': self.jobs.get(self.active) if self.active else None,
                    'preview_available': Path(self.mgba).is_file(), 'realtime_available':self.realtime.available(), 'rom_directory':str(ROM_DIRECTORY),
                    'source_profiles':{key:profile['label'] for key,profile in SOURCE_PROFILES.items()},
                    'nds_library_song_count':len(SONGS),
                    'project_notice':self.project_notice, 'target_label':self.value.get('target_label') if self.value else None, 'selected_sources':sorted(self.selected_sources & self.source_paths.keys()),
                    'source_options':[{'key':key,'label':SOURCE_PROFILES[key]['label'],'filename':filename,
                                       'size_bytes':path.stat().st_size if path.is_file() else 0,
                                       'loaded':self.value is not None and (key in self.decoded[2] or key in self.value.get('nds_sources',{}))}
                                      for key,(filename,path) in sorted(self.source_paths.items())
                                      if key not in NDS_PROFILES or self.selected_target in ('exe6', 'exe6f')]}

    def upload(self, role, filename, data):
        if role == 'rom':
            try:
                key = identify(data)
            except ValueError:
                key = identify_nds(data)
            role = 'rom:' + key
        if role not in INPUTS or not data or len(data) > 32 * 1024 * 1024:
            raise ValueError('Choose a supported ROM, BPS or IPS file, no larger than 32 MiB')
        with self.lock:
            if self.active:
                raise ValueError('Wait for the current task before changing files')
            filename = filename.replace('\\', '/').rsplit('/', 1)[-1][:200]
            if role.startswith('rom:'):
                key = role[4:]
                if key in NDS_PROFILES:
                    if self.selected_target not in ('exe6', 'exe6f'):
                        raise ValueError('Select Japanese EXE6 Gregar or Falzar before adding NDS music')
                    if identify_nds(data) != key:
                        raise ValueError('NDS source does not match its selected game')
                directory = self.directory / 'uploaded-roms'
                directory.mkdir(exist_ok=True)
                path = directory / SOURCE_PROFILES[key]['filename']
                temporary = path.with_suffix('.tmp')
                temporary.write_bytes(data)
                temporary.replace(path)
                self.source_paths[key] = (filename, path)
                self.selected_sources.add(key)
                self._invalidate()
                self.select_sources(sorted(self.selected_sources & self.source_paths.keys()))
            else:
                if role=='base':
                    if fingerprint(data)['sha256'] != TARGETS[self.selected_target]['base_sha256']:
                        raise ValueError('ROM does not match the selected target revision')
                if role=='pvp' and not TARGETS[self.selected_target]['patch_filename']:
                    raise ValueError('This target uses its original ROM without a pre-patch')
                if role=='pvp' and TARGETS[self.selected_target].get('patch_format')=='ips':
                    profile = target_profile(self.selected_target)
                    if fingerprint(data)['sha256'] != profile['patch_sha256']:
                        raise ValueError('Pre-patch does not match ChipControl 1.1.0 Japanese IPS')
                self.inputs[role] = (filename, bytes(data))
                self._invalidate()

        result = self.state()
        if role.startswith('rom:'): result['added_source'] = role[4:]
        return result

    def _start(self, kind, function):
        with self.lock:
            if self.active:
                raise ValueError('Another task is already running')
            job_id = uuid.uuid4().hex
            self.jobs[job_id] = {'id': job_id, 'kind': kind, 'status': 'running', 'message': 'Working…'}
            self.active = job_id

        def run():
            try:
                result = function(job_id)
            except Exception as exc:
                with self.lock:
                    self.jobs[job_id].update(status='error', message=str(exc))
            else:
                with self.lock:
                    self.jobs[job_id].update(status='done', message='Ready', result=result)
            finally:
                with self.lock:
                    self.active = None
        self.executor.submit(run)
        return {'job_id': job_id}

    def job(self, job_id):
        with self.lock:
            if job_id not in self.jobs:
                raise ValueError('Task not found')
            return copy.deepcopy(self.jobs[job_id])

    def load(self, sources=None, project=None):
        if project is not None and (not isinstance(project,dict) or project.get('schema_version') != 1 or not isinstance(project.get('pools'),dict) or not project['pools']):
            raise ValueError('Project requires schema_version 1 and nonempty pools')
        if sources is not None: self.select_sources(sources)
        with self.lock:
            if 'base' not in self.inputs or (TARGETS[self.selected_target]['patch_filename'] and 'pvp' not in self.inputs):
                raise ValueError('Select the target ROM and its required pre-patch')
            inputs, revision = dict(self.inputs), self.revision
            profile = target_profile(self.selected_target)
            draft = copy.deepcopy(project if project is not None else self.project)
            source_paths = {key:self.source_paths[key] for key in sorted(self.selected_sources & self.source_paths.keys())}
        def task(_):
            base = inputs['base'][1]
            if 'pvp' not in inputs:
                pvp, pvp_info = base, None
            elif profile.get('patch_format') == 'ips':
                pvp, pvp_info = apply_prepatch(base,inputs['pvp'][1],profile)
            else:
                pvp, pvp_info = apply_bps(base,inputs['pvp'][1])
            donors = {key:path.read_bytes() for key,(_,path) in source_paths.items() if key in PROFILES}
            nds_originals = {key:path.read_bytes() for key,(_,path) in source_paths.items() if key in NDS_PROFILES}
            value, reports = catalog_originals(base, pvp, donors)
            add_nds_catalog(value, nds_originals)
            with self.lock:
                if revision != self.revision:
                    raise ValueError('Files changed; load tracks again')
                self.selected_target = value['target_profile']
                self._reconcile_project(value, draft)
                self.inputs.update({'rom:' + key:(source_paths[key][0],data) for key,data in donors.items()})
                self.value = value
                self.decoded = (base, pvp, donors, pvp_info, reports)
                self.nds_sources = {key:source_paths[key][1] for key in nds_originals}
            return {'tracks': sum(row['playlist_eligible'] for row in value['entries'])}
        return self._start('catalog', task)

    def _loaded(self):
        if self.value is None or self.decoded is None:
            raise ValueError('Load tracks first')

    def _build_snapshot(self, value, decoded, paths, project):
        base, pvp, donors, _, reports = decoded
        keys = {key for rule in resolve_pools(project, value) for key in rule['keys']}
        needed = {row['original_source'] for row in value['entries']
                  if row['key'] in keys and row.get('nds_selector')}
        originals = {}
        for key in sorted(needed):
            raw = paths[key].read_bytes()
            if fingerprint(raw) != value['nds_sources'][key]['rom_fingerprint']:
                raise ValueError('NDS source changed; load tracks again')
            originals[key] = raw
        prepared, reports, donors = prepare_nds_catalog(value, reports, donors, originals, base, keys, self.nds_cache)
        output, catalog, manifest = build_catalog(base, pvp, prepared, reports, donors, project, selected_only=True)
        annotate_nds_manifest(manifest, prepared)
        return output, catalog, manifest

    def save_project(self, project):
        with self.lock:
            self._loaded()
            if self.active:
                raise ValueError('Wait for the current task before changing the project')
            if not isinstance(project, dict):
                raise ValueError('Project must be a JSON object')
            resolve_pools(project, self.value)
            project = copy.deepcopy(project)
            for key, scene in self.value.get('scene_events',{}).items():
                if key not in project['pools']:
                    inherited = project['pools'].get(str(scene['native_event']))
                    project['pools'][key] = copy.deepcopy(inherited or {
                        'tracks':[f"{self.value['native_source']}:{scene['native_event']}"],'selector_shift':0})
            resolve_pools(project, self.value)
            if 'names' in project:
                self._validate_names(project['names'])
                self.names.update(project['names'])
            self.project = {'schema_version': 1, 'target_profile':self.value['target_profile'], 'pools': copy.deepcopy(project['pools'])}
            self.project_path.write_text(json.dumps(self.project, ensure_ascii=False, indent=2) + '\n')
            self.names_path.write_text(json.dumps(self.names, ensure_ascii=False, indent=2) + '\n')
        return self.state()

    def _validate_names(self, names):
        known = {row['key'] for row in self.value['entries']}
        if not isinstance(names, dict) or any(key not in known or not isinstance(name, str) or len(name) > 120 for key, name in names.items()):
            raise ValueError('Track names must match this catalog and be at most 120 characters')

    def name(self, key, name):
        with self.lock:
            self._loaded()
            self._validate_names({key: name})
            self.names[key] = name.strip()
            self.names_path.write_text(json.dumps(self.names, ensure_ascii=False, indent=2) + '\n')
        return {'key': key, 'name': name.strip()}

    def export(self, project):
        self.save_project(project)
        with self.lock:
            decoded = self.decoded
            value, paths = self.value, dict(self.nds_sources)
            project = copy.deepcopy(self.project)
            known = {r['key'] for r in self.value['entries']}
            names = {key:name for key,name in self.names.items() if key in known}
        def task(job_id):
            directory = self.directory / job_id
            directory.mkdir()
            base, _, _, pvp_info, _ = decoded
            output, catalog, manifest = self._build_snapshot(value, decoded, paths, project)
            patch = make_bps(base, output)
            if apply_bps(base, patch)[0] != output:
                raise AssertionError('Export verification failed')
            for row in catalog['entries']:
                row['name'] = names.get(row['key'], row.get('name') or '')
            patch_role = TARGETS[catalog['target_profile']].get('patch_role','pvp')
            manifest.update(source_patches={patch_role:pvp_info} if pvp_info else {}, manager=True, music_sources='original ROMs')
            (directory / 'unified.gba').write_bytes(output)
            (directory / 'unified.bps').write_bytes(patch)
            (directory / 'build.json').write_text(json.dumps(manifest, indent=2) + '\n')
            saved_project = {**project, 'names': names}
            (directory / 'project.json').write_text(json.dumps(saved_project, ensure_ascii=False, indent=2) + '\n')
            write_catalog(directory, catalog)
            return {'files': ['unified.bps', 'unified.gba', 'project.json', 'catalog.csv'],
                    'size_bytes': len(output), 'fingerprint': fingerprint(output), 'directory': str(directory)}
        return self._start('export', task)

    def preview(self, key, seconds=12):
        with self.lock:
            self._loaded()
            row = next((r for r in self.value['entries'] if r['key'] == key), None)
            if not row or not row['playlist_eligible']:
                raise ValueError('This entry is not available for music preview')
            if type(seconds) is not int or not 1 <= seconds <= 30:
                raise ValueError('Preview length must be 1..30 seconds')
            cache_key = (self.revision, key, seconds)
            if cache_key in self.preview_cache:
                return {'job_id': self.preview_cache[cache_key]}
            decoded = self.decoded
            value, paths = self.value, dict(self.nds_sources)
            target_id = row['target_index']
        def task(job_id):
            directory = self.directory / job_id
            directory.mkdir()
            config = {'schema_version': 1, 'pools': {str(value['preview_trigger']): {'tracks': [key], 'selector_shift': 0}}}
            output, _, manifest = self._build_snapshot(value, decoded, paths, config)
            rom = directory / 'preview.gba'
            rom.write_bytes(output)
            wav, info = capture_preview(rom, manifest, target_id, directory / 'capture', seconds, self.mgba)
            (directory / 'preview.wav').write_bytes(wav.read_bytes())
            with self.lock:
                self.preview_cache[cache_key] = job_id
            return {'files': ['preview.wav'], 'key': key, 'audio': info}
        return self._start('preview', task)

    def live_preview(self, key, sample_rate=48000):
        with self.lock:
            self._loaded()
            row = next((r for r in self.value['entries'] if r['key'] == key), None)
            if not row or not row['playlist_eligible']:
                raise ValueError('This entry is not available for music preview')
            base, pvp, donors, _, reports = self.decoded
            self.live_request += 1
            ticket, revision = self.live_request, self.revision
            if row.get('nds_selector'):
                snapshot = self.value, self.decoded, dict(self.nds_sources)
            elif row['source'] == self.value['native_source']:
                layout = target_profile(self.value['target_profile'])['layout']
                data, table, count = pvp, layout['table_offset'], layout['entry_count']
            else:
                profile = PROFILES[row['source']]
                data, table, count = donors[row['source']], profile['table_offset'], profile['entry_count']
            if not row.get('nds_selector'):
                return self.realtime.start(data,table,count,row['source_index'],sample_rate)
        # Conversion can be slow; state/stop/source-change requests stay responsive.
        value, decoded, paths = snapshot
        config = {'schema_version':1,'pools':{str(value['preview_trigger']):{'tracks':[key],'selector_shift':0}}}
        data, _, manifest = self._build_snapshot(value, decoded, paths, config)
        with self.lock:
            if revision != self.revision or ticket != self.live_request:
                raise ValueError('Preview cancelled or sources changed')
            return self.realtime.start(data,manifest['target_table_file_offset'],manifest['table_entry_count'],row['target_index'],sample_rate)

    def stop_live_preview(self, session_id=None):
        with self.lock:
            if session_id is None:
                self.live_request += 1
            return self.realtime.stop(session_id)

    def file(self, job_id, filename):
        with self.lock:
            job = self.jobs.get(job_id)
            if not job or job['status'] != 'done' or filename not in job['result'].get('files', []):
                raise ValueError('File not found')
        path = self.directory / job_id / filename
        if not path.is_file():
            raise ValueError('File not found')
        return path

    def close(self):
        with self.lock:
            self.revision += 1
            self.live_request += 1
            self.realtime.stop()
        self.executor.shutdown(wait=True)
