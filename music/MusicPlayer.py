import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gsk", "4.0")

from gi.repository import Gtk, Gsk, GObject, Gdk # type: ignore

songsDictionary = {
    "1": "sprites.wav",
    "2": "adventure.wav",
    "3": "presentation_demo.wav",
    "4": "lost.wav",
    "5": "strange.wav"
}
from graphics.config import ROOT_PATH
# Get path for songs
defaultPath = ROOT_PATH / "music" / "songs"

# Import CSS Stylesheet
style_path = ROOT_PATH / "ui" / "css" / "music_player_style.css"

class MusicPlayer(Gtk.ApplicationWindow):

    def __init__(self, app):
            super().__init__(application = app, title = "NOXIA Music Player")

            # Set size
            self.set_default_size(300, 300)

            # Add CSS provider
            self.style = Gtk.CssProvider()
            self.style.load_from_path(str(style_path))

            Gtk.StyleContext.add_provider_for_display(
                self.get_display(), self.style,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

            # Add CSS class for this window.
            self.add_css_class("music_window")

            # Set an inital song
            song_path = self.get_song_path("1")
            self.current_song = Gtk.MediaFile.new_for_filename(str(song_path))

            # Play button
            self.play_btn = PlayButton(self)
            self.play_btn.add_css_class("play_button")
            
            # Pause Button
            self.pause_btn = PauseButton(self)
            self.pause_btn.add_css_class("pause_button")

            # Volume Slider
            self.vol_slider = VolumeSlider(parent_window=self)

            # Text box
            self.text_box = Gtk.Entry()
            self.text_buffer = Gtk.EntryBuffer()
            self.text_box.set_buffer(self.text_buffer)
            self.text_box.set_placeholder_text("song number (1-5)")
            self.text_box.connect("activate", self.on_text_input)

            # Make grid
            self.button_grid = Gtk.Grid()

            # Add buttons, slider, and text box to grid
            self.button_grid.attach(self.play_btn, 1, 1, 1, 1)
            self.button_grid.attach(self.pause_btn, 2, 1, 1, 1)
            self.button_grid.attach(self.text_box, 1, 2, 1, 1)
            self.button_grid.attach(self.vol_slider, 1, 3, 1, 1)

            # Add grid to window and add css to grid
            self.set_child(self.button_grid)
            self.button_grid.add_css_class("button_grid")

    # When text box for song choice is activated
    def on_text_input(self, text_box):
        input = self.text_buffer.get_text()

        if input not in songsDictionary:
            # clear buffer
            self.text_buffer.delete_text(0, self.text_buffer.get_length())
            return

        if self.current_song is not None:
            self.current_song.pause()
            self.current_song = None

        if input in songsDictionary:
            # Get song path and create Gtk.MediaFile object
            song_path = self.get_song_path(input)
            self.current_song = Gtk.MediaFile.new_for_filename(str(song_path))

        # clear buffer
        self.text_buffer.delete_text(0, self.text_buffer.get_length())

    def get_song_path(self, song_key):
        if song_key in songsDictionary:
            print(defaultPath / songsDictionary[song_key])
            return defaultPath / songsDictionary[song_key]
        else:
            return None

class PlayButton(Gtk.Button):
    # Get music window attributes
    def __init__(self, parent_window):
        super().__init__(label="play")
        self.parent_window = parent_window

    # Play audio file
    def do_clicked(self):

        # Restart song if it has ended.
        if self.parent_window.current_song.get_ended():
            self.parent_window.current_song.seek(0)

        self.parent_window.current_song.play()

class PauseButton(Gtk.Button):

    # Get music window attributes
    def __init__(self, parent_window):
        super().__init__(label="pause")
        self.parent_window = parent_window

    # Pause audio file
    def do_clicked(self):

        if self.parent_window.current_song is None: return
        self.parent_window.current_song.pause()

class VolumeSlider(Gtk.Scale):

    # Initialize volume slider with range 0.0 to 1.0
    def __init__(self, parent_window):

        # Set parent window and make necessary object for parent class initializer
        adjustment_vals = Gtk.Adjustment.new(0.5, 0.0, 1.0, 0.1, 0.0, 0.0)
        self.parent_window = parent_window

        super().__init__(
        orientation = Gtk.Orientation.HORIZONTAL,
        adjustment = adjustment_vals
        )

    # Update volume on slider value change
    def do_value_changed(self):
        if self.parent_window is not None:
            self.parent_window.current_song.set_volume(self.get_value())