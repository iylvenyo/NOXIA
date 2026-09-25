import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

gi.require_version("Gsk", "4.0")

from gi.repository import Gsk

class MusicButton(Gtk.Button):

    def __init__(self):
        super().__init__(label="play sound")
        self.test_audio_file = Gtk.MediaFile.new_for_filename("test_sound.wav")
        self.test_audio_file.set_volume(0.75)

    # Play audio file
    def do_clicked(self):
        self.test_audio_file.prepared = True

        self.test_audio_file.play()
        self.test_audio_file.prepared = False
    
def on_activate(app):

    btn = MusicButton()

    music_win = Gtk.ApplicationWindow(application=app)
    music_win.set_child(btn)
    music_win.present()

app = Gtk.Application(application_id='music.demo')
app.connect('activate', on_activate)
app.run(None)
