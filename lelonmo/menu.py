from . import main_offline, main_online, settings_menu
from .colors.colors import *
from .consolemenu import MenuFormatBuilder, SelectionMenu
from .consolemenu.format import MenuBorderStyleType
from .persist_data import DATA as settings

version = settings["version"]


def bye():
    print("Au revoir")
    exit()


menu_format = MenuFormatBuilder().set_border_style_type(MenuBorderStyleType.HEAVY_BORDER) \
    .set_prompt(">> ") \
    .set_title_align('center') \
    .set_subtitle_align('center') \
    .set_left_margin(4) \
    .set_right_margin(4) \
    .show_header_bottom_border(True)


def main():
    select = ["Mode Local", "Mode en Ligne", "Options", "Quitter"]
    link = [main_offline.main_loop, main_online.main_online,
            settings_menu.main, bye]
    menu = SelectionMenu(
        select, f"{blue('L')}{yellow('e')}{blue('L')}{magenta('o')}{cyan('n')}{green('M')}{magenta('o')} {red(f'v{version}')}",
        subtitle="Le jeu du long mot",
        prologue_text="Choisisser votre mode de jeu :",
        show_exit_option=False,
        formatter=menu_format
    )
    while True:
        menu.show()
        menu.join()
        link[menu.selected_option]()


if __name__ == "__main__":
    main()
