import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gsk", "4.0")

from gi.repository import Gtk, Gsk, GObject, Gdk # type: ignore

songsDictionary = {
    "1": "test1.wav",
    "2": "test2.wav",
    "3": "presentation_demo.mp3"
}

# Get path for songs
from pathlib import Path
defaultPath = Path(__file__).resolve().parent / "songs"

# Import CSS Stylesheet
style_path = Path(__file__).resolve().parent.parent / "ui" / "css" / "music_player_style.css"

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

            self.current_song = None

            # Play button
            self.play_btn = PlayButton(self)
            self.play_btn.add_css_class("play_button")
            
            # Pause Button
            self.pause_btn = PauseButton(self)
            self.pause_btn.add_css_class("pause_button")

            # Text box
            self.text_box = Gtk.Entry()
            self.text_buffer = Gtk.EntryBuffer()
            self.text_box.set_buffer(self.text_buffer)
            self.text_box.set_placeholder_text("song number (1-3)")
            self.text_box.connect("activate", self.on_text_input)

            # Make grid
            self.button_grid = Gtk.Grid()

            # Add buttons and text box to grid
            self.button_grid.attach(self.play_btn, 1, 1, 1, 1)
            self.button_grid.attach(self.pause_btn, 2, 1, 1, 1)
            self.button_grid.attach(self.text_box, 1, 2, 1, 1)

            # Add grid to window and add css to grid
            self.set_child(self.button_grid)
            self.button_grid.add_css_class("button_grid")

    def on_text_input(self, text_box):
        input = self.text_buffer.get_text()

        if self.current_song is not None:
            self.current_song.pause()
            self.current_song = None

        if input in songsDictionary:
            # Get song path and create Gtk.MediaFile object
            song_path = self.get_song_path(input)
            self.current_song = Gtk.MediaFile.new_for_filename(str(song_path))
            self.current_song.set_volume(1)
            self.current_song.play()

        # clear buffer
        self.text_buffer.delete_text(0, self.text_buffer.get_length())

    def get_song_path(self, song_key):
        if song_key in songsDictionary:
            print(0)
            print(defaultPath / songsDictionary[song_key])
            return defaultPath / songsDictionary[song_key]
        else:
            return None

class PlayButton(Gtk.Button):
    # Get music window attributes
    def __init__(self, parent_window):
        super().__init__(label="play")
        self.parent_window = parent_window
        self.song = self.parent_window.current_song

    # Play audio file
    def do_clicked(self):
        print("play button clicked")

        # Update current song
        if self.parent_window.current_song is None:
            self.parent_window.on_text_input(self.parent_window.text_box)
        else:
            self.song = self.parent_window.current_song

        # Restart song if it has ended.
        if self.song.get_ended():
            self.song.seek(0)

        self.song.play()

class PauseButton(Gtk.Button):

    # Get music window attributes
    def __init__(self, parent_window):
        super().__init__(label="pause")
        self.parent_window = parent_window
        self.song = self.parent_window.current_song

    # Pause audio file
    def do_clicked(self):
        print("pause button clicked")

        if self.parent_window.current_song is None: return
        self.song = self.parent_window.current_song
        self.song.pause()

