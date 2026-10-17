import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gsk", "4.0")
from gi.repository import Gtk, Gsk, GObject, Gio

# Get path for songs
from pathlib import Path
song_path1 = Path(__file__).resolve().parent / "songs" / "test1.wav"
song_path2 = Path(__file__).resolve().parent / "songs" / "test2.wav"
song_path3 = Path(__file__).resolve().parent / "songs" / "presentation_demo.mp3"


class MusicPlayer(Gtk.ApplicationWindow):

    def __init__(self, app):
            super().__init__(application = app, title = "NOXIA Music Player")

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
            self.play_btn = PlayButton(self, self.song_menu, self.song_array)
            
            # Pause Button
            self.pause_btn = PauseButton(self, self.song_menu, self.song_array)

            # Text box
            self.text_box = Gtk.Entry()
            self.text_buffer = Gtk.EntryBuffer()
            self.text_box.set_buffer(self.text_buffer)
            self.text_box.set_placeholder_text("song number (1-3)")
            self.text_box.connect("activate", self.on_text_input)

            # Make grid
            self.button_grid = Gtk.Grid()
            self.button_grid.attach(self.play_btn, 1, 1, 1, 1)
            self.button_grid.attach(self.pause_btn, 1, 2, 1, 1)
            self.button_grid.attach(self.text_box, 1, 3, 1, 1)
            self.set_child(self.button_grid)

    # Music player properties
    song1 = None
    song2 = None
    song3 = None
    play_btn = None
    pause_btn = None
    song_array = None
    song_menu = None
    button_grid = None

    def on_text_input(self, text_box):
        input = self.text_buffer.get_text()

        if (int(input) >= 1 and int(input) <= 3):
            self.current_song = self.song_array[int(input) - 1]

        # clear buffer
        self.text_buffer.delete_text(0, self.text_buffer.get_length())


class PlayButton(Gtk.Button):

    # Get music window attributes
    def __init__(self, parent_window, menu, song_array):
        super().__init__(label="play")
        self.parent_window = parent_window
        self.menu = menu
        self.song_array = song_array
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
    def __init__(self, parent_window, menu, song_array):
        super().__init__(label="pause")
        self.parent_window = parent_window
        self.menu = menu
        self.song_array = song_array
        self.song = self.parent_window.current_song

    # Pause audio file
    def do_clicked(self):
        self.song = self.parent_window.current_song
        self.song.pause()

