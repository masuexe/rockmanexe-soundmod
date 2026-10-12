#!/usr/bin/env python3
"""Run the local browser manager (Python stdlib; ROMs never leave this machine)."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import secrets
from urllib.parse import parse_qs, unquote, urlsplit
import webbrowser

from manager_backend import Manager, ROOT


class Server(ThreadingHTTPServer):
    daemon_threads = True
    def __init__(self, address, manager):
        self.manager = manager
        self.token = secrets.token_urlsafe(32)
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def json(self, value, status=200):
        raw = json.dumps(value, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(raw)

    def trusted(self):
        port = self.server.server_address[1]
        hosts = {f'127.0.0.1:{port}', f'localhost:{port}'}
        if self.headers.get('Host') not in hosts:
            self.json({'error': 'Use the local manager address'}, 403)
            return False
        origin = self.headers.get('Origin')
        if origin and origin not in {f'http://{host}' for host in hosts}:
            self.json({'error': 'Origin not allowed'}, 403)
            return False
        return True

    def authorized(self):
        query = parse_qs(urlsplit(self.path).query)
        supplied = self.headers.get('X-Manager-Token', query.get('token', [''])[0])
        if not secrets.compare_digest(supplied, self.server.token):
            self.json({'error': 'Reload the manager page'}, 403)
            return False
        return True

    def do_GET(self):
        if not self.trusted():
            return
        path = urlsplit(self.path).path
        try:
            if path == '/':
                raw = (ROOT / 'web/index.html').read_text().replace('__MANAGER_TOKEN__', self.server.token).encode()
                mime = 'text/html; charset=utf-8'
            elif path in ('/app.js', '/realtime.js', '/audio-worklet.js', '/style.css'):
                raw = (ROOT / 'web' / path[1:]).read_bytes()
                mime = 'application/javascript' if path.endswith('.js') else 'text/css'
            elif path.startswith('/api/'):
                if not self.authorized():
                    return
                if path == '/api/state':
                    self.json(self.server.manager.state()); return
                if path.startswith('/api/job/'):
                    self.json(self.server.manager.job(path.rsplit('/', 1)[-1])); return
                raise ValueError('Route not found')
            elif path.startswith('/files/'):
                if not self.authorized():
                    return
                parts = path.split('/')
                if len(parts) != 4:
                    raise ValueError('File not found')
                file = self.server.manager.file(parts[2], parts[3])
                raw = file.read_bytes()
                mime = 'audio/wav' if file.suffix == '.wav' else 'application/octet-stream'
                self.send_response(200)
                self.send_header('Content-Type', mime)
                self.send_header('Content-Length', str(len(raw)))
                self.send_header('Content-Disposition', f'{"inline" if file.suffix == ".wav" else "attachment"}; filename="{file.name}"')
                self.send_header('Cache-Control', 'private, max-age=3600')
                self.send_header('X-Content-Type-Options', 'nosniff')
                self.end_headers(); self.wfile.write(raw); return
            else:
                raise ValueError('Route not found')
            self.send_response(200)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(raw)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self'; media-src 'self'; connect-src 'self'; frame-ancestors 'none'")
            self.end_headers(); self.wfile.write(raw)
        except ValueError as exc:
            self.json({'error': str(exc)}, 404)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def stream_audio(self, value):
        session = self.server.manager.live_preview(value['key'],value.get('sample_rate',48000))
        try:
            self.send_response(200)
            self.send_header('Content-Type','application/octet-stream')
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('X-Preview-Id',session.id)
            self.send_header('X-Audio-Sample-Rate',str(session.metadata['sample_rate']))
            self.send_header('Connection','close')
            self.end_headers()
            self.close_connection = True
            while True:
                block = session.read()
                if not block: break
                self.wfile.write(block)
                self.wfile.flush()
        except (BrokenPipeError,ConnectionResetError,OSError,ValueError):
            pass
        finally:
            self.server.manager.realtime.stop(session.id)
            session.close()

    def do_POST(self):
        if not self.trusted() or not self.authorized():
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 <= length <= 32 * 1024 * 1024:
                raise ValueError('File exceeds 32 MiB')
            raw = self.rfile.read(length)
            path = urlsplit(self.path).path
            if path.startswith('/api/upload/'):
                role = path.rsplit('/', 1)[-1]
                result = self.server.manager.upload(role, unquote(self.headers.get('X-Filename', 'input')), raw)
            else:
                value = json.loads(raw or b'{}')
                if not isinstance(value, dict):
                    raise ValueError('Request must be a JSON object')
                if path == '/api/realtime':
                    self.stream_audio(value); return
                elif path == '/api/realtime/stop':
                    result = self.server.manager.realtime.stop(value.get('id'))
                elif path == '/api/load':
                    result = self.server.manager.load(value.get('sources'),value.get('project'))
                elif path == '/api/name':
                    result = self.server.manager.name(value['key'], value['name'])
                elif path == '/api/project':
                    result = self.server.manager.save_project(value)
                elif path == '/api/export':
                    result = self.server.manager.export(value)
                elif path == '/api/preview':
                    result = self.server.manager.preview(value['key'], value.get('seconds', 12))
                else:
                    raise ValueError('Route not found')
            self.json(result)
        except (ValueError, KeyError, TypeError, OSError) as exc:
            self.json({'error': str(exc)}, 400)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--data-dir', type=Path, help='Local names, projects, and generated files')
    parser.add_argument('--mgba', default='/usr/games/mgba')
    parser.add_argument('--realtime',type=Path,help='agbplay streaming helper executable')
    args = parser.parse_args()
    manager = Manager(args.data_dir, mgba=args.mgba, realtime=args.realtime)
    try:
        server = Server(('127.0.0.1', args.port), manager)
    except OSError as exc:
        manager.close()
        parser.exit(1, f'Cannot open the local manager port: {exc}\n')
    url = f'http://127.0.0.1:{server.server_address[1]}/'
    print(f'Rockman EXE Sound Manager: {url}', flush=True)
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        manager.close()


if __name__ == '__main__':
    main()
