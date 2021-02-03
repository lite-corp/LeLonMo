import uuid

from lelonmo import persist_data, socket_client

server_ip = str()
def main_online(host=''):
    global server_ip
    try:
        if not host:
            if bool(persist_data.DATA["debug"]["RANDOMIZE_UUID"]):
                persist_data.DATA["online"]["uuid"] = str(uuid.uuid4())
            host = input(
                f"Please enter the IP of the server (leave empty for [{persist_data.DATA['online']['last_ip']}]) : ")
            if not host:
                host = persist_data.DATA['online']['last_ip']
            persist_data.update_key("last_ip", host, "online")
        socket_client.atexit.register(socket_client.exit_server)
        socket_client.main(host)
        while socket_client.human_to_bool("Do you want to play again ?\n"):
            socket_client.main(host)
        exit()
    except KeyboardInterrupt:
        socket_client.exit_server()
        print("Exiting ...")
        exit(0)
    except Exception as e:
        socket_client.exit_server()
        print("Something went wrong :", e)
        exit(-1)

if __name__ == "__main__":
    main_online()
