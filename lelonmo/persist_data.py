import json
import os
import uuid
from os.path import expanduser

home = expanduser("~") + os.path.sep
save_file = home + ".lelonmo_save.json"

default_data = dict(
    version="0.4.5",
    online=dict(
        uuid=str(uuid.uuid4()),
        name="",
        update_speed=1,
        last_ip="localhost"
    ),
    settings=dict(
        USE_INPROVED_GENERATOR=True,
        GAME_LANGUAGE="fr",
        USE_COLORS=True
    ),
    game=dict(
        LETTER_NUMBER=7,
        DICT_LANGUAGE="fr",
        FIRST_RUN=True
    ),
    debug=dict(
        ACCEPT_ANY_WORD=False,
        ACCEPT_ANY_LETTER=False,
        DEBUG_WORDS=False,
        SKIP_INTRO=False,
        RANDOMIZE_UUID=False
    )
)

DATA = dict()


def _create_database(f=save_file):
    file = open(save_file, "w+")
    json.dump(default_data, file)
    file.close()


def _fill_data(f=save_file):
    global DATA
    file = open(save_file, "r")
    try:
        DATA = json.load(file)
    except:
        _create_database(save_file)
        print("Database corrupted, reseting to default")
        DATA = default_data
    file.close()


def _repair_data():
    global DATA

    for key1 in default_data.keys():
        if not key1 in DATA:
            DATA[key1] = default_data[key1]
            print(key1, "missing")
            print("Ducon arrête de modifier ce que tu comprends pas")
            continue
        elif key1 == "version":
            if DATA[key1] != default_data[key1]:
                print("Version changed")
                DATA[key1] = default_data[key1]
        else:
            for key2 in default_data[key1].keys():
                if not key2 in DATA[key1]:
                    DATA[key1][key2] = default_data[key1][key2]
                    print(key1, key2, "missing")
                    continue
                else:
                    if DATA[key1][key2] == "" and not default_data[key1][key2] == "":
                        DATA[key1][key2] = default_data[key1][key2]
                        print("Reseting", key2)


def _apply_changes(f=save_file, DATA=DATA):
    file = open(f, "w")
    json.dump(DATA, file)
    file.close()


def update_key(key, value, master=str()):
    global DATA

    if not master:
        working_dict = DATA
    else:
        working_dict = DATA[master]

    working_dict[key] = value
    if master:
        DATA[master] = working_dict
    else:
        DATA = working_dict

    _apply_changes(DATA=DATA)


def update_data():
    global DATA

    if not os.path.exists(save_file):
        _create_database()

    _fill_data()
    _repair_data()
    _apply_changes(f=save_file, DATA=DATA)


update_data()
