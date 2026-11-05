import gi

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

        Terminal.app = app

        # Termainl Box Container
        terminalBox = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6,
        )

        terminalBox.set_valign(Gtk.Align.START)
        
        terminalBox.set_margin_start(10)
        terminalBox.set_margin_end(10)
        terminalBox.set_margin_top(10)
        terminalBox.set_margin_bottom(10)

        # Terminal History Label
        
        self.termainlHistory = Gtk.Label(label="")
        self.termainlHistory.set_valign(Gtk.Align.START)
        self.termainlHistory.set_halign(Gtk.Align.START)

        # Termainal Scroll Window
        self.scrollWindow = Gtk.ScrolledWindow()
        self.scrollWindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrollWindow.set_propagate_natural_height(True)
        self.scrollWindow.set_max_content_height(DEFAULT_HEIGHT - 100)
        self.scrollWindow.set_child(self.termainlHistory)     

        self.scrollWindow.set_visible(False)  

        # Termainl Command Line Prompt and Entry

        self.commandLinePrompt = Gtk.Label(label=BASE_LINE)

        commandLine = Gtk.Entry()
        commandLine.set_hexpand(True)
        commandLine.set_placeholder_text("")
        commandLine.set_has_frame(False)
        commandLine.add_css_class("command_line")
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

        self.termainlHistory.set_text("\n".join(terminal_history))
        self.scroll_to_bottom(self.scrollWindow.get_vadjustment())
        
    def scroll_to_bottom(self, adjustment):
        adjustment.set_value(adjustment.get_upper() - adjustment.get_page_size())

    def set_command_line_prompt(self, prompt):
        self.commandLinePrompt.set_label(prompt)