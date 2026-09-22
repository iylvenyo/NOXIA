#!/usr/bin/env python3
# Starts the application

import sys
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk
from ui.window import NoxiaWindow


class NoxiaApplication(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.iylvenyo.noxia",
        )

        self.window = None

    def do_activate(self):
        if self.window is None:
            self.window = NoxiaWindow(self)

        self.window.present()


def main():
    app = NoxiaApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
