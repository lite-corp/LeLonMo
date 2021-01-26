import uuid

from . import persist_data, socket_client


def main_online():
    if bool(persist_data.DATA["debug"]["RANDOMIZE_UUID"]):
        persist_data.DATA["online"]["uuid"] = str(uuid.uuid4())
    host = input(
        "Please enter the IP of the server (leave empty for local) : ")
    if not host:
        host = "localhost"
    socket_client.main(host)
    while socket_client.human_to_bool("Do you want to play again ?\n"):
        socket_client.main(host)
    


if __name__ == "__main__":
    main_online()
