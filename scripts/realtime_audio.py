"""Bounded live agbplay sessions. Original input copies are cached, never rebuilt."""
import json
import os
from pathlib import Path
import selectors
import subprocess
import threading
import time
import uuid

from scan_audio import fingerprint


class Session:
    def __init__(self, process, log, metadata, initial=b''):
        self.process, self.log, self.metadata = process, log, metadata
        self.initial = initial
        self.id = uuid.uuid4().hex
        self.lock = threading.Lock()
        self.closed = False

    def read(self, size=8192):
        if self.initial:
            data, self.initial = self.initial, b''
            return data
        return self.process.stdout.read(size)

    def close(self):
        with self.lock:
            if self.closed: return
            self.closed = True
            if self.process.poll() is None:
                self.process.terminate()
                try: self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self.process.kill(); self.process.wait(timeout=2)
            self.process.stdout.close()
            self.log.close()


class RealtimeEngine:
    def __init__(self, binary, directory):
        self.binary = Path(binary)
        self.directory = Path(directory)
        self.lock = threading.RLock()
        self.active = None

    def available(self):
        return self.binary.is_file() and os.access(self.binary, os.X_OK)

    def start(self, data, table, count, song, sample_rate=48000):
        if type(sample_rate) is not int or not 22050 <= sample_rate <= 96000:
            raise ValueError('Audio output rate must be 22050..96000 Hz')
        if not self.available():
            raise ValueError('Build the realtime player first: python3 scripts/build_realtime.py')
        with self.lock:
            self.stop()
            self.directory.mkdir(parents=True, exist_ok=True)
            rom = self.directory / (fingerprint(data)['sha256'] + '.gba')
            if not rom.exists(): rom.write_bytes(data)
            log = (self.directory / ('session-' + uuid.uuid4().hex + '.log')).open('wb')
            try:
                process = subprocess.Popen([str(self.binary.resolve()),str(rom.resolve()),hex(table),str(count),str(song),str(sample_rate)],
                                           stdout=subprocess.PIPE,stderr=log,bufsize=0)
            except OSError:
                log.close()
                raise
            session = Session(process,log,{})
            try:
                raw = b''
                deadline = time.monotonic() + 5
                with selectors.DefaultSelector() as selector:
                    selector.register(process.stdout,selectors.EVENT_READ)
                    while b'\n' not in raw:
                        remaining = deadline - time.monotonic()
                        if remaining <= 0 or not selector.select(remaining):
                            raise ValueError('Realtime player initialization timed out')
                        chunk = os.read(process.stdout.fileno(),4096)
                        if not chunk: raise ValueError('Realtime player could not initialize this song; see its session log')
                        raw += chunk
                        if len(raw)>8192 and b'\n' not in raw: raise ValueError('Invalid realtime player response')
                line, session.initial = raw.split(b'\n',1)
                metadata = json.loads(line)
                if not isinstance(metadata, dict) or metadata.get('sample_rate')!=sample_rate or metadata.get('channels')!=2 or metadata.get('format')!='f32le':
                    raise ValueError('Invalid realtime audio format')
                session.metadata = metadata
                self.active = session
                return session
            except Exception:
                session.close()
                raise

    def stop(self, session_id=None):
        with self.lock:
            if self.active and (session_id is None or self.active.id == session_id):
                self.active.close()
                self.active = None
        return {'stopped':True}
