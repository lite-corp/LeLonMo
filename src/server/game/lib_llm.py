from random import randint
import unicodedata

from settings import DefaultProvider

word_dict = []

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def generate_letters(n):
    global word_dict
    settings = DefaultProvider()

    word_dict = [w.replace('\n', '') for w in open(settings['dict_path'], 'r').readlines()]

    
    valid = False
    while not valid:
        shuffle_word = word_dict[randint(1, len(word_dict)-1)].replace('\n', '')
        if len(list(set(list(shuffle_word)))) > n:
            valid = False
            pass
        elif len(list(set(list(shuffle_word)))) == n:
            return list(set(list(remove_accents(shuffle_word))))
        else:
            r = list(set(list(shuffle_word)))
            while len(r) < n:
                r.append(chr(randint(ord('a'), ord('z'))))

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