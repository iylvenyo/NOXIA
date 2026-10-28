import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gsk", "4.0")
from gi.repository import Gtk, Gsk, GObject, Gdk

# Get path for songs
from pathlib import Path
song_path1 = Path(__file__).resolve().parent / "songs" / "test1.wav"
song_path2 = Path(__file__).resolve().parent / "songs" / "test2.wav"
song_path3 = Path(__file__).resolve().parent / "songs" / "presentation_demo.mp3"

# Import CSS Stylesheet
style_path = Path(__file__).resolve().parent.parent / "ui" / "music_player_style.css"


class MusicPlayer(Gtk.ApplicationWindow):

    def __init__(self, app):
            super().__init__(application = app, title = "NOXIA Music Player")

            # Set size
            self.set_default_size(300, 300)

            # Add CSS provider
            self.style = Gtk.CssProvider()
            self.style.load_from_path(str(style_path))
            Gtk.StyleContext.add_provider_for_display(
                Gdk.Display.get_default(), self.style,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

            # Add CSS class for this window.
            self.add_css_class("music_window")

            # Create media stream for song 1
            self.song1 = Gtk.MediaFile.new_for_filename(str(song_path1))
            self.song1.set_volume(1)

            # Create media stream for song 2
            self.song2 = Gtk.MediaFile.new_for_filename(str(song_path2))
            self.song2.set_volume(1)

            # Create media stream for song 3
            self.song3 = Gtk.MediaFile.new_for_filename(str(song_path3))
            self.song3.set_volume(1)

            # Make array of songs
            self.song_array = [self.song1, self.song2, self.song3]

            # Set current song
            self.current_song = self.song1

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
        user_input = self.text_buffer.get_text()

        # Handle bad input
        if not isinstance(user_input, int):
            self.text_buffer.delete_text(0, self.text_buffer.get_length())
            return

        # If user input is within range, update current song
        if (int(user_input) >= 1 and int(user_input) <= 3):
            self.current_song = self.song_array[int(user_input) - 1]

        # clear buffer
        self.text_buffer.delete_text(0, self.text_buffer.get_length())


class PlayButton(Gtk.Button):

    # Get music window attributes
    def __init__(self, parent_window):
        super().__init__(label="play")
        self.parent_window = parent_window
        self.song = self.parent_window.current_song

    # Play audio file
    def do_clicked(self):

        # Update current song
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
        self.song = self.parent_window.current_song
        self.song.pause()

