import gi
import random

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class ClickingMinigame(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title="Minigame")
        
        self.fixed = Gtk.Fixed()
        self.set_child(self.fixed)
        self.score = 0
        self.max_button_amount = 5
        self.game_x_coords = 800
        self.game_y_coords = 800


    def start_game(self):
        for _ in range(self.max_button_amount):
            button = self.generate_button()
            self.randomize_buttons(button)


    def randomize_buttons(self, button):
        x = random.randint(100, self.game_x_coords - 200)
        y = random.randint(100, self.game_y_coords - 200)

        if button.get_parent() == self.fixed:
            self.fixed.move(button, x, y)
        else:
            self.fixed.put(button, x, y)


    def generate_button(self):
        button = Gtk.Button(label="Click")
        button.connect("clicked", self.on_button_clicked)
        return button
    

    def on_button_clicked(self, button):
        self.randomize_buttons(button)
        self.score += 1


        
def on_activate(app):
    window = ClickingMinigame(application = app)
    window.set_default_size(1000, 1000)
    window.start_game()
    window.present()

app = Gtk.Application(application_id="com.example.App")
app.connect("activate", on_activate)
app.run(None)