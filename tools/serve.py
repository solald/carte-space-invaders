import http.server, socketserver, functools, os
REPO = '/Users/solald/Documents/Projets/carte-space-invaders'
try:
    os.chdir(REPO)
except Exception:
    pass
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=REPO)
with socketserver.TCPServer(('127.0.0.1', 8765), Handler) as httpd:
    httpd.serve_forever()
