from sys import argv
def main(): 
    print("[I] Starting server...", end="\r")
    PORT = 11111
    main_thread = server.MainThread(PORT)
    main_thread.setDaemon(True)
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


if __name__ == "__main__":
    import server.socket_server as server
    if "release" in argv:
        from release_tools import create_release_zip
        create_release_zip.main()
    main()