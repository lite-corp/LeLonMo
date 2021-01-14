import json
import os

from default_settings import *

save_file = ".\\.save.json"


def get_save(f):
    global data
    if os.path.exists(f):
        f = open(save_file)
        try:
            data = json.load(f)
            return data
        except:
            raise ValueError(
                "Invalid JSON data\nPlease do not edit setting file without knowing what you are doing")
    else:
        default_data = dict(
            version=version,
            settings=dict(
                USE_INPROVED_GENERATOR=USE_INPROVED_GENERATOR,
                GAME_LANGUAGE=GAME_LANGUAGE
                ),
            game=dict(
                LETTER_NUMBER=LETTER_NUMBER,
                DICT_LANGUAGE=DICT_LANGUAGE
                )
            )
        f = open(save_file, "w+")
        f.write(json.dumps(default_data))
        return default_data


settings = get_save(save_file)
if settings["version"] != version:
    print("Updated from another version, please remove {file} if you encouter any problem"
          .format(file=os.path.abspath(save_file))
          )

try:
    LETTER_NUMBER = settings["game"]["LETTER_NUMBER"]
    DICT_LANGUAGE = settings["game"]["DICT_LANGUAGE"]
    USE_INPROVED_GENERATOR = settings["settings"]["USE_INPROVED_GENERATOR"]
    GAME_LANGUAGE = settings["settings"]["GAME_LANGUAGE"]
except KeyError:
    print("Error while reading settings, rolling back to default")
    os.remove(save_file)
    get_save(save_file)
    print("Please restart the game for the changes to take effect")
