# LeLonMo
## ANSI for windows
in regedit go to Computer\HKEY_CURRENT_USER\Console
Create DWORD "VirtualTerminalLevel" entry set to 1 (0x00000001)

## Comment installer le jeu
 - Cliquer sur télécharger le code
 - Extraire le dossier
 - Appuyer sur la touche windows du clavier
 - Taper regedit
 - Faire \[ENTRER\]
 - Copier/Coller "HKEY_CURRENT_USER\Console" sans les guillemets dans la barre en haut
 - Cliquer-droit dans l'espace vide à coté des valeurs
 - Faire Nouveau > DWORD...
 - Renomner la valeur "VirtualTerminalLevel" sans les guillemets
 - Double-cliquer sur la valeur et entrer 1 dans le champ de texte
 - Lancez menu.py avec python

## Contributions
 - ansicolors  by Jonathan Eunice
 - consolemenu by aegirhall
