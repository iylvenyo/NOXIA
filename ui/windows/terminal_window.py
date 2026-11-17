import gi
from gi.repository import GLib # type: ignore

gi.require_version("Gtk", "4.0")

from gi.repository import Gtk, Gdk # type: ignore
from graphics.config import DEFAULT_HEIGHT, DEFAULT_WIDTH, ROOT_PATH, BASE_LINE, RESPONSE_LINE
from backend.Terminal.terminal_tools import Terminal

style_path = ROOT_PATH / "ui" / "css" / "terminal_window.css"

class NoxiaTerminalWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(
            application=app,
            title="NOXIA Terminal",
        )

        self.app = app

        # Set the size of the window and load the css file
        self.set_default_size(DEFAULT_WIDTH, DEFAULT_HEIGHT)
        self.style = Gtk.CssProvider()
        self.style.load_from_path(str(style_path))

        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), self.style,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.add_css_class("terminal_window")

        # Create a custom headerbar with a custom title and assign it to the window
        self.headerBar = Gtk.HeaderBar()
        self.headerBar.add_css_class("header_bar")

        self.titleLabel = Gtk.Label(label=self.get_title()) # type: ignore
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

        self.commandLine = Gtk.Entry()
        self.commandLine.set_hexpand(True)
        self.commandLine.set_placeholder_text("")
        self.commandLine.set_has_frame(False)
        self.commandLine.add_css_class("command_line")
        self.commandLine.add_css_class("terminal_text")
        self.commandLine.connect("activate", self.on_entry_activate)

        commandLineBox = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=6,
        )
        commandLineBox.append(self.commandLinePrompt)
        commandLineBox.append(self.commandLine)
        
        # Append Termianl History and Command Line to Terminal Box
        terminalBox.append(self.scrollWindow)
        terminalBox.append(commandLineBox)

        self.set_child(terminalBox)

        # Keyboard input controller
        controller = Gtk.EventControllerKey()
        controller.connect("key_pressed", self.on_key_pressed)
        self.add_controller(controller)

        self.connect("close_request", self.on_close_request)
    
    def on_close_request(self, window):
        if Terminal.app is not None:
            Terminal.app.quit()
        return False
    
    def on_key_pressed(self, controller, keyval, keycode, state):
        match keyval:
            case Gdk.KEY_Up:
                Terminal.cycle_command_history_up()
                return True
            case Gdk.KEY_Down:
                Terminal.cycle_command_history_down()
                return True
        return False

    def on_entry_activate(self, entry):

        # If the entry is empty, exit
        if entry.get_text().strip() == "":
            return

        # Run the command parsing method from the terminal_tool.py file
        Terminal.parse(entry.get_text())

        # Update the terminal
        self.update_termainl_history(Terminal.get_terminal_history())

        # Reset the entry field
        entry.set_text("")

    def set_entry_text(self, text):
        self.commandLine.set_text(text)

    def get_entry_text(self):
        return self.commandLine.get_text()

    def update_termainl_history(self, terminal_history):
        # If there is only a single entry in the terminal history and it is an empty string, turn off the scroll bar
        if len(terminal_history) == 1 and terminal_history[0].strip() == "":
                self.scrollWindow.set_visible(False)
        # If there are zero entries in the terminal history, turn off the scroll bar
        elif len(Terminal.get_terminal_history()) == 0:
            self.scrollWindow.set_visible(False)
        # Otherwise, there must be at least a single history entry that is not an empty string, turn on the scroll bar
        else:
            self.scrollWindow.set_visible(True)

        self.terminalHistory.set_text("\n".join(terminal_history))

        # Give Gtk 20ms to calculate the new terminal history dimensions before automatically scrolling to the bottom of the scroll window
        GLib.timeout_add(20, self.scroll_to_bottom)
        
    def scroll_to_bottom(self):
        adjustment = self.scrollWindow.get_vadjustment()
        adjustment.set_value(max(adjustment.get_lower(), adjustment.get_upper() - adjustment.get_page_size()))

        return GLib.SOURCE_REMOVE

    def set_command_line_prompt(self, prompt):
        self.commandLinePrompt.set_label(prompt)

    def set_command_line_placeholder(self, placeholder):
        self.commandLine.set_placeholder_text(placeholder)