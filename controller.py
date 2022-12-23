from pynput import keyboard


class Controller:
    def __init__(self):
        self.keyboard_settings = {}

        listener = keyboard.Listener(
            on_press=self.press_func)
        listener.start()

    def press_func(self, key):
        try:
            if key.char in self.keyboard_settings:
                for event in self.keyboard_settings[key.char]:
                    event[0](*event[1])
        except AttributeError:
            pass

    def add_key_event(self, key, event, args):
        if key in self.keyboard_settings:
            self.keyboard_settings[key] = [event, args] + self.keyboard_settings[key]
        else:
            self.keyboard_settings[key] = [[event, args]]
