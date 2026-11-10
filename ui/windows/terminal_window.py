import gi
from gi.repository import GLib

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk # type: ignore
from graphics.config import DEFAULT_HEIGHT, DEFAULT_WIDTH, ROOT_PATH, BASE_LINE, RESPONSE_LINE
from backend.Terminal.terminal_tools import Terminal

style_path = ROOT_PATH / "ui" / "css" / "terminal_window.css"

class NoxiaTerminalWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(
            application=app,
            title="NOXIA Terminal",
        )
        self.set_default_size(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.style = Gtk.CssProvider()
        self.style.load_from_path(str(style_path))

        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), self.style,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.add_css_class("terminal_window")

        self.headerBar = Gtk.HeaderBar()
        self.headerBar.add_css_class("header_bar")

        self.titleLabel = Gtk.Label(label=self.get_title())
        self.titleLabel.add_css_class("header_title")
        self.titleLabel.set_halign(Gtk.Align.START)

        self.headerBar.set_title_widget(Gtk.Box())
        self.headerBar.pack_start(self.titleLabel)
        self.set_titlebar(self.headerBar)

        Terminal.app = app

        # Termainl Box Container
        terminalBox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )
        terminalBox.add_css_class("terminal_box")
        terminalBox.set_valign(Gtk.Align.START)
        
        terminalBox.set_margin_start(10)
        terminalBox.set_margin_end(10)
        terminalBox.set_margin_top(10)
        terminalBox.set_margin_bottom(10)

        # Terminal History Label
        self.terminalHistory = Gtk.Label(label="")
        self.terminalHistory.set_valign(Gtk.Align.START)
        self.terminalHistory.set_halign(Gtk.Align.START)
        self.terminalHistory.add_css_class("terminal_text")
        self.terminalHistory.set_wrap(False)
        self.terminalHistory.set_xalign(0)

        # Termainal Vertical Scroll Window
        self.scrollWindow = Gtk.ScrolledWindow()
        self.scrollWindow.set_policy(Gtk.PolicyType.EXTERNAL, Gtk.PolicyType.AUTOMATIC)
        self.scrollWindow.set_propagate_natural_width(False)
        self.scrollWindow.set_propagate_natural_height(True)
        self.scrollWindow.set_max_content_height(DEFAULT_HEIGHT - 100)
        self.scrollWindow.set_child(self.terminalHistory)   
        self.scrollWindow.set_visible(False)
        self.scrollWindow.add_css_class("scroll_window")
        self.scrollWindow.set_overlay_scrolling(False)

        # Termainl Command Line Prompt and Entry

        self.commandLinePrompt = Gtk.Label(label=BASE_LINE)
        self.commandLinePrompt.add_css_class("terminal_text")

        commandLine = Gtk.Entry()
        commandLine.set_hexpand(True)
        commandLine.set_placeholder_text("")
        commandLine.set_has_frame(False)
        commandLine.add_css_class("command_line")
        commandLine.add_css_class("terminal_text")
        commandLine.connect("activate", self.on_entry_activate)

        commandLineBox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
        )
        commandLineBox.append(self.commandLinePrompt)
        commandLineBox.append(commandLine)
        
        # Append Termianl History and Command Line to Terminal Box
        terminalBox.append(self.scrollWindow)
        terminalBox.append(commandLineBox)

        self.set_child(terminalBox)

    def on_entry_activate(self, entry):

        if entry.get_text().strip() == "":
            return

        Terminal.parse(entry.get_text())

        self.update_termainl_history(Terminal.get_terminal_history())

        entry.set_text("")

    def update_termainl_history(self, terminal_history):

        if len(terminal_history) == 1 and terminal_history[0].strip() == "":
                self.scrollWindow.set_visible(False)
        elif len(Terminal.get_terminal_history()) == 0:
            self.scrollWindow.set_visible(False)
        else:
            self.scrollWindow.set_visible(True)

        self.terminalHistory.set_text("\n".join(terminal_history))

        GLib.timeout_add(20, self.scroll_to_bottom)
        
    def scroll_to_bottom(self):
        adjustment = self.scrollWindow.get_vadjustment()
        adjustment.set_value(max(adjustment.get_lower(), adjustment.get_upper() - adjustment.get_page_size()))

        return GLib.SOURCE_REMOVE

    def set_command_line_prompt(self, prompt):
        self.commandLinePrompt.set_label(prompt)