import gi

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk # type: ignore

from graphics.config import DEFAULT_HEIGHT, DEFAULT_WIDTH
from backend.Terminal.terminal_tools import Terminal

class NoxiaTerminalWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(
            application=app,
            title="NOXIA Terminal",
        )

        Terminal.app = app

        self.set_default_size(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.label = Gtk.Label(label="")
        self.label.set_vexpand(True)
        self.label.set_valign(Gtk.Align.END)
        self.label.set_halign(Gtk.Align.START)

        self.scrollWindow = Gtk.ScrolledWindow()
        self.scrollWindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrollWindow.set_max_content_height(DEFAULT_HEIGHT - 50)
        self.scrollWindow.set_vexpand(True)
        self.scrollWindow.set_child(self.label)


        box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(10)
        box.set_margin_bottom(10)

        entry = Gtk.Entry()
        entry.set_placeholder_text("Type here...")
        entry.connect("activate", self.on_entry_activate)

        box.append(self.scrollWindow)
        box.append(entry)
        self.set_child(box)

    def on_entry_activate(self, entry):
        Terminal.parse(entry.get_text())
        self.update_label_text(Terminal.get_terminal_history())

        entry.set_text("")
        entry.set_placeholder_text("Type here...")

    def update_label_text(self, terminal_history):
        self.label.set_text("\n".join(terminal_history))
        self.scroll_to_bottom(self.scrollWindow.get_vadjustment())

    def scroll_to_bottom(self, adjustment):
        adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())