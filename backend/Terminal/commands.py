## this script is a list of all commands for the noxia terminal
## each command is a unique class which inherits from the Command class
import random

from backend.Terminal.errors import Error


class Command:
    def __init__(self, argument):
        self.argument = argument

    def execute(self):
        raise NotImplementedError("Subclasses must implement the execute method.")


class Clear(Command):
    def __init__(self):
        from backend.Terminal.terminal_tools import Terminal
        super().__init__(Terminal)

    def execute(self):
        if self.argument is None:
            raise ValueError(Error("ArgumentNullError", "terminalHistory is null or undefined"))

        self.argument.clear_terminal_history()

class Funny(Command):
    responseList = [
        "Ask again later",
        "Eh no budy",
        "Very doubtful",
        "Yes",
        "Hilarious man",
        "Wow, your so funny, did you know that your so funny",
        "Hehe, its not that funny relax",
        "Do you actually want to know my real opinion?"
    ]

    def __init__(self, joke):
        
        super().__init__(joke)

    def execute(self):
        from backend.Terminal.terminal_tools import Terminal

        if self.argument is None:
            print(12012)
            Terminal.add_to_terminal_history(Error("ArgumentNullError", "joke is null or undefined"))
            return

        randomResponseIndex = random.randint(0, len(self.responseList) - 1)
        
        Terminal.add_to_terminal_history(f"Do I think your joke is funny? {self.responseList[randomResponseIndex]}")

class ChangeBackground(Command):
    def __init__(self):
        super().__init__(None)

    def execute(self):
        from backend.Terminal.terminal_tools import Terminal

        if Terminal.app is None or Terminal.app.graphics_window is None:
            raise ValueError(Error("ApplicationNullError", "Terminal.app or Terminal.app.graphics_window is null or undefined"))
        
        Terminal.app.graphics_window.cycle_graphic()

class ResetGraphics(Command):
    def __init__(self, argument=None):
        super().__init__(argument)

    def execute(self):
        from backend.Terminal.terminal_tools import Terminal
        
        if Terminal.app is None or Terminal.app.graphics_window is None:
            raise ValueError(Error("ApplicationNullError", "Terminal.app or Terminal.app.graphics_window is null or undefined"))
        
        graphics_window = Terminal.app.graphics_window
        graphics_window.simulation.reset()
        graphics_window.area.queue_render()

        Terminal.add_to_terminal_history("Anemone reset")

class Quit(Command):
    def __init__(self):
        super().__init__(None)

    def execute(self):
        from backend.Terminal.terminal_tools import Terminal

        if Terminal.app is None:
            raise ValueError(Error("ApplicationNullError", "Terminal.app is null or undefined"))
        
        Terminal.app.quit()