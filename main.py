import platform
import argparse

os_name = platform.system()


parser = argparse.ArgumentParser(description='Play LeLonMo')
parser.add_argument("--server", help="Start the server", action="store_true")
args = parser.parse_args()

if args.server:
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
else:
    print("Starting the game, please wait ...")
    if os_name == "Windows":
        import lelonmo.persist_data as persist
        if platform.version().startswith("10."):
            persist.update_key("FIRST_RUN", False, "game")
        elif persist.DATA["game"]['FIRST_RUN']:
            persist.update_key("FIRST_RUN", False, "game")
            input("Colors are not supported on this version of windows, and are disabled by default. ")
            persist.update_key("USE_COLORS", False, "settings")
        import lelonmo.menu as menu
        menu.main()
    else:
        import lelonmo.menu as menu
        input(
            "This platform is not officially supported press [ENTER] to continue")
        menu.main()
