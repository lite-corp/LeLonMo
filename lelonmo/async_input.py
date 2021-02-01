from lelonmo.pynput import keyboard


class Input:
    def __init__(self, on_update, hide_char=""):
        self.text = list()
        self.text_shown = str()
        self.hide_char = hide_char
        self.on_update = on_update
    def run(self):    
        with keyboard.Listener(on_press=self._press) as listener:
            listener.join()
        return self.text
    def _press(self, key):
        try:
            key.char # Detect non-char key (ctrl, esc, ...)
            if key.char == '\x03': # CTRL+C
                raise KeyboardInterrupt
            if self.hide_char:
                self.text_shown = self.hide_char * (len(self.text)) + key.char
            else:
                self.text_shown = self.text_shown + key.char
            self.text.append(key.char)
        except AttributeError:
            if key == keyboard.Key.backspace: # Delete
                try:
                    if len(self.text) == 1:
                        self.text_shown = ""
                    else:
                        del self.text[-1]
                        s = list(self.text_shown)
                        del s[-1]
                        self.text_shown = "".join(s)
                except IndexError:
                    self.text = list()
                    self.text_shown = str()
            elif key == keyboard.Key.enter:
                return False
        self.on_update(self.text_shown)