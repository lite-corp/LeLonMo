from sys import argv


def main(game=None):
    import server.socket_server as server
    from importlib import reload
    if game:
        print("[W] Reloading server")
        reload(server)
        if "release" in argv:
            from release_tools import create_release_zip
            reload(create_release_zip)
    if "release" in argv:
        from release_tools import create_release_zip
        print("[I] Creating release")
        create_release_zip.main()
    print("[I] Starting server...", end="\r")
    PORT = 11111
    main_thread = server.MainThread(PORT)
    main_thread.setDaemon(True)
    main_thread.start()
    if game is not None:
        main_thread.game = game
    while True:
        try:
            u = input("[llm_server] ~$ ")
        except:
            u = "exit"
        if u == "exit":
            try:
                main_thread.enabled = False
                main_thread.tcpsock.close()
            except OSError:
                pass
            return
        elif u == "update":
            print("\r[W] Update scheduled")
            main(main_thread.game)
            return
        elif u == "release":
            from release_tools import create_release_zip
            reload(create_release_zip)
            print("[I] Creating release")
            create_release_zip.main()


if __name__ == "__main__":
    main()
