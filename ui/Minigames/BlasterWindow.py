import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

from graphics.blaster_renderer import BlasterRenderer


FRAME_DELAY_MS = 10


class BlasterWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="Blaster")
        self.set_default_size(900, 650)

        self.renderer = BlasterRenderer(900, 650)

        self.area = Gtk.DrawingArea()
        self.area.set_content_width(900)
        self.area.set_content_height(650)
        self.area.set_hexpand(True)
        self.area.set_vexpand(True)
        self.area.set_draw_func(self.on_draw)
        self.set_child(self.area)

        self.timer_id = GLib.timeout_add(
            FRAME_DELAY_MS,
            self.tick,
        )
        self.connect("close-request", self.on_close_request)

    def tick(self):
        self.renderer.update(
            self.area.get_width(),
            self.area.get_height(),
        )
        self.area.queue_draw()
        return GLib.SOURCE_CONTINUE

    def on_draw(self, area, cr, width, height):
        self.renderer.render(cr, width, height)

    def on_close_request(self, window):
        if self.timer_id is not None:
            GLib.source_remove(self.timer_id)
            self.timer_id = None

        return False


def on_activate(app):
    window = BlasterWindow(app)
    window.present()


if __name__ == "__main__":
    app = Gtk.Application(application_id="com.example.Blaster")
    app.connect("activate", on_activate)
    app.run(None)