#!/usr/bin/env python3
# Starts the application

import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gsk", "4.0")

from gi.repository import Gtk, Gsk # type: ignore

# Noxia terminal imports
from ui.windows.terminal_window import NoxiaTerminalWindow

# Noxia graphics imports
from ui.windows.graphics_window import NoxiaGraphicsWindow

# Noxia audio imports
from music.MusicPlayer import MusicPlayer

class NoxiaApplication(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.iylvenyo.noxia",
        )

        self.terminal_window = None
        self.graphics_window = None
        self.music_player = None

    def do_activate(self):
        self.present_terminal_window()

    def present_terminal_window(self):
        if self.terminal_window is None:
            self.terminal_window = NoxiaTerminalWindow(self)
        self.terminal_window.present()

    def present_graphics_window(self):
        if self.graphics_window is None:
            self.graphics_window = NoxiaGraphicsWindow(self)
        self.graphics_window.present()

    def present_music_player_window(self):
        print("Opening")
        if self.music_player is None:
            self.music_player = MusicPlayer(self)
        self.music_player.present()


def main():
    app = NoxiaApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
