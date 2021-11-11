from random import choice, randint
import unicodedata

from settings import DefaultProvider

word_dict = {}

def load_dictionnary():
    global word_dict

    settings = DefaultProvider()

    f = open(settings.dict_path, "r")
    for i in f.readlines():
        if i[0] in word_dict:
            word_dict[i[0]].append(i.replace("\n", ""))
        else:
            word_dict[i[0]] = [i.replace("\n", "")]
    f.close()


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize("NFKD", input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def generate_letters(n):
    global word_dict

    valid = False
    while not valid:
        shuffle_word = choice( word_dict[ choice(list(word_dict.keys())) ])
        if len(set(shuffle_word)) > n:
            valid = False
            pass
        elif len(set(shuffle_word)) == n:
            return list(set(remove_accents(shuffle_word)))
        else:
            r = list(set(shuffle_word))
            while len(r) < n:
                if not (x:=chr(randint(ord("a"), ord("z")))) in set(shuffle_word):
                    r.append(x)
            return r


def check_dict(word):
    global word_dict

    word = remove_accents(word.lower())
    try:
        return word in word_dict[word[0]]
    except KeyError:
        return False
    except IndexError:
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