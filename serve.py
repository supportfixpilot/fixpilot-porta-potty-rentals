#!/usr/bin/env python3
"""
Local development server for FixPilot — mirrors Cloudflare Pages behavior.

Features:
  - Clean URLs: /locations → locations/index.html or locations.html
  - Directory index: /atlanta → porta-potty-rental-atlanta-ga/index.html
  - .html extension fallback: /blog/post → blog/post.html
  - Serves on http://localhost:8000 by default

Usage:
  python3 serve.py          # port 8000
  python3 serve.py 3000     # custom port
"""

import http.server
import os
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).parent
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class CloudflareHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        """Try to serve the request, resolving clean URLs like Cloudflare Pages."""
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path.lstrip('/'))

        resolved = self._resolve(path)
        if resolved:
            self.path = '/' + str(resolved.relative_to(ROOT))
            super().do_GET()
        else:
            # Fall back to 404.html if it exists
            f404 = ROOT / '404.html'
            if f404.exists():
                self.send_response(404)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(f404.read_bytes())
            else:
                self.send_error(404, f"Not found: {self.path}")

    def _resolve(self, path: str) -> Path | None:
        """Resolve a URL path to a filesystem file, Cloudflare-style."""
        candidates = []

        if not path:
            # Root
            candidates.append(ROOT / 'index.html')
        else:
            # 1. Exact file match
            candidates.append(ROOT / path)
            # 2. path/index.html  (directory index)
            candidates.append(ROOT / path / 'index.html')
            # 3. path.html  (clean URL)
            candidates.append(ROOT / (path + '.html'))
            # 4. Strip trailing slash and retry
            if path.endswith('/'):
                clean = path.rstrip('/')
                candidates.append(ROOT / clean / 'index.html')
                candidates.append(ROOT / (clean + '.html'))

        for candidate in candidates:
            if candidate.exists() and candidate.is_file():
                return candidate
        return None

    def log_message(self, fmt, *args):
        """Clean log output."""
        code = args[1] if len(args) > 1 else '-'
        color = '\033[32m' if str(code).startswith('2') else '\033[33m' if str(code).startswith('3') else '\033[31m'
        reset = '\033[0m'
        print(f"  {color}{args[1]}{reset}  {args[0]}")


if __name__ == '__main__':
    os.chdir(ROOT)
    print(f"\n  FixPilot Local Server")
    print(f"  ─────────────────────")
    print(f"  http://localhost:{PORT}\n")
    print(f"  Clean URLs enabled (mirrors Cloudflare Pages)")
    print(f"  Press Ctrl+C to stop\n")

    with http.server.HTTPServer(('', PORT), CloudflareHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Server stopped.")
