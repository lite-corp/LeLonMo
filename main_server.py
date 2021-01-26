print("[I] Starting server...", end="\r")
import server.socket_server as server
# Settings #
LANGUAGE = "fr"
PORT = 11111
main_thread = server.MainThread(PORT)
main_thread.start()
while True:
    try:
        u = input()
    except:
        u = "exit"
    if u == "exit":
        try:
            main_thread.tcpsock.close()
        except OSError:
            pass
    exit()