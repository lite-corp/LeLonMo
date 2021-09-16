import os
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer

from security_tools import secure_path
from game.chat import Chat
from settings import DefaultProvider
from mime import mime_content_type

settings = None
chat = None

class LLM_Server(BaseHTTPRequestHandler):
    def _send_headers(self, code = 200, mime = "text/plain", lenght = 0, cookies = None):
        self.send_response(code)
        self.send_header("Content-type", mime)
        if lenght : self.send_header("Content-Length", lenght)
        if cookies is not None:
            for c in cookies.values():
                self.send_header("Set-Cookie", c.OutputString())

        self.end_headers()
    
    def serve_file(self):
        global settings

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
                        cookies=None
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
        self.serve_file()
        

    def do_POST(self):
        global chat
        content_len = int(self.headers.get('Content-Length'))
        post_data = self.rfile.read(content_len).decode("utf-8")
        
        if self.path == "/chat":
            chat.handle_requests(post_data)



def main():
    global settings, chat
    
    # Load settings
    settings = DefaultProvider()
    chat = Chat()


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
    