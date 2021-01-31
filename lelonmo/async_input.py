from lelonmo.pynput import keyboard


class Input:
    def __init__(self, on_update, hide_char=""):
        self.text = list()
        self.text_shown = str()
        self.hide_char = hide_char
        self.on_update = on_update
        self.ctrl_pressed = False
    def run(self):    
        with keyboard.Listener(on_press=self._press, on_release=self.__release) as listener:
            listener.join()
        return self.text
    def _press(self, key):
        try:
            if not self.ctrl_pressed:
                key.char
                if self.hide_char:
                    self.text_shown = self.hide_char * (len(self.text)) + key.char
                else:
                    self.text_shown = self.text_shown + key.char
                self.text.append(key.char)
        except AttributeError:
            if key == keyboard.Key.backspace: # Delete
                try:
                    del self.text[-1]
                    s = list(self.text_shown)
                    del s[-1]
                    self.text_shown = "".join(s)
                except IndexError:
                    self.text = list()
                    self.text_shown = str()
            elif key == keyboard.Key.enter:
                return False
            elif key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r :
                self.ctrl_pressed = True
        self.on_update(self.text_shown)
    def __release(self, key):
        if key == keyboard.Key.ctrl:
            self.ctrl_pressed = False