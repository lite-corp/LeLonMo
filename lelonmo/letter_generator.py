from random import randint as ri
from os import path

from lelonmo.persist_data import DATA as settings
from lelonmo.word_check import remove_accents

program_path = path.abspath(path.join(path.dirname(__file__),"."))
word_dict = open(
    f"{program_path}{path.sep}data{path.sep}dict{path.sep}dict_{settings['game']['DICT_LANGUAGE']}.txt", "r", encoding='UTF-8').readlines()


def generate(letter_range=(97, 122), lenght=settings["game"]["LETTER_NUMBER"], language=settings["game"]["DICT_LANGUAGE"]):
    global word_dict
    if lenght > 20:
        raise ValueError(f"Trop de lettres ({lenght})")
    if settings["settings"]["USE_INPROVED_GENERATOR"]:
        valid = False
        while not valid:
            shuffle_word = word_dict[ri(1, len(word_dict)-1)].replace('\n', '')
            if settings["debug"]["DEBUG_WORDS"]:
                print(shuffle_word)
            if len(list(set(list(shuffle_word)))) > lenght:
                valid = False
                pass
            elif len(list(set(list(shuffle_word)))) == lenght:
                return list(set(list(remove_accents(shuffle_word))))
            else:
                r = list(set(list(shuffle_word)))
                while len(r) < lenght:
                    r.append(chr(ri(letter_range[0], letter_range[1])))

    else:
        r = list()
        for i in range(lenght):
            r.append(chr(ri(letter_range[0], letter_range[1])))
        return r
