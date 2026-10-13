import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gsk", "4.0")
from gi.repository import Gtk, Gsk

# Get path for songs
from pathlib import Path
song_path = Path(__file__).resolve().parent / "songs" / "test2.wav"


class MusicPlayer(Gtk.ApplicationWindow):

    def __init__(self, app):
            super().__init__(application = app, title = "NOXIA Music Player")

            # Create media stream
            self.song1 = Gtk.MediaFile.new_for_filename(str(song_path))
            self.song1.set_volume(1)

            # Play button
            self.play_btn = PlayButton(self)
            
            # Pause Button
            self.pause_btn = PauseButton(self)
                
            # Make grid
            self.button_grid = Gtk.Grid()
            self.button_grid.attach(self.play_btn, 1, 1, 1, 1)
            self.button_grid.attach(self.pause_btn, 1, 2, 1, 1)
            self.set_child(self.button_grid)

class PlayButton(Gtk.Button):

    # Get music window attributes
    def __init__(self, parent_window):
        super().__init__(label="play")
        self.parent_window = parent_window

    # Play audio file
    def do_clicked(self):
        if self.parent_window.song1.get_ended():
            self.parent_window.song1.seek(0)

        self.parent_window.song1.play()

class PauseButton(Gtk.Button):

    # Get music window attributes
    def __init__(self, parent_window):
        super().__init__(label="pause")
        self.parent_window = parent_window

    # Pause audio file
    def do_clicked(self):
        self.parent_window.song1.pause()

