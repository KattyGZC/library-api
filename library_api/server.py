# -*- coding: utf-8 -*-

from http.server import HTTPServer
from database import *
import os

from handler import LibraryHTTPRequestHandler

def run_server():
    db_filename = 'library.db'
    
    # Eliminar la base de datos si existe
    if os.path.exists(db_filename):
        os.remove(db_filename)
        print(f"{db_filename} eliminada.")
        
    create_database()
    seed_database()
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, LibraryHTTPRequestHandler)
    print('Starting server...')
    httpd.serve_forever()
