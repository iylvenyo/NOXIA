import cairo
import gi

gi.require_version("Gtk", "4.0")

from gi.repository import GLib, Gdk, Gtk  # pyright: ignore[reportMissingModuleSource]

from graphics.config import DEFAULT_HEIGHT, DEFAULT_WIDTH, DELAY_US
from graphics.simulation import NoxiaSimulation
from backend.Terminal.terminal_tools import Terminal

class NoxiaWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(
            application=app,
            title="NOXIA Terminal",
        )
        
        self.set_default_size(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.label = Gtk.Label(label="")

        self.terminalObj = Terminal()

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        entry = Gtk.Entry()
        entry.set_placeholder_text("Type here...")
        entry.connect("activate", self.on_entry_activate)
        
        self.label.set_vexpand(True)
        self.label.set_valign(Gtk.Align.END)
        self.label.set_halign(Gtk.Align.START)

        box.append(self.label)
        box.append(entry)
        
        self.set_child(box)

    def on_entry_activate(self, entry):
        self.terminalObj.parse(entry.get_text())

        self.update_label_text(self.terminalObj.get_terminal_history())
        entry.set_text("")
        entry.set_placeholder_text("Type here...")

    def update_label_text(self, terminalHistory):
        if len(terminalHistory) == 0:
            self.label.set_text("")
            return

        temp = ""
        for text in terminalHistory:
            temp += text + "\n"

        self.label.set_text(temp)


        
    # def tick(self):
    #     self.simulation.step()
    #     self.area.queue_draw()

    #     return True

    # def resize_noxia(self, area, width, height):
    #     self.simulation.width = width
    #     self.simulation.height = height

    # def draw_noxia(self, area, context, width, height):
    #     context.set_source_rgb(0.0, 0.0, 0.0)
    #     context.paint()

    #     context.set_antialias(cairo.ANTIALIAS_NONE)

    #     context.set_line_cap(cairo.LINE_CAP_ROUND)
    #     context.set_line_join(cairo.LINE_JOIN_BEVEL)

    #     for command in self.simulation.commands:
    #         red, green, blue, alpha = command.color

    #         context.set_source_rgba(red, green, blue, alpha)
    #         context.set_line_width(command.width)

    #         context.move_to(command.x1, command.y1)
    #         context.line_to(command.x2, command.y2)
    #         context.stroke()

    # def key_pressed(self, controller, keyval, keycode, modifiers):
    #     if keyval in (Gdk.KEY_Escape, Gdk.KEY_q, Gdk.KEY_Q):
    #         self.close()
    #         return True

    #     if keyval in (Gdk.KEY_r, Gdk.KEY_R):
    #         self.simulation.reset()
    #         self.area.queue_draw()
    #         return True

    #     return False
