import logging
import threading
import os
from string import Template
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

class Api:
  def __init__(self, controller=None, host='0.0.0.0', port=8080):
    self.server = HTTPServer((host, port), self._create_handler(controller))
    logging.info(f'Server running on http://{host}:{port}')
    self.thread = threading.Thread(target=self._start_server, name=self.__class__.__name__, daemon=True)
    self.thread.start()

  def _create_handler(self, controller):
    class CustomHttpRequestHandler(HttpRequestHandler):
      def __init__(self, *args, **kwargs):
        self.controller = controller
        super().__init__(*args, **kwargs)
    return CustomHttpRequestHandler

  def _start_server(self):
    try:
      self.server.serve_forever()
    except Exception as e:
      logging.error(f"Server error: {e}")
    finally:
      self.server.server_close()
      logging.info("Server stopped.")

class HttpRequestHandler(BaseHTTPRequestHandler):
  TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

  def send_response_with_body(self, code, content_type, body):
    self.send_response(code)
    self.send_header('Content-Type', content_type)
    self.end_headers()
    self.wfile.write(body.encode('utf-8'))

  def handle_home(self):
    html_content = self._generate_html()
    self.send_response_with_body(200, 'text/html', html_content)

  def handle_tag_write_post(self):
    try:
      content_length = int(self.headers.get('Content-Length', 0))
      post_data = self.rfile.read(content_length).decode('utf-8')
      parsed_data = parse_qs(post_data)
      data_to_write = parsed_data.get('data', [None])[0]

      if not data_to_write:
        raise ValueError("No data provided in the POST body")

      written_data = self.controller.write_data(data_to_write)
      if written_data:
        message = f"Successfully written data: {written_data}"
        self.send_response_with_body(200, 'text/plain', message)
      else:
        self.send_response_with_body(500, 'text/plain', "Failed to write data to tag")

    except ValueError as e:
      self.send_response_with_body(400, 'text/plain', str(e))
    except Exception as e:
      logging.error(f"Error in handle_tag_write_post: {e}")
      self.send_response_with_body(500, 'text/plain', f"Internal Server Error: {e}")

  def do_GET(self):
    try:
      if self.path in ('', '/', None):
        self.handle_home()
      else:
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')
    except Exception as e:
      logging.error(f"Error in do_GET: {e}")
      self.send_response_with_body(500, 'text/plain', f"Internal Server Error: {e}")

  def do_POST(self):
    try:
      if self.path == '/tag/write':
        self.handle_tag_write_post()
      else:
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b'Not Found')
    except Exception as e:
      logging.error(f"Error in do_POST: {e}")
      self.send_response_with_body(500, 'text/plain', f"Internal Server Error: {e}")

  def _generate_html(self):
    template_path = os.path.join(self.TEMPLATE_DIR, 'index.html')
    try:
      with open(template_path, 'r') as file:
        html_template = Template(file.read())

      # Ensure default values are used if attributes are None or not present
      content = self.controller.content or '-'
      tag_id = self.controller.tag_id or '-'
      last_id = self.controller.last_id or '-'
      current_id = self.controller.current_id or '-'
      resilience_counter = str(self.controller.resilience_counter or '-')

      return html_template.substitute(
        content=content,
        tag_id=tag_id,
        last_id=last_id,
        current_id=current_id,
        resilience_counter=resilience_counter
      )
    except FileNotFoundError:
        raise RuntimeError(f"Template file not found: {template_path}")
    except KeyError as e:
        raise RuntimeError(f"Missing placeholder in template: {e}")

