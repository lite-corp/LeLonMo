######### SETTINGS ########

# Nombre de lettres générées
LETTER_NUMBER = 7

# Langue du dictionnaire
DICT_LANGUAGE = "fr"

# Langue du jeu
GAME_LANGUAGE = "fr"

###########################


########## DEBUG ##########

# Cette fonction permet de générer une liste ayant forcément une réponse
USE_INPROVED_GENERATOR = True # Sur True, le temps d'éxecution est plus long

# Sur True, la vérification par dicitionnaire est désactivée
ACCEPT_ANY_WORD = False

# Sur True, la vérification des lettres de la liste est désactivée
ACCEPT_ANY_LETTER = False

# Affiche les mots utilisés pour la génération aléatoire
DEBUG_WORDS = False

# Passe l'introduction
SKIP_INTRO = False
###########################


version = "0.2-dev"

##############################################
########## DEBUG RUN DO NOT EDIT #############
##############################################
if __name__ == "__main__":
    import main_offline
    main_offline.intro()
    main_offline.game()