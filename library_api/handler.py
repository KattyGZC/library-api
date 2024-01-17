from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json
import re
from database import *


class LibraryHTTPRequestHandler(BaseHTTPRequestHandler):
    def _get_book_id(self):
        """
        Obtiene el ID del libro de la URL.
        """
        book_id = self.path.split('/')[2]
        try:
            return int(book_id)
        except ValueError:
            self._send_error_response(f'El book_id debe ser un número entero. Valor recibido: {book_id}', status_code=404)
            return None

    def _get_page_number(self):
        """
        Obtiene el número de página de la URL.
        """
        page_number = self.path.split('/')[-1]
        page_number = page_number.split('?')[0]
        try:
            return int(page_number)
        except ValueError:
            self._send_error_response(f'El page_number debe ser un número entero. Valor recibido: {page_number}', status_code=404)
            return None

    def _send_json_response(self, data, status_code=200):
        """
        Envía una respuesta JSON con el código de estado especificado.
        """
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def _send_error_response(self, message, status_code=400):
        """
        Envía una respuesta de error en formato JSON con el código de estado especificado.
        """
        data = {'error': message, 'status_code': status_code}
        self._send_json_response(data, status_code)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        only_book_re = r"^/books/\d+$"
        book_pages_re = r"^/books/\d+/page/\d+$"
        if parsed_url.path == '/books':
            books = get_books()
            data = [{'id': book.id, 'title': book.title, 'author': book.author} for book in books]
            self._send_json_response(data)
            
        elif re.search(only_book_re, parsed_url.path):
            book_id = self._get_book_id()
            if book_id is None:
                return
            
            book = get_book(book_id)
            if not book:
                self._send_error_response('El libro no existe', status_code=404)
                return

            pages_data = [{'number': page.page_number, 'content': page.content} for page in book.pages]
            
            book_data = {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'pages': pages_data if pages_data else 'Sin páginas aún'
            }
            self._send_json_response(book_data)

        elif re.search(book_pages_re, parsed_url.path):
            book_id = self._get_book_id()
            if book_id is None:
                return

            book = get_book(book_id)
            if not book:
                self._send_error_response('El libro no existe', status_code=404)
                return
            
            if not book.pages:
                self._send_error_response('El libro no tiene páginas', status_code=404)
                return
            
            page_number = self._get_page_number()
            if page_number is None:
                return
            
            if page_number > len(book.pages):
                self._send_error_response('Página solicitada no encontrada', status_code=404)
                return

            page = get_page(book_id, page_number)
            total_pages = get_total_pages(book_id)
            format_param = parsed_url.query.split('=')[1]

            if format_param == 'html':
                content = f'<html><body><p>{page}</p></body></html>'
            else:
                content = page
            
            book_page_data = {
                'title': book.title,
                'page': f'{page_number} de {total_pages}',
                'content': content
            }
            self._send_json_response(book_page_data)
            
        else:
            self._send_error_response('URL inválida', status_code=404)
