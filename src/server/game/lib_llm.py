from random import choice, randint
import unicodedata

from settings import DefaultProvider

word_dict = []

def load_dictionnary():
    global word_dict

    settings = DefaultProvider()

    f = open(settings.dict_path, "r")
    word_dict = set(f.readlines())
    f.close()


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize("NFKD", input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def generate_letters(n):
    global word_dict

    valid = False
    while not valid:
        shuffle_word = choice(list(word_dict)).replace("\n", "")
        if len(list(set(list(shuffle_word)))) > n:
            valid = False
            pass
        elif len(list(set(list(shuffle_word)))) == n:
            return list(set(list(remove_accents(shuffle_word))))
        else:
            r = list(set(list(shuffle_word)))
            while len(r) < n:
                r.append(chr(randint(ord("a"), ord("z"))))
            return r


def check_dict(word, language="fr"):
    global word_dict

    word = word.lower()
    for w in word_dict:
        if remove_accents(word) == remove_accents(w).replace("\n", ""):
            return True
    return False


def check_list(word, letters):
    for l in remove_accents(word):
        if not l.lower() in letters:
            return False
    return True

def pub_to_private_uuid(public_uuid: str, player_list: dict)-> str:
    for private_uuid in player_list:
        if player_list[private_uuid]['public_uuid'] == public_uuid:
            return private_uuid
    return None