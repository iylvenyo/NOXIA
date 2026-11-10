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
        # Manually adds a reference to the Terminal as the argumnet
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

        # If there is no argument, throw a null error
        if self.argument is None:
            Terminal.add_to_terminal_history(Error("ArgumentNullError", "joke is null or undefined"))
            Terminal.add_to_terminal_history("\n")
            return

        # Get a random response from the respose list
        randomResponseIndex = random.randint(0, len(self.responseList) - 1)

        # Add the response to the terminal
        Terminal.add_to_terminal_history(f"Do I think your joke is funny? {self.responseList[randomResponseIndex]}")

class ChangeBackground(Command):
    def __init__(self):
        super().__init__(None)

    def execute(self):
        from backend.Terminal.terminal_tools import Terminal

        # If the graphics window is null, throw a null error
        if Terminal.app is None or Terminal.app.graphics_window is None:
            raise ValueError(Error("ApplicationNullError", "Terminal.app or Terminal.app.graphics_window is null or undefined"))

        # Otherwise, change the background graphic
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

class Help(Command):
    def __init__(self):
        super().__init__(None)

        # Get the path to the help.json file
        from graphics.config import ROOT_PATH
        help_path = ROOT_PATH / "backend" / "json" / "help.json"

        self.inital_json_key = "Start"

        # Load the json file
        self.response_object = MultiResponseHandler(help_path)
        self.old_key = self.inital_json_key

    def execute(self):
        self.response_object.print_at_key(self.inital_json_key)

    def inject_input(self, input_param):
            from backend.Terminal.terminal_tools import Terminal
    
            self.input = input_param

            # If the json failed to load or does not exist, exit
            if self.response_object.json is None:
                return

            # If the provided input is not valid from the current json position, exit
            if str(self.input) not in self.response_object.json[self.old_key]:
                return

            # Otherwise, get a list of all the json keys to travel to from the provided input
            nextList = self.response_object.json[self.old_key][str(self.input)]["next"]

            # If that list is empty or doesn't exist, exit and end commanded terminal mode
            if nextList is None:
                Terminal.return_command()
                return

            # If the list has more than 1 option, randomly choose from those options and set that as the next_key
            # Otherwise set next_key to the only option available
            if len(nextList) > 1:
                next_key = nextList[random.randrange(0, len(nextList))]
            else:
                next_key = nextList[0]
            
            self.old_key = next_key

            # Print the json at next_key's position 
            self.response_object.print_at_key(next_key)

class Chat(Command):
    def __init__(self):
        super().__init__(None)

        # Get the path to the help.json file
        from graphics.config import ROOT_PATH
        dialogue_path = ROOT_PATH / "backend" / "json" / "dialogue.json"

        self.inital_json_key = "FirstChat"

        # Load the json file
        self.response_object = MultiResponseHandler(dialogue_path)
        self.old_key = self.inital_json_key

    def execute(self):
        self.response_object.print_at_key(self.inital_json_key)

    def inject_input(self, input_param):
        from backend.Terminal.terminal_tools import Terminal

        self.input = input_param

        # If the json failed to load or does not exist, exit
        if self.response_object.json is None:
            return

        # If the provided input is not valid from the current json position, exit
        if str(self.input) not in self.response_object.json[self.old_key]:
            return

        # Otherwise, get a list of all the json keys to travel to from the provided input
        nextList = self.response_object.json[self.old_key][str(self.input)]["next"]

        # If that list is empty or doesn't exist, exit and end commanded terminal mode
        if nextList is None:
            Terminal.return_command()
            return

        # If the list has more than 1 option, randomly choose from those options and set that as the next_key
        # Otherwise set next_key to the only option available
        if len(nextList) > 1:
            next_key = nextList[random.randrange(0, len(nextList))]
        else:
            next_key = nextList[0]
        
        self.old_key = next_key

        # Print the json at next_key's position 
        self.response_object.print_at_key(next_key)

class Open(Command):
    def __init__(self, window):
        
        super().__init__(window)

    def execute(self):
        match self.argument:
            case "music_player":
                from backend.Terminal.terminal_tools import Terminal
                if Terminal.app is not None:
                    Terminal.app.present_music_player_window()
                return
            case "noxia":
                from backend.Terminal.terminal_tools import Terminal
                if Terminal.app is not None:
                    Terminal.app.present_graphics_window()
                return

# Helper function
class MultiResponseHandler():
    def __init__(self, JSON_path):
        
        from backend.content_manager import ContentManager

        self.input = input

        # load the json at the path argument
        content_manager = ContentManager(JSON_path)

        self.json = content_manager.json

    def print_at_key(self, key):
        from backend.Terminal.terminal_tools import Terminal

        # Exit if the json failed to load or does not exit
        if self.json is None: return

        # Otherwise, print the response
        Terminal.add_to_terminal_history(self.json[key]["Response"])
        Terminal.add_to_terminal_history("\n")

        # And print all the available input options
        temp_dict = self.json[key]

        for i in range(1, 5):
            if str(i) in temp_dict:
                text = str(i) + ") " + self.json[key][str(i)]["promptResponse"]
                Terminal.add_to_terminal_history(text)