from consolemenu.console_menu import MenuItem
from consolemenu import *
from consolemenu.format import *
from colors.colors import *
from persist_data import *
import menu


def main(c=(-1, -1, -1)):
    menu_format = MenuFormatBuilder()\
        .set_border_style_type(MenuBorderStyleType.DOUBLE_LINE_OUTER_LIGHT_INNER_BORDER) \
        .set_prompt(">> ") \
        .set_title_align('center') \
        .set_subtitle_align('center') \
        .set_left_margin(4) \
        .set_right_margin(4) \
        .show_header_bottom_border(True)

    settings_menus = [
        ["Game Settings", [
            ["Use improved generator", [
                "Yes (recomended)",
                "No"]],
            ["General Language (incoming)", [
                "Français",
                "English"
            ]],
            ["Use colored text", [
                "Yes (recommended)",
                "No"
            ]]]],
        ["Gameplay", [
            ["Letter number", list(range(3, 11))],
            ["Word checking language", [
                'French',
                'English'
            ]]]],
        ["Online Settings", [
            ["Reset name", [
                "Confirm ?"
            ]],
            ["Reset UUID", [
                "Confirm ?"
            ]]
        ]],
        ["Debug [Advanced]", [
            ["ACCEPT_ANY_WORD", list(range(0, 2))],
            ["ACCEPT_ANY_LETTER", list(range(0, 2))],
            ["DEBUG_WORDS", list(range(0, 2))],
            ["SKIP_INTRO", list(range(0, 2))],
        ]]
    ]
    settings_link = [
        ["settings", [
            ["USE_INPROVED_GENERATOR", [
                True,
                False]],
            ["GAME_LANGUAGE", [
                "fr",
                "en"
            ]],
            ["USE_COLORS", [
                True,
                False
            ]]]],
        ["game", [
            ["LETTER_NUMBER", list(range(3, 11))],
            ["DICT_LANGUAGE", [
                'fr',
                'en'
            ]]]],
        ["online", [
            ["name", [""]],
            ["uuid", [""]]

            ]],
        ["debug", [
            ["ACCEPT_ANY_WORD", [not bool(i) for i in range(0, 2)]],
            ["ACCEPT_ANY_LETTER", [not bool(i) for i in range(0, 2)]],
            ["DEBUG_WORDS", [not bool(i) for i in range(0, 2)]],
            ["SKIP_INTRO", [not bool(i) for i in range(0, 2)]],
        ]]
    ]
    c1, c2, c3 = c

    try:
        if c1 == -1:
            l = [i[0] for i in settings_menus]
            main_menu = SelectionMenu(
                l,
                title=f"{blue('L')}{yellow('e')}{blue('L')}{magenta('o')}{cyan('n')}{green('M')}{magenta('o')} {red(DATA['version'])}",
                prologue_text="Paramètres",
                formatter=menu_format
            )
            main_menu.start()
            main_menu.join()
            c1 = main_menu.selected_option
        if c2 == -1:
            l = [i[0] for i in settings_menus[c1][1]]
            main_menu = SelectionMenu(
                l,
                title=f"{blue('L')}{yellow('e')}{blue('L')}{magenta('o')}{cyan('n')}{green('M')}{magenta('o')} {red(DATA['version'])}",
                prologue_text=settings_menus[c1][0],
                formatter=menu_format
            )
            main_menu.start()
            main_menu.join()
            c2 = main_menu.selected_option
        if c3 == -1:
            l = [str(i) for i in settings_menus[c1][1][c2][1]]
            main_menu = SelectionMenu(
                l,
                title=f"{blue('L')}{yellow('e')}{blue('L')}{magenta('o')}{cyan('n')}{green('M')}{magenta('o')} {red(DATA['version'])}",
                prologue_text=settings_menus[c1][1][c2][0],
                formatter=menu_format
            )
            main_menu.start()
            main_menu.join()
            c3 = main_menu.selected_option
            master = settings_link[c1][0]
            key = settings_link[c1][1][c2][0]
            value = settings_link[c1][1][c2][1][c3]
            update_key(master=master, key=key, value=value)
            main()
    except IndexError:
        if c3 != -1:
            c3 = -1
            c2 = -1
        elif c2 != -1:
            c2 = -1
            c1 = -1
        elif c1 != -1:
            menu.main()
        main(c=(c1, c2, c3))



if __name__ == "__main__":
    main()
