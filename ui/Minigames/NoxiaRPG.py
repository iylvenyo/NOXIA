import CharacterClasses
import gi
import random

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk


class NoxiaRPG(Gtk.ApplicationWindow):
    def __init__(self, **kargs):
        super().__init__(**kargs, title="Noxia RPG")
        
        self.classes = {
            "Warrior":CharacterClasses.Warrior,
            "Tank":CharacterClasses.Tank,
            "Mage":CharacterClasses.Mage,
        }

        self.enemies_defeated = 0

    def start_game(self):
        self.start_prompt()
    
    #Start screen
    def start_prompt(self):
        start_screen = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=50
        )
        
        title = Gtk.Label(label="NOXIA RPG")
        start_button = Gtk.Button(label="Start")


        start_screen.append(title)
        start_screen.append(start_button)

        start_button.connect("clicked", self.start_clicked)
        self.set_child(start_screen)


    def start_clicked(self, button):
        self.class_prompt()


    #Class selection screen
    def class_prompt(self):
        class_screen = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=50
        )

        title = Gtk.Label(label="Choose Your Class")
        for class_name in self.classes:
            button = Gtk.Button(label=class_name)
            button.connect("clicked", self.select_class, class_name)
            class_screen.append(button)
        

        class_screen.append(title)
        self.set_child(class_screen)


    #Set class for player 
    def select_class(self, button, character):
        self.player_character = self.classes[character]()
        self.main_screen()


    #Main game screen
    def main_screen(self):

        #Create enemy
        self.generate_enemy()

        main_screen = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=100
        )

        title = Gtk.Label(label="NOXIA RPG")
        main_screen.append(title)

        #Health and text display
        top_gui = Gtk.CenterBox()

        #Class moveset display
        bottom_gui = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10
        )
        self.player_health_label = Gtk.Label(label=f"Player Health: {self.player_character.health}")
        self.enemy_health_label = Gtk.Label(label=f"Enemy Health: {self.enemy_character.health}")


        #Battle text display
        self.text_output_box = Gtk.TextView()
        self.text_output_box.set_cursor_visible(False)
        self.text_output_box.set_hexpand(True)
        self.text_output_box.set_vexpand(True)
        self.text_scroll = Gtk.ScrolledWindow()
        self.text_scroll.set_child(self.text_output_box)

        top_gui.set_start_widget(self.player_health_label)
        top_gui.set_end_widget(self.enemy_health_label)
        top_gui.set_center_widget(self.text_scroll)


        #Class moveset buttons
        bottom_gui.append(self.generate_class_buttons())

        top_gui.set_vexpand(True)
        bottom_gui.set_vexpand(True)

        
        main_screen.append(top_gui)
        main_screen.append(bottom_gui)
        self.set_child(main_screen)


    #Create class moveset buttons
    def generate_class_buttons(self):
        bottom_gui = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=200
        )

        for move_name in self.player_character.moveset:
            button = Gtk.Button(label=move_name)
            button.connect("clicked", self.take_turn, move_name)
            bottom_gui.append(button)

        return bottom_gui

    
    #Create a random enemy 
    def generate_enemy(self):
        class_list = list(self.classes.keys())
        random_class = class_list[random.randint(0, len(class_list) - 1)]
        self.enemy_character = self.classes[random_class]()


    #Output text to screen
    def output_text(self, string):
        text_buffer = self.text_output_box.get_buffer()
        end = text_buffer.get_end_iter()
        text_buffer.insert(end, string + "\n")
        end = text_buffer.get_end_iter()
        self.text_output_box.scroll_to_iter(end, 0.0, False, 0.0, 1.0)


    #Player turn
    def take_turn(self, button, move_name):

        if move_name == "Block":
            self.output_text(f"Player {self.player_character.block()}")

        elif move_name == "Heal":
            self.output_text(f"Player has used heal")
            self.output_text(f"Player {self.player_character.heal(self.player_character.moveset[move_name])}")
            

        else:
            self.output_text(f"Player {self.player_character.class_name} uses {move_name}")
            self.output_text(f"Enemy {self.player_character.deal_damage(self.player_character.moveset[move_name], self.enemy_character)}")

        self.update_labels()

        #Check if enemy has been defeated on player turn
        if self.enemy_character.health <= 0:
            self.end_screen()

        else:
            self.enemy_turn()


    #Enemy turn
    def enemy_turn(self):
        moveset_list = list(self.enemy_character.moveset.keys())
        random_move = moveset_list[random.randint(0, len(moveset_list) - 1)]
        if random_move == "Block":
            self.output_text(f"Enemy {self.enemy_character.block()}")
        
        elif random_move == "Heal":
            self.output_text(f"Enemy has used heal")
            self.output_text(f"Enemy {self.enemy_character.heal(self.enemy_character.moveset[random_move])}")
                    
        
        else:
            self.output_text(f"Enemy {self.enemy_character.class_name} uses {random_move}")
            self.output_text(f"Player {self.enemy_character.deal_damage(self.enemy_character.moveset[random_move], self.player_character)}")
        
        self.update_labels()

        #Check if player has been defeated on enemy turn
        if self.player_character.health <= 0:
            self.end_screen()


    #Update health labels
    def update_labels(self):
        self.player_health_label.set_text(f"Health: {self.player_character.health}")
        self.enemy_health_label.set_text(f"Enemy Health: {self.enemy_character.health}")


    #Victory/defeat screen
    def end_screen(self):
            end_screen = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=50
            )
    
            title = Gtk.Label(label="Journey Results")
            main_menu_button = Gtk.Button(label="Go to main menu")
            main_menu_button.connect("clicked", self.main_menu_button)
            end_screen.append(title)


            if self.enemy_character.health <= 0:
                self.enemies_defeated += 1
                result_display = Gtk.Label(label="Victory!")
                continue_button = Gtk.Button(label="Continue")
                continue_button.connect("clicked", self.continue_button)
                end_screen.append(continue_button)

            if self.player_character.health <= 0:
                result_display = Gtk.Label(label="Defeat")
            
            end_screen.append(result_display)
            enemies_defeated_label = Gtk.Label(label=f"Enemies defeated: {self.enemies_defeated}")
            end_screen.append(enemies_defeated_label)
            end_screen.append(main_menu_button)

            self.set_child(end_screen)


    def continue_button(self, button):
        self.main_screen()


    def main_menu_button(self, button):
        self.enemies_defeated = 0
        self.start_game()


def on_activate(app):
    window = NoxiaRPG(application = app)
    window.set_default_size(1000, 1000)
    window.start_game()
    window.present()

app = Gtk.Application(application_id="com.example.App")
app.connect("activate", on_activate)
app.run(None)