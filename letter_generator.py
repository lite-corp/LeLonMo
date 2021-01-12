from random import randint as ri
from default_settings import *


def generate(letter_range=(97, 122), lenght=7, language="fr"):
    if lenght > 20:
        raise ValueError(f"Trop de lettres ({lenght})")
    if USE_INPROVED_GENERATOR:
        d = open(f"data/dict/dict_{language}.txt", "r", encoding='UTF-8').readlines()
        valid = False
        while not valid:
            shuffle_word = d[ri(1, len(d)-1)].replace('\n', '')
            if DEBUG_WORDS : print(shuffle_word)
            if len(list(set(list(shuffle_word)))) > lenght :
                valid=False
                pass
            elif len(list(set(list(shuffle_word)))) == lenght:
                return list(set(list(shuffle_word)))
            else:
                r=list(set(list(shuffle_word)))
                while len(r) < lenght:
                    r.append(chr(ri(letter_range[0], letter_range[1])))

    else:
        r=list()
        for i in range(lenght):
            r.append(chr(ri(letter_range[0], letter_range[1])))
        return r
