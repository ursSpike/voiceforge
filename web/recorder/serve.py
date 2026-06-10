#!/usr/bin/env python3
"""Local recording booth + assembly trigger for the hero call. Stdlib only, localhost only.

  .venv/bin/python web/recorder/serve.py [--port 7861]
  -> open http://localhost:7861 (Chrome recommended; localhost is a secure context so the
     browser mic works without HTTPS)

Routes:
  GET  /                 booth UI
  GET  /shot             money-shot page (web/shot.html): audio + clickable failure table
  GET  /timeline.json    data/hero/timeline.json
  GET  /turns.json       data/hero/turns.json (ground-truth call_log, written by assembler)
  GET  /signals.json     FTO analysis computed LIVE from turns.json + rubric.yaml
  GET  /state            {"saved": ["t2", ...]} — user turns already on disk
  GET  /audio/<file>     agent clips from data/hero/raw/
  GET  /hero.wav         assembled call (404 until assembled)
  POST /save?turn=t2     body = recorded blob -> data/hero/raw/user_t2.<ext> (last take wins)
  POST /assemble         runs pipeline/assemble_hero.py assemble; returns its output
"""
import argparse
import json
import os
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent.parent.parent
HERE = Path(__file__).resolve().parent
HERO = ROOT / "data" / "hero"
RAW = HERO / "raw"
sys.path.insert(0, str(ROOT / "pipeline"))

EXT = {"audio/mp4": ".m4a", "audio/webm": ".webm", "audio/ogg": ".ogg",
       "audio/mpeg": ".mp3", "audio/wav": ".wav"}


class Booth(BaseHTTPRequestHandler):
    def _send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send_media(self, path, ctype):
        """Media with HTTP Range support — without 206 responses Chrome marks the file
        non-seekable (seekable=[0,0]) and silently ignores currentTime assignments,
        which would break click-to-seek on the failure table."""
        data = path.read_bytes()
        n = len(data)
        start, end, code = 0, n - 1, 200
        rng = self.headers.get("Range", "")
        if rng.startswith("bytes="):
            spec = rng.split("=", 1)[1].split(",")[0].strip()
            s, _, e = spec.partition("-")
            try:
                if s == "":
                    start, end = max(0, n - int(e)), n - 1
                else:
                    start, end = int(s), (int(e) if e else n - 1)
                end = min(end, n - 1)
                code = 206
            except ValueError:
                start, end, code = 0, n - 1, 200
            if start > end or start >= n:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{n}")
                self.end_headers()
                return
        chunk = data[start:end + 1]
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        if code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{n}")
        self.send_header("Content-Length", str(len(chunk)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(chunk)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):
        p = urlparse(self.path).path
        if p == "/":
            return self._send(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if p == "/timeline.json":
            return self._send(200, (HERO / "timeline.json").read_bytes(), "application/json")
        if p == "/shot":
            return self._send(200, (ROOT / "web" / "shot.html").read_bytes(), "text/html; charset=utf-8")
        if p == "/turns.json":
            if not (HERO / "turns.json").exists():
                return self._send(404, "not assembled yet")
            return self._send(200, (HERO / "turns.json").read_bytes(), "application/json")
        if p == "/signals.json":
            if not (HERO / "turns.json").exists():
                return self._send(404, "not assembled yet")
            import signals  # pipeline/ is on sys.path; recomputed per request -> rubric edits show on refresh
            call = json.loads((HERO / "turns.json").read_text())
            res = signals.analyze(call["turns"], signals.load_rubric())
            return self._send(200, json.dumps(res), "application/json")
        if p == "/state":
            saved = sorted({f.stem.split("_", 1)[1] for f in RAW.glob("user_t*.*") if f.is_file()})
            return self._send(200, json.dumps({"saved": saved}), "application/json")
        if p == "/hero.wav":
            tl = json.loads((HERO / "timeline.json").read_text())
            w = HERO / f"{tl['call_id']}.wav"
            if w.exists():
                return self._send_media(w, "audio/wav")
            return self._send(404, "not assembled yet")
        if p.startswith("/audio/"):
            f = RAW / Path(p).name  # .name strips any traversal
            if f.is_file():
                return self._send_media(f, "audio/mpeg")
            return self._send(404, "missing")
        if p == "/favicon.ico":
            return self._send(204)
        return self._send(404, "?")

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/save":
            turn = parse_qs(u.query).get("turn", [""])[0]
            if not re.fullmatch(r"t\d{1,3}", turn):
                return self._send(400, "bad turn id")
            n = int(self.headers.get("Content-Length", 0))
            if n <= 0 or n > 100 * 1024 * 1024:
                return self._send(400, "bad size")
            body = self.rfile.read(n)
            mime = (self.headers.get("Content-Type") or "").split(";")[0].strip()
            RAW.mkdir(parents=True, exist_ok=True)
            stem = f"user_{turn}"
            for old in RAW.glob(stem + ".*"):
                old.unlink()
            out = RAW / (stem + EXT.get(mime, ".webm"))
            out.write_bytes(body)
            print(f"  saved {out.name} ({n / 1024:.0f} KB)", flush=True)
            return self._send(200, json.dumps({"saved": out.name}), "application/json")
        if u.path == "/assemble":
            r = subprocess.run(
                [sys.executable, str(ROOT / "pipeline" / "assemble_hero.py"), "assemble"],
                capture_output=True, text=True, cwd=str(ROOT))
            out = r.stdout + ("\n--- stderr ---\n" + r.stderr if r.stderr.strip() else "")
            return self._send(200 if r.returncode == 0 else 500, out)
        return self._send(404, "?")

    def log_message(self, *a):  # quiet; saves/assembles print explicitly
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 7861)))
    args = ap.parse_args()
    srv = ThreadingHTTPServer(("127.0.0.1", args.port), Booth)
    print(f"recording booth: http://localhost:{args.port}  (Ctrl-C to stop)", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
