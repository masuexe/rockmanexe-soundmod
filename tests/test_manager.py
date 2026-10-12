import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from manager_backend import Manager, INPUTS
from manage_sound import Handler
from scan_audio import apply_bps


def finish(manager, started):
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        job = manager.job(started['job_id'])
        if job['status'] != 'running':
            if job['status'] == 'error':
                raise AssertionError(job['message'])
            return job
        time.sleep(.02)
    raise AssertionError('Job timed out')


class Connection:
    def __init__(self, request):
        self.input = io.BytesIO(request)
        self.output = bytearray()
    def makefile(self, *_):
        return self.input
    def sendall(self, data):
        self.output.extend(data)


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.manager = Manager(self.temp.name, preload=False)
        self.server = SimpleNamespace(manager=self.manager, token='test-token', server_address=('127.0.0.1',8765))
    def tearDown(self):
        self.manager.close()
        self.temp.cleanup()
    def request(self, path, token=True, host='127.0.0.1:8765', body=None, origin=None):
        method = 'GET' if body is None else 'POST'
        headers = [f'{method} {path} HTTP/1.1',f'Host: {host}','Connection: close']
        if token: headers.append('X-Manager-Token: test-token')
        if origin: headers.append(f'Origin: {origin}')
        raw = b'' if body is None else json.dumps(body).encode()
        headers.append(f'Content-Length: {len(raw)}')
        connection = Connection(('\r\n'.join(headers)+'\r\n\r\n').encode()+raw)
        Handler(connection, ('127.0.0.1',1), self.server)
        head, response = bytes(connection.output).split(b'\r\n\r\n',1)
        return int(head.split()[1]),response
    def test_api_requires_token_and_local_origin(self):
        self.assertEqual(self.request('/api/state',token=False)[0],403)
        self.assertEqual(self.request('/api/state',host='evil.example:8765')[0],403)
        self.assertEqual(self.request('/api/state',origin='https://evil.example')[0],403)
        status, data = self.request('/api/state')
        self.assertEqual(status,200)
        self.assertEqual(json.loads(data)['inputs'],{})
    def test_page_and_file_paths(self):
        status,page = self.request('/',token=False)
        self.assertEqual(status,200)
        self.assertIn(b"window.MANAGER_TOKEN = 'test-token'",page)
        self.assertEqual(self.request('/files/nojob/../track-names.json')[0],404)
        self.assertEqual(self.request('/scripts/manager_backend.py')[0],404)
    def test_malformed_project_returns_error(self):
        self.assertEqual(self.request('/api/project',body=[])[0],400)
        self.assertEqual(self.request('/api/load',body={})[0],400)


@unittest.skipUnless(all(path.exists() for path in INPUTS.values()), 'local ROM inputs unavailable')
class ManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.manager = Manager(self.temp.name)
        finish(self.manager,self.manager.load())
    def tearDown(self):
        self.manager.close()
        self.temp.cleanup()
    def test_names_persist_and_invalid_project_is_atomic(self):
        self.manager.name('exegp:1',' GP title ')
        before = copy.deepcopy(self.manager.project)
        project = copy.deepcopy(before)
        project['pools']['55']['tracks']=['soundmod:0']
        project['names']={'unknown:1':'bad'}
        with self.assertRaises(ValueError): self.manager.save_project(project)
        self.assertEqual(self.manager.project,before)
        self.assertEqual(self.manager.state()['project']['names']['exegp:1'],'GP title')
        other = Manager(self.temp.name,preload=False)
        try: self.assertEqual(other.names['exegp:1'],'GP title')
        finally: other.close()
    def test_default_export_round_trip_and_input_preservation(self):
        original = {role:data for role,(_,data) in self.manager.inputs.items()}
        job = finish(self.manager,self.manager.export(self.manager.state()['project']))
        output = self.manager.file(job['id'],'unified.gba').read_bytes()
        patch_data = self.manager.file(job['id'],'unified.bps').read_bytes()
        self.assertEqual(apply_bps(original['base'],patch_data)[0],output)
        self.assertEqual(job['result']['fingerprint']['sha256'],'e20a5763e40d3510b200c9fd1a67597eb384d290007e3e38e3b40e5a621b5854')
        self.assertEqual(original,{role:data for role,(_,data) in self.manager.inputs.items()})
        with self.assertRaises(ValueError): self.manager.file(job['id'],'build.json')
    def test_preview_isolated_and_cached(self):
        before = copy.deepcopy(self.manager.project)
        def capture(rom, manifest, target, directory, seconds, mgba):
            self.assertEqual(manifest['hook']['rules'][0]['ids'],[499])
            self.assertEqual(target,499)
            directory.mkdir()
            wav = directory/'preview.wav'; wav.write_bytes(b'fixture')
            return wav, {'seconds':seconds}
        with patch('manager_backend.capture_preview',side_effect=capture) as mock:
            job = finish(self.manager,self.manager.preview('soundmod:0',3))
            self.assertEqual(self.manager.preview('soundmod:0',3)['job_id'],job['id'])
            self.assertEqual(mock.call_count,1)
        self.assertEqual(self.manager.project,before)
        self.assertEqual(self.manager.file(job['id'],'preview.wav').read_bytes(),b'fixture')
        with self.assertRaises(ValueError): self.manager.preview('exegp:5')
    def test_wrong_input_rejects_and_invalidates_catalog(self):
        self.manager.upload('donor','other.gba',b'bad ROM')
        self.assertIsNone(self.manager.state()['catalog'])
        started = self.manager.load()
        with self.assertRaisesRegex(AssertionError,'Unsupported exegp fingerprint'):
            finish(self.manager,started)
        self.assertIsNone(self.manager.decoded)


if __name__ == '__main__': unittest.main()
