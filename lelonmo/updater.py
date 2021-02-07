import socket
from zipfile import ZipFile
import os, sys, imp
from lelonmo import persist_data

BUFFER_SIZE = 4096
SERVER_PORT = 11111

def _send_data(data: str, host: str):
    socket.timeout = 2
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, SERVER_PORT))
        s.send(
            bytearray(
                "%llm_client%" \
                f"{persist_data.DATA['version'].replace('.', str())}%" \
                f"{persist_data.DATA['online']['uuid']}%" \
                f"{data}",
                "utf-8"
            )
        )
        v = s.recv(BUFFER_SIZE)
        s.close()
        return v
    except ConnectionRefusedError:
        print("Server error : Connexion refused")
        s.close()
        exit()
    except Exception as e:
        s.close()
        print("Server error :", e)
        exit(0)


def auto_update(ip, wb):
    size = int(_send_data("size%", ip))
    wb.update("The update is available")
    tmp_file = open("tmp_update.zip", "wb")
    s = socket.socket()  
    s.connect((ip, SERVER_PORT))
    s.send(bytearray(f"%llm_client%{persist_data.DATA['version'].replace('.', str())}%{persist_data.DATA['online']['uuid']}%latest_file%","utf-8"))
    data = b'1'
    wb.update("Downloading ...")
    while data:
        data = s.recv(BUFFER_SIZE)
        if not data:
            break
        # write data to a file
        tmp_file.write(data)
    tmp_file.close()
    wb.update("Done")
    ziph = ZipFile('tmp_update.zip', 'r')
    wb.update("Extracting update ...")
    for file in ziph.namelist():
        ziph.extract(file, os.path.realpath(os.path.join(__file__, f"..{os.path.sep}..")))
    wb.update("Update successful")
    exit(0)