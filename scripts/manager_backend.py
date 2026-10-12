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

ROOT = Path(__file__).resolve().parents[1]
ROM_DIRECTORY = ROOT.parent / 'roms'
INPUTS = {'base': ROM_DIRECTORY / 'exe45.gba', 'pvp': ROOT / 'references/exe45_pvp_0.6.0.bps'}
INPUTS.update({f'rom:{key}': ROM_DIRECTORY / profile['filename'] for key, profile in PROFILES.items()})



class Manager:
    def __init__(self, directory=None, preload=True, mgba='/usr/games/mgba', realtime=None):
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
        self.default_project = {'schema_version':1,'pools':{str(i):{'tracks':[f'pvp:{i}'],'selector_shift':0} for i in (55,64,65,89,98,99)}}
        self.project_notice = ''
        self.project = copy.deepcopy(self.default_project)
        self.names_path = self.directory / 'track-names.json'
        self.project_path = self.directory / 'project.json'
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
        self.selected_sources = set(saved['sources']) if saved and isinstance(saved.get('sources'), list) else set(self.source_paths)
        self.selected_sources.intersection_update(PROFILES)

    def _invalidate(self):
        self.revision += 1
        self.value = self.decoded = None
        self.inputs = {key:value for key,value in self.inputs.items() if not key.startswith('rom:')}
        self.preview_cache.clear()
        self.realtime.stop()

    def select_sources(self, sources):
        with self.lock:
            if self.active: raise ValueError('Wait for the current task before changing sources')
            if not isinstance(sources, list) or any(not isinstance(key, str) or key not in self.source_paths for key in sources):
                raise ValueError('Select available original ROM sources')
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
        project = copy.deepcopy(draft)
        removed = fallback = 0
        try:
            for trigger, pool in project['pools'].items():
                old = pool['tracks']
                if not isinstance(old, list): raise ValueError('Invalid tracks list')
                tracks = [key for key in old if isinstance(key, str) and key in eligible]
                removed += len(old) - len(tracks)
                if tracks != old: pool['selector_shift'] = 0
                if not tracks:
                    tracks = [f'pvp:{int(trigger)}']
                    pool['selector_shift'] = 0
                    fallback += 1
                pool['tracks'] = tracks
            resolve_pools(project, value)
        except (ValueError, KeyError, TypeError, AttributeError):
            self.project = copy.deepcopy(self.default_project)
            self.project_notice = 'Invalid previous pools: native playback defaults restored. Save to keep the new project.'
        else:
            self.project = {'schema_version':1,'pools':project['pools']}
            self.project_notice = f'Removed {removed} unavailable playlist entries; {fallback} empty pools restored to native PvP music. Save to keep these changes.' if removed or fallback else ''

    def state(self):
        with self.lock:
            value = copy.deepcopy(self.value)
            if value:
                for row in value['entries']:
                    row['name'] = self.names.get(row['key'], '')
            project = copy.deepcopy(self.project)
            known = {r['key'] for r in value['entries']} if value else set(self.names)
            project['names'] = {key:name for key,name in self.names.items() if key in known}
            return {'inputs': {role: {'filename': value[0], 'size_bytes': len(value[1])} for role, value in self.inputs.items()},
                    'revision': self.revision, 'catalog': value, 'project': project,
                    'active_job': self.jobs.get(self.active) if self.active else None,
                    'preview_available': Path(self.mgba).is_file(), 'realtime_available':self.realtime.available(), 'rom_directory':str(ROM_DIRECTORY),
                    'source_profiles':{key:profile['label'] for key,profile in PROFILES.items()},
                    'project_notice':self.project_notice, 'selected_sources':sorted(self.selected_sources & self.source_paths.keys()),
                    'source_options':[{'key':key,'label':PROFILES[key]['label'],'filename':filename,
                                       'size_bytes':path.stat().st_size if path.is_file() else 0,'loaded':self.value is not None and key in self.decoded[2]}
                                      for key,(filename,path) in sorted(self.source_paths.items())]}

    def upload(self, role, filename, data):
        if role == 'rom':
            role = 'rom:' + identify(data)
        if role not in INPUTS or not data or len(data) > 32 * 1024 * 1024:
            raise ValueError('Choose a supported ROM or BPS file, no larger than 32 MiB')
        with self.lock:
            if self.active:
                raise ValueError('Wait for the current task before changing files')
            filename = filename.replace('\\', '/').rsplit('/', 1)[-1][:200]
            if role.startswith('rom:'):
                key = role[4:]
                directory = self.directory / 'uploaded-roms'
                directory.mkdir(exist_ok=True)
                path = directory / PROFILES[key]['filename']
                temporary = path.with_suffix('.tmp')
                temporary.write_bytes(data)
                temporary.replace(path)
                self.source_paths[key] = (filename, path)
                self.selected_sources.add(key)
                self._invalidate()
                self.select_sources(sorted(self.selected_sources & self.source_paths.keys()))
            else:
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
            if not {'base','pvp'} <= set(self.inputs):
                raise ValueError('Select the original EXE4.5 ROM and the PvP BPS patch')
            inputs, revision = dict(self.inputs), self.revision
            draft = copy.deepcopy(project if project is not None else self.project)
            source_paths = {key:self.source_paths[key] for key in sorted(self.selected_sources & self.source_paths.keys())}
        def task(_):
            base = inputs['base'][1]
            pvp, pvp_info = apply_bps(base, inputs['pvp'][1])
            donors = {key:path.read_bytes() for key,(_,path) in source_paths.items()}
            value, reports = catalog_originals(base, pvp, donors)
            with self.lock:
                if revision != self.revision:
                    raise ValueError('Files changed; load tracks again')
                self._reconcile_project(value, draft)
                self.inputs.update({'rom:' + key:(source_paths[key][0],data) for key,data in donors.items()})
                self.value = value
                self.decoded = (base, pvp, donors, pvp_info, reports)
            return {'tracks': sum(row['playlist_eligible'] for row in value['entries'])}
        return self._start('catalog', task)

    def _loaded(self):
        if self.value is None or self.decoded is None:
            raise ValueError('Load tracks first')

    def save_project(self, project):
        with self.lock:
            self._loaded()
            if self.active:
                raise ValueError('Wait for the current task before changing the project')
            if not isinstance(project, dict):
                raise ValueError('Project must be a JSON object')
            resolve_pools(project, self.value)
            if 'names' in project:
                self._validate_names(project['names'])
                self.names.update(project['names'])
            self.project = {'schema_version': 1, 'pools': copy.deepcopy(project['pools'])}
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
            project = copy.deepcopy(self.project)
            known = {r['key'] for r in self.value['entries']}
            names = {key:name for key,name in self.names.items() if key in known}
        def task(job_id):
            directory = self.directory / job_id
            directory.mkdir()
            base, pvp, donors, pvp_info, reports = decoded
            output, value, manifest = build_catalog(base, pvp, self.value, reports, donors, project, selected_only=True)
            patch = make_bps(base, output)
            if apply_bps(base, patch)[0] != output:
                raise AssertionError('Export verification failed')
            for row in value['entries']:
                row['name'] = names.get(row['key'], '')
            manifest.update(source_patches={'pvp':pvp_info}, manager=True, music_sources='original ROMs')
            (directory / 'unified.gba').write_bytes(output)
            (directory / 'unified.bps').write_bytes(patch)
            (directory / 'build.json').write_text(json.dumps(manifest, indent=2) + '\n')
            saved_project = {**project, 'names': names}
            (directory / 'project.json').write_text(json.dumps(saved_project, ensure_ascii=False, indent=2) + '\n')
            write_catalog(directory, value)
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
            target_id = row['target_index']
        def task(job_id):
            directory = self.directory / job_id
            directory.mkdir()
            base, pvp, donors, _, reports = decoded
            config = {'schema_version': 1, 'pools': {'55': {'tracks': [key], 'selector_shift': 0}}}
            output, _, manifest = build_catalog(base, pvp, self.value, reports, donors, config, selected_only=True)
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
            base, pvp, donors, _, _ = self.decoded
            if row['source'] == 'pvp':
                data, table, count = pvp, 0x135214, 499
            else:
                profile = PROFILES[row['source']]
                data, table, count = donors[row['source']], profile['table_offset'], profile['entry_count']
            return self.realtime.start(data,table,count,row['source_index'],sample_rate)

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
        self.realtime.stop()
        self.executor.shutdown(wait=True)
