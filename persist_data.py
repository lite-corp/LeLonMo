import json
import os

save_file = ".\\.save.json"

default_data = dict(
    version="0.2-dev",
    settings=dict(
        USE_INPROVED_GENERATOR=True,
        GAME_LANGUAGE="fr"
    ),
    game=dict(
        LETTER_NUMBER=7,
        DICT_LANGUAGE="fr"
    ),
    debug=dict(
        ACCEPT_ANY_WORD=False,
        ACCEPT_ANY_LETTER=False,
        DEBUG_WORDS=False,
        SKIP_INTRO=False,
        TEST_VALUE=5
    )
)


def get_save(f=save_file):
    if os.path.exists(f):
        data_file = open(f)
        try:
            data = json.load(data_file)
            return data
        except:
            raise ValueError(
                "Invalid JSON data\nPlease do not edit setting file without knowing what you are doing")
    else:
        data_file = open(f, "w+")
        data_file.write(json.dumps(default_data))
        return default_data


def update_variables(f=save_file):

    global LETTER_NUMBER
    global DICT_LANGUAGE
    global USE_INPROVED_GENERATOR
    global GAME_LANGUAGE
    global ACCEPT_ANY_WORD
    global ACCEPT_ANY_LETTER
    global DEBUG_WORDS
    global SKIP_INTRO
    global TEST_VALUE
    global version

    settings = get_save()
    if settings["version"] != default_data["version"]:
        update_settings()
        print("Updated from another version, please remove {file} if you encouter any problem"
              .format(file=os.path.abspath(f))
              )

    try:
        LETTER_NUMBER = settings["game"]["LETTER_NUMBER"]
        DICT_LANGUAGE = settings["game"]["DICT_LANGUAGE"]
        USE_INPROVED_GENERATOR = settings["settings"]["USE_INPROVED_GENERATOR"]
        GAME_LANGUAGE = settings["settings"]["GAME_LANGUAGE"]
        ACCEPT_ANY_WORD = settings["debug"]["ACCEPT_ANY_WORD"]
        ACCEPT_ANY_LETTER = settings["debug"]["ACCEPT_ANY_LETTER"]
        DEBUG_WORDS = settings["debug"]["DEBUG_WORDS"]
        SKIP_INTRO = settings["debug"]["SKIP_INTRO"]
        TEST_VALUE = settings["debug"]["TEST_VALUE"]
        version = settings["version"]
    except KeyError:
        update_settings()

def update_settings(f=save_file, default=default_data):
    try:
        data = get_save(f)
        for i in default.keys():
            if i == "version":
                data[i] = default[i]
                continue
            if not data.get(i):
                data[i] = default[i]
            for j in default[i]:
                if not data.get(i).get(j):
                    data[i][j]=default[i][j]
    except:
        print("Error while updating settings, rolling back to default")
        os.remove(f)
        get_save(f)
        print("Please restart the game for the changes to take effect")

def write(key, value, f=save_file):
    data = get_save(f)
    data[key] = value
    json.dump(data, open(f, "w"))
    update_variables(f)


update_variables()