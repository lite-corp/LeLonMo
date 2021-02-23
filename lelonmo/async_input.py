keyboard = None # Avoid re-import on each Input call
class Input:
    def __init__(self, on_update, hide_char=""):
        global keyboard
        self.text = list()
        self.text_shown = list()
        self.hide_char = hide_char
        self.on_update = on_update
        from lelonmo.pynput import keyboard as keyboard_module
        keyboard = keyboard_module
    def run(self):    
        with keyboard.Listener(on_press=self._press) as listener:
            listener.join()
        self.flush_input()
        text = "".join(self.text)
        self.text = list()
        self.text_shown = list()
        return text
    def flush_input(self):
        try:
            import msvcrt
            while msvcrt.kbhit():
                msvcrt.getch()
        except ImportError:
            import sys, termios    #for linux/unix
            termios.tcflush(sys.stdin, termios.TCIOFLUSH)
    def _press(self, key):
        try:
            key.char # Detect non-char key (ctrl, esc, ...)
            if key.char == '\x03': # CTRL+C
                raise KeyboardInterrupt
            if len(self.text) < 65:
                if self.hide_char:
                    self.text_shown = [self.hide_char for i in range(len(self.text))]
                    self.text_shown.append(key.char)
                else:
                    self.text_shown.append(key.char)
                self.text.append(key.char)
            
        except AttributeError:
            if key == keyboard.Key.backspace: # Delete
                try:
                    del self.text[-1]
                    del self.text_shown[-1]
                except IndexError:
                    self.text = list()
                    self.text_shown = list()
                    self.on_update("")
            elif key == keyboard.Key.enter:
                self.text_shown = list()
                return False
        self.on_update("".join(self.text_shown))