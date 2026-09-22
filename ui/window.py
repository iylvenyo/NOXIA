import cairo
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gdk, Gtk

from graphics.config import DEFAULT_HEIGHT, DEFAULT_WIDTH, DELAY_US
from graphics.simulation import NoxiaSimulation

class NoxiaWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(
            application=app,
            title="NOXIA",
        )

        self.set_default_size(DEFAULT_WIDTH, DEFAULT_HEIGHT)

        self.simulation = NoxiaSimulation()

        self.area = Gtk.DrawingArea()
        self.area.set_content_width(DEFAULT_WIDTH)
        self.area.set_content_height(DEFAULT_HEIGHT)

        self.area.set_draw_func(self.draw_noxia)
        self.area.connect("resize", self.resize_noxia)

        self.set_child(self.area)

        key_controller = Gtk.EventControllerKey()
        key_controller.connect("key-pressed", self.key_pressed)

        self.add_controller(key_controller)

        GLib.timeout_add(DELAY_US // 1000, self.tick)

    def tick(self):
        self.simulation.step()
        self.area.queue_draw()

        return True

    def resize_noxia(self, area, width, height):
        self.simulation.width = width
        self.simulation.height = height

    def draw_noxia(self, area, context, width, height):
        context.set_source_rgb(0.0, 0.0, 0.0)
        context.paint()

        context.set_antialias(cairo.ANTIALIAS_NONE)

        context.set_line_cap(cairo.LINE_CAP_ROUND)
        context.set_line_join(cairo.LINE_JOIN_BEVEL)

        for command in self.simulation.commands:
            red, green, blue, alpha = command.color

            context.set_source_rgba(red, green, blue, alpha)
            context.set_line_width(command.width)

            context.move_to(command.x1, command.y1)
            context.line_to(command.x2, command.y2)
            context.stroke()

    def key_pressed(self, controller, keyval, keycode, modifiers):
        if keyval in (Gdk.KEY_Escape, Gdk.KEY_q, Gdk.KEY_Q):
            self.close()
            return True

        if keyval in (Gdk.KEY_r, Gdk.KEY_R):
            self.simulation.reset()
            self.area.queue_draw()
            return True

        return False
