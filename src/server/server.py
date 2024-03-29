import json
import os
import ssl
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import account_storage
from acconts import AccontManager
from game.lib_llm import load_dictionnary
from game.llm import LeLonMo
from mime import mime_content_type
from server_tools import file_postprocess, secure_path
from settings import JSONProvider

settings = None
game = None


class LLM_Server(BaseHTTPRequestHandler):
    def _send_headers(self, code=200, mime="text/plain", lenght=0, cookies=None):
        self.send_response(code)
        self.send_header("Content-type", mime)
        if lenght:
            self.send_header("Content-Length", lenght)
        if cookies is not None:
            for c in cookies.values():
                self.send_header("Set-Cookie", c.OutputString())

        self.end_headers()

    def client_cookies(self):
        cookies = SimpleCookie(self.headers.get("Cookie"))
        if self.path in self.server.settings.cookies_pages:
            cookies["token_validator"] = self.server.accounts.get_token_validator()
            cookies["token_validator"]["path"] = "/"
            cookies["token_validator"]["samesite"] = "Strict"
            if "auth_token" in cookies:
                cookies["auth_token"]["path"] = "/"
                cookies["auth_token"]["samesite"] = "Strict"
            return cookies
        else:
            return SimpleCookie()

    def serve_file(self, cookies=None):
        if self.path == "/":
            self.path = "/html/index.html"
            self.serve_file(cookies)
            return
        self.path = secure_path(self.path)

        if self.path in self.server.settings.authenticated_pages:
            # Ensure the client is authenticated before playing
            if "auth_token" not in cookies or not self.server.accounts.is_valid_token(
                cookies["auth_token"].value
            ):
                print("[I] Redirecting user to login page")
                self.send_response(302)
                self.send_header("Location", self.server.settings.login_page)
                self.end_headers()

        if os.path.exists(self.server.settings.web_path + self.path):
            if os.path.isdir(self.server.settings.web_path + self.path):
                self.path = self.path + "index.html"
                self.serve_file()
            else:
                # File exists

                mime = mime_content_type(self.path)
                with open(self.server.settings.web_path + self.path, "rb") as f:
                    file_content = f.read()
                    file_content = file_postprocess(file_content, mime)
                    self._send_headers(
                        code=200, mime=mime, lenght=len(file_content), cookies=cookies
                    )
                    self.wfile.write(file_content)
        else:
            self._raise_404()

    def _raise_404(self):
        self._send_headers(code=404)
        self.wfile.write(b"Could not find file at " + self.path.encode("UTF-8"))

    def do_GET(self):
        cookies = self.client_cookies()
        try:
            self.serve_file(cookies)
        except BrokenPipeError:
            print("[W] A file could not get delivered properly")

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length"))
        try:
            post_data = json.loads(self.rfile.read(content_len).decode("utf-8"))
        except:
            import traceback

            answer = json.dumps(
                {
                    "success": False,
                    "message": "data_format",
                    "detail": traceback.format_exc(),
                }
            ).encode("utf-8")
            self._send_headers(502, "text/json", len(answer))
            self.wfile.write(answer)
            return
        cookies = SimpleCookie(self.headers.get("Cookie"))
        try:
            player_uuid = self.server.accounts.get_uuid(cookies["auth_token"].value)
        except KeyError:
            player_uuid = "\0"
        answer = None
        if self.path == "/chat":
            answer = self.server.game.chat.handle_requests(player_uuid, post_data)
        elif self.path == "/llm":
            answer = self.server.game.handle_requests(player_uuid, post_data)
        elif self.path == "/auth":
            answer = self.server.accounts.handle_auth_requests(post_data)
        elif self.path == "/user":
            answer = self.server.accounts.handle_user_requests(player_uuid, post_data)
        else:
            answer = json.dumps({"success": False, "message": "invalid_request"})

        answer = json.dumps(answer).encode("utf-8")
        self._send_headers(200, "text/json", len(answer))
        self.wfile.write(answer)

    def log_request(self, code="-", size="-") -> None:
        if self.server.settings.log_requests:
            super().log_request(code=code, size=size)


def main(settings_provider):
    settings = settings_provider()

    account_storage.register_storages(settings)

    web_server = ThreadingHTTPServer(settings.get_address(), LLM_Server)
    if settings.ssl_enabled:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(settings.ssl_certificate, settings.ssl_key)
        web_server.socket = ssl_context.wrap_socket(web_server.socket, server_side=True)

    # Load settings
    web_server.settings = settings
    web_server.game = LeLonMo(settings)
    web_server.accounts = AccontManager(settings, web_server.game)

    load_dictionnary(settings)

    print(f"[I] Server started http://{settings.server_address}:{settings.get_port()}")

    try:
        web_server.serve_forever()
    except KeyboardInterrupt:
        pass

    web_server.server_close()
    print("\r[I] Closed HTTP server. ")
    web_server.accounts.delete()


if __name__ == "__main__":
    main(JSONProvider)
