# -*- coding: utf-8 -*-
"""Artifact'e YAKIN katı CSP simülasyonu (gerçek Artifact CSP'si bilinmiyor; bu bir yaklaşıktır).
Kullanım: py csp_server.py 8766   (10_Website klasörünü katı CSP başlığıyla sunar)
Eval yok, harici script yok, yalnızca Google Fonts stil/yazı tipi, blob/data görsel."""
import sys, os, http.server, functools

CSP = ("default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com data:; img-src data: blob:; connect-src 'self' blob: data:; worker-src blob:; "
       "base-uri 'none'; form-action 'none'")


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Content-Security-Policy", CSP)
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8766
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "10_Website"))
    http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(H, directory=root)).serve_forever()
