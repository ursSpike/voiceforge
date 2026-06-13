#!/usr/bin/env python3
"""Serve the two-route VoiceForge product surface. Localhost only, offline, stdlib-only.

Routes:
  GET /                 the cinematic presentation (out/surface/), real data, all 76 calls.
                        Bundle key handlers (Left/Right/Home/Esc, demo path) live in surface/app.js.
  GET /index.html       same as /
  GET /app.js
  GET /styles.css
  GET /design_data.js   the GENERATED real-data contract (run pipeline/build_surface.py first)

  GET /platform         the OPERATOR WORKSPACE (out/platform/, run pipeline/build_platform.py):
                        fixed call-directory rail (search + filters), Frozen Pilot <-> Live Today
                        switch, aggregate clusters + individual-call evidence views, live empty
                        state w/ execution-id command helper. Falls back to the audited
                        dashboard+live-panel only if out/platform/ is not built.
  GET /platform/app.js, /platform/styles.css, /platform/platform_data.js  workspace assets.
  GET /platform/live    JSON: out/live_calls.json if present, else {"live": false, "calls": []}
  GET /dashboard.html   the raw audited dashboard, byte-identical, no injection (hard fallback)

Both routes are fully self-contained and load with Wi-Fi off.

Run:  python3 pipeline/serve_surface.py [--port 8080]
      -> open http://localhost:8080            (presentation)
         open http://localhost:8080/platform   (operator dashboard + live-today)
"""
import argparse
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
SURFACE = OUT / "surface"
PLATFORM = OUT / "platform"
DASHBOARD = OUT / "dashboard.html"
LIVE_CALLS = OUT / "live_calls.json"

CTYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".svg": "image/svg+xml",
}

# Static files served from out/surface/ for the "/" route.
SURFACE_FILES = {"index.html", "app.js", "styles.css", "design_data.js"}

# Static files served from out/platform/ for the operator "/platform" route.
PLATFORM_FILES = {"index.html", "app.js", "styles.css", "platform_data.js"}


def _read_live():
    """Read out/live_calls.json if present; tolerate absence/corruption gracefully."""
    if not LIVE_CALLS.exists():
        return {"live": False, "calls": [], "note": "No live calls yet — ingest on-site."}
    try:
        data = json.loads(LIVE_CALLS.read_text())
    except Exception as e:
        return {"live": False, "calls": [], "note": f"live_calls.json unreadable: {e}"}
    # Accept either a raw list of calls or an object with a "calls" key.
    if isinstance(data, list):
        return {"live": True, "calls": data}
    if isinstance(data, dict):
        data.setdefault("live", bool(data.get("calls")))
        data.setdefault("calls", [])
        return data
    return {"live": False, "calls": [], "note": "live_calls.json has unexpected shape."}


# The LIVE-TODAY panel is injected just before </body> of the audited dashboard.html.
# Self-contained: inline CSS, no external refs. It fetches /platform/live (same-origin,
# offline) and renders a small roster; on absence it shows the on-site placeholder.
LIVE_PANEL = """
<section id="vf-live-today" style="max-width:1180px;margin:28px auto 40px;padding:0 22px;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;">
  <div style="border:1px solid #cfc9bb;border-radius:14px;background:#fffefa;overflow:hidden;">
    <div style="display:flex;align-items:center;gap:10px;padding:14px 18px;border-bottom:1px solid #e3dfd4;background:#f1efe8;">
      <span style="width:9px;height:9px;border-radius:50%;background:#b03f37;box-shadow:0 0 0 4px #f8e7e4;"></span>
      <strong style="font-size:14px;letter-spacing:.04em;text-transform:uppercase;color:#141d2e;">Live today</strong>
      <span id="vf-live-count" style="margin-left:auto;font-size:12px;color:#6e7785;font-variant-numeric:tabular-nums;"></span>
    </div>
    <div id="vf-live-body" style="padding:16px 18px;color:#46505f;font-size:14px;">Loading live calls…</div>
  </div>
</section>
<script>
(function(){
  var body=document.getElementById('vf-live-body'), count=document.getElementById('vf-live-count');
  var esc=function(s){return String(s==null?'':s).replace(/[&<>\"']/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c]);});};
  fetch('/platform/live').then(function(r){return r.json();}).then(function(d){
    var calls=(d&&d.calls)||[];
    if(!d||!d.live||!calls.length){
      count.textContent='0 ingested';
      body.innerHTML='<span style=\"color:#6e7785\">'+esc((d&&d.note)||'No live calls yet — ingest on-site.')+'</span>';
      return;
    }
    count.textContent=calls.length+' ingested';
    var rows=calls.map(function(c){
      var id=esc(c.call_id||c.id||'—');
      var lang=esc(c.language||c.lang||'');
      var wf=esc(c.workflow_type||c.wf||'');
      var oc=c.outcome&&typeof c.outcome==='object'?c.outcome.task_completed:c.outcome;
      var badge=oc===true?'completed':oc===false?'not completed':'pending';
      var col=oc===true?'#136f58':oc===false?'#b03f37':'#8f5c10';
      return '<tr><td style=\"font-family:ui-monospace,Menlo,monospace;padding:6px 10px;border-top:1px solid #f1efe8\">'+id+'</td>'
        +'<td style=\"padding:6px 10px;border-top:1px solid #f1efe8\">'+lang+'</td>'
        +'<td style=\"padding:6px 10px;border-top:1px solid #f1efe8\">'+wf+'</td>'
        +'<td style=\"padding:6px 10px;border-top:1px solid #f1efe8;color:'+col+';font-weight:600\">'+badge+'</td></tr>';
    }).join('');
    body.innerHTML='<table style=\"width:100%;border-collapse:collapse;font-size:13px\"><thead><tr style=\"text-align:left;color:#6e7785;font-size:11px;text-transform:uppercase;letter-spacing:.05em\">'
      +'<th style=\"padding:0 10px 6px\">call</th><th style=\"padding:0 10px 6px\">lang</th><th style=\"padding:0 10px 6px\">workflow</th><th style=\"padding:0 10px 6px\">outcome</th></tr></thead><tbody>'+rows+'</tbody></table>';
  }).catch(function(e){
    count.textContent='';
    body.innerHTML='<span style=\"color:#6e7785\">No live calls yet — ingest on-site.</span>';
  });
})();
</script>
"""


def _platform_html():
    """The audited dashboard.html with the LIVE-TODAY panel injected before </body>.
    dashboard.html itself is never modified on disk; injection is in-memory per request."""
    html = DASHBOARD.read_text()
    if "</body>" in html:
        return html.replace("</body>", LIVE_PANEL + "\n</body>", 1)
    return html + LIVE_PANEL


class Surface(BaseHTTPRequestHandler):
    def _send(self, code, body=b"", ctype="text/plain; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _send_surface_file(self, name):
        f = SURFACE / name
        if not f.is_file():
            return self._send(
                404,
                f"{name} not found in out/surface/. Run: python3 pipeline/build_surface.py",
            )
        ctype = CTYPES.get(f.suffix, "application/octet-stream")
        return self._send(200, f.read_bytes(), ctype)

    def _send_platform_file(self, name):
        f = PLATFORM / name
        if not f.is_file():
            return self._send(
                404,
                f"{name} not found in out/platform/. Run: python3 pipeline/build_platform.py",
            )
        ctype = CTYPES.get(f.suffix, "application/octet-stream")
        return self._send(200, f.read_bytes(), ctype)

    def do_GET(self):
        p = urlparse(self.path).path

        # ---- route: / (presentation) ----
        if p == "/" or p == "/index.html":
            return self._send_surface_file("index.html")
        # bundle assets (referenced by surface/index.html: design_data.js then app.js, + styles.css)
        name = p.lstrip("/")
        if name in SURFACE_FILES:
            return self._send_surface_file(name)

        # ---- route: /platform (operator workspace, out/platform/) ----
        # /platform/live MUST be checked before generic /platform/<asset>.
        if p == "/platform/live":
            return self._send(200, json.dumps(_read_live()), CTYPES[".json"])
        if p == "/platform" or p == "/platform/":
            # Prefer the real operator workspace; fall back to the audited
            # dashboard+live-panel if the workspace hasn't been built yet.
            if (PLATFORM / "index.html").is_file():
                return self._send_platform_file("index.html")
            if DASHBOARD.exists():
                return self._send(200, _platform_html(), CTYPES[".html"])
            return self._send(404, "out/platform/ not built and out/dashboard.html missing")
        # platform static assets: /platform/app.js, /platform/styles.css, /platform/platform_data.js
        if p.startswith("/platform/"):
            asset = p[len("/platform/"):]
            if asset in PLATFORM_FILES:
                return self._send_platform_file(asset)

        # ---- hard fallback: untouched audited dashboard ----
        if p == "/dashboard.html":
            if not DASHBOARD.exists():
                return self._send(404, "out/dashboard.html missing")
            return self._send(200, DASHBOARD.read_bytes(), CTYPES[".html"])

        if p == "/favicon.ico":
            return self._send(204)
        return self._send(404, "not found")

    def log_message(self, *a):  # quiet
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 8080)))
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    if not (SURFACE / "index.html").exists():
        print("note: out/surface/ not built yet — run `python3 pipeline/build_surface.py` first.",
              file=sys.stderr)

    srv = ThreadingHTTPServer((args.host, args.port), Surface)
    print(f"VoiceForge surface: http://localhost:{args.port}            (presentation)", flush=True)
    print(f"                    http://localhost:{args.port}/platform   (operator dashboard + live today)", flush=True)
    print("Ctrl-C to stop", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped", flush=True)


if __name__ == "__main__":
    main()
