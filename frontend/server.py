#!/usr/bin/env python3
"""Simple HTTP server for the frontend with CORS support"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
import os

class CORSHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

def run_server(port=3000):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSHTTPRequestHandler)
    
    print(f"""
    🌐 DermaMed Frontend Server
    ========================
    Servidor rodando em: http://localhost:{port}
    
    📝 Instruções:
    1. Certifique-se que o backend está rodando em http://localhost:8000
    2. Abra http://localhost:{port} no navegador
    3. Use as credenciais: demo_doctor / demo123
    
    Pressione Ctrl+C para parar
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Servidor frontend parado")

if __name__ == '__main__':
    run_server()