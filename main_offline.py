import letter_generator
import word_check
from getpass import getpass
from persist_data import *
from colors.colors import *

score_j1 = 0
score_j2 = 0

def human_to_bool(q: str):
    yes = ["oui", "yes", "o", "y"]
    no  = ["non", "no", "n"]
    while True:
        r = input(q)
        if r.lower() in yes:
            return True
        elif r.lower() in no:
            return False
        print(red("La réponse n'est pas valide, entrez oui on non."))

def intro():
    global name_j1
    global name_j2
    if not SKIP_INTRO:
        letters = str(LETTER_NUMBER) if len(str(LETTER_NUMBER)) > 1 else str(LETTER_NUMBER) + " "
        intro_txt = open("data\\welcome_screen.txt", "r").read().replace(
            "%%letters%%", bold(letters))
        intro_ln = intro_txt.splitlines(keepends=False)
        for i, l in enumerate(intro_ln):
            if i in range(4,9):
                l = l.replace("L", blue("L"))
                l = l.replace("e", yellow("e"))
                l = l.replace("o", magenta("o"))
                l = l.replace("n", cyan("n"))
                l = l.replace("M", green("M"))
            if i == 10:
                l = l.replace("By Alexis Rossfelder", red("By Alexis Rossfelder"))
            print(l)

    print("Les lettres avec lesquelles vous devez composer votre mot sont ")
    name_j1 = input(cyan("Joueur 1, veuiller entrer votre nom : "))
    name_j1 = cyan("Joueur 1" if not name_j1 else name_j1)
    name_j2 = input(magenta("Joueur 2, veuiller entrer votre nom : "))
    name_j2 = magenta("Joueur 2" if not name_j2 else name_j2)
        


def game():
    global score_j1
    global score_j2

    letters = letter_generator.generate((97,123), LETTER_NUMBER, LANGUAGE)
    
    for i in letters:
        print(bold(i), " ", end="")
    print()
    j1 = getpass(f"{name_j1}, entrez votre mot à l'abris des regards indiscrets : ")
    while not (word_check.check_dict(j1, LANGUAGE) and word_check.check_list(j1, letters)):
        j1 = getpass(red("Votre mot n'est pas valide, veuillez en entrer un autre : "))

    j2 = getpass(f"{name_j2}, entrez votre mot à l'abris des regards indiscrets : ")
    while not (word_check.check_dict(j2, LANGUAGE) and word_check.check_list(j2, letters)):
        j2 = getpass(red("Votre mot n'est pas valide, veuillez en entrer un autre : "))
    

    print(f"Les mots: \nJ1 : {cyan(j1)}\nJ2 : {magenta(j2)}")
    if len(j1) > len(j2):
        print(cyan(f"{name_j1} a gagné"))
    elif len(j2) > len(j1):
        print(magenta(f"{name_j2} a gagné"))
    else:
        print(yellow("Egalité parfaite"))
    
    score_j1 += len(j1)
    score_j2 += len(j2)
    print(f"{name_j1} a {score_j1} points et {name_j2} en a {score_j2}. ")

def main_loop():
    intro()
    game()
    while human_to_bool(italic("Voulez-vous rejouer ?\n")): game()

if __name__ == "__main__":
    main_loop()


