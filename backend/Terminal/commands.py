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
            Terminal.add_to_terminal_history(Error("ArgumentNullError", "joke is null or undefined"))
            Terminal.add_to_terminal_history("\n")
            return

        randomResponseIndex = random.randint(0, len(self.responseList) - 1)
        
        Terminal.add_to_terminal_history(f"Do I think your joke is funny? {self.responseList[randomResponseIndex]}")
        Terminal.add_to_terminal_history("\n")

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
        Terminal.add_to_terminal_history("\n")

class Quit(Command):
    def __init__(self):
        super().__init__(None)

    def execute(self):
        from backend.Terminal.terminal_tools import Terminal

        if Terminal.app is None:
            raise ValueError(Error("ApplicationNullError", "Terminal.app is null or undefined"))
        
        Terminal.app.quit()

class Chat(Command):
    def __init__(self):
        super().__init__(None)
        self.inital_json_key = "FirstChat"
        self.response_object = MultiResponseHandler()
        self.old_key = self.inital_json_key

    def execute(self):
        self.response_object.print_at_key(self.inital_json_key)

    def inject_input(self, input_param):
        from backend.Terminal.terminal_tools import Terminal

        self.input = input_param

        if self.response_object.dialogue[self.old_key][str(self.input)]["next"] not in self.response_object.dialogue:
            return

        next_key = self.response_object.dialogue[self.old_key][str(self.input)]["next"]

        if next_key is None: 
            Terminal.return_command()
            return
        
        self.old_key = next_key

        self.response_object.print_at_key(next_key)

class MultiResponseHandler():
    def __init__(self):
        
        from backend.content_manager import ContentManager

        self.input = input

        content_manager = ContentManager()

        self.dialogue = content_manager.dialogue

    def print_at_key(self, key):
        from backend.Terminal.terminal_tools import Terminal

        if self.dialogue is None: return

        Terminal.add_to_terminal_history(self.dialogue[key]["Response"])
        Terminal.add_to_terminal_history("\n")

        temp_dict = self.dialogue[key]

        for i in range(1, 5):
            if str(i) in temp_dict:
                Terminal.add_to_terminal_history(self.dialogue[key][str(i)]["originalResponse"])