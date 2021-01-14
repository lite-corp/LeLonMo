import unicodedata
from persist_data import DATA as settings

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def check_dict(word, language="fr"):
    if settings["debug"]["ACCEPT_ANY_WORD"]:
        return True
    word = word.lower()
    for w in open(f"data/dict/dict_{language}.txt", "r", encoding="UTF-8").readlines():
        if remove_accents(word) == remove_accents(w).replace("\n", ""):
            return True
    return False


def check_list(word, letters):
    if settings["debug"]["ACCEPT_ANY_LETTER"]:
        return True
    for l in remove_accents(word):
        if not l.lower() in letters:
            return False
    return True
