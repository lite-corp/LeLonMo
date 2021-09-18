from http import cookies
import os
import json
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
import uuid

from security_tools import secure_path
from game.chat import Chat
from game.llm import LeLonMo
from settings import DefaultProvider
from mime import mime_content_type

settings = None
game = None

class LLM_Server(BaseHTTPRequestHandler):
    def _send_headers(self, code = 200, mime = "text/plain", lenght = 0, cookies = None):
        self.send_response(code)
        self.send_header("Content-type", mime)
        if lenght : self.send_header("Content-Length", lenght)
        if cookies is not None:
            for c in cookies.values():
                self.send_header("Set-Cookie", c.OutputString())

        self.end_headers()
    
    def client_cookies(self):
        cookies = SimpleCookie(self.headers.get('Cookie'))
        if 'private_uuid' in cookies:
            return
        cookies['private_uuid'] = uuid.uuid4()
        return cookies


    def serve_file(self, cookies = None):
        global settings
        
        if self.path == '/':
            self.path = '/html/index.html'
            self.serve_file(cookies)
            return
        self.path = secure_path(self.path)
        if os.path.exists(settings["web_path"] + self.path):
            if os.path.isdir(settings["web_path"] + self.path):
                self.path = self.path + "index.html"
                self.serve_file()
            else:
                # File exists

                mime = mime_content_type(self.path)
                with open(settings["web_path"] + self.path, 'rb') as f:
                    file_content = f.read()
                    self._send_headers(
                        code = 200,
                        mime=mime,
                        lenght=len(file_content),
                        cookies=cookies
                    )
                    self.wfile.write(file_content)
        else:
            self._raise_404()
            

    def _raise_404(self):
        self._send_headers(
            code = 404
        )
        self.wfile.write(b'Could not find file at ' + self.path.encode("UTF-8"))

    def do_GET(self):
        cookies = self.client_cookies()
        self.serve_file(cookies)
        

    def do_POST(self):
        global game
        content_len = int(self.headers.get('Content-Length'))
        try:
            post_data = json.loads(self.rfile.read(content_len).decode("utf-8"))
        except:
            import traceback
            answer = json.dumps({'success' : False, 'message' : 'data_format', 'detail' : traceback.format_exc()}).encode('utf-8')
            self._send_headers(502, 'text/json', len(answer))
            self.wfile.write(answer)
            return
        cookies = SimpleCookie(self.headers.get('Cookie'))
        private_uuid = cookies["private_uuid"].value
        
        answer = None
        if self.path == "/chat":
            answer = game.chat.handle_requests(private_uuid, post_data)
            answer = json.dumps(answer).encode("utf-8")
        elif self.path == "/llm":
            answer = game.handle_requests(private_uuid, post_data)
            answer = json.dumps(answer).encode("utf-8")
        else:
            answer = json.dumps(dict(
                success=False,
                message='invalid_request'
            )).encode('utf-8')
        self._send_headers(200, 'text/json', len(answer))
        self.wfile.write(answer)



def main():
    global settings, game
    
    # Load settings
    settings = DefaultProvider()
    game = LeLonMo()


    web_server = HTTPServer(settings.get_address(), LLM_Server)
    print(f"Server started http://{settings['server_address']}:{settings.get_port()}")

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print("Closed HTTP server. ")


if __name__ == "__main__":
    main()
    