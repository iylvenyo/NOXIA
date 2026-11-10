import csv
import inspect
from backend.Terminal.commands import *
from graphics.config import BASE_LINE, RESPONSE_LINE, MAX_COMMAND_HISTORY_LENGTH, MAX_TERMINAL_HISTORY_LENGTH

class Terminal:
    app = None
    terminalHistory = []
    commandHistory = []
    commanded = False
    commanded_command = None
    current_command_index = -1

    @staticmethod
    def parse(textBlock):

        # Return if the text block is empty
        if textBlock.strip() == "":
            return

        Terminal.add_to_command_history(textBlock)

        # Change the pre entry text depending on the commanded condition
        if Terminal.commanded:
            Terminal.add_to_terminal_history(RESPONSE_LINE + "  " + textBlock)
        else:
            Terminal.add_to_terminal_history(BASE_LINE + "  " + textBlock)

        # Split the text block at semicolons
        stringParts = next(csv.reader([textBlock], delimiter=';', quotechar='"', skipinitialspace=True))

        # Loop through the split parts
        for part in stringParts:
            # Split the part into its subparts(command and argument if one is present)
            reader = csv.reader([part], delimiter=' ', quotechar='"')
            subParts = next(reader)

            # Throw a syntax error if there are no subparts or too many subparts
            if len(subParts) == 0 or len(subParts) > 2:
                if not Terminal.commanded:
                    Terminal.add_to_terminal_history(Error("InvalidCommandSyntaxError"))
                Terminal.add_to_terminal_history("\n")
                continue

            # Get the command and commands argument
            command_name = subParts[0]
            command_argument = subParts[1] if len(subParts) == 2 else None

            # If the terminal is currently being commanded by a commanded command
            if Terminal.commanded:
                # Exit the command if a commanded return command was entered
                if TerminalCommands.containsSubcontrollerReturn(command_name):
                    Terminal.return_command()
                    return
                # Otherwise, inject the input in the command_name variable to the command which has command of the terminal
                else:
                    if Terminal.commanded_command is not None:
                        Terminal.commanded_command.inject_input(command_name)

                Terminal.add_to_terminal_history("\n")
                return
            # If command_name is a valid command, continue
            if TerminalCommands.containsCommand(command_name):
                command_class = TerminalCommands.commandsDictionary[command_name]

                # If there are no parameters in the current command then do not supply arguments
                if len(inspect.signature(command_class).parameters) == 0:
                    command = command_class()
                # Otherwise, supply the captured argument
                else: 
                    command = command_class(command_argument)

                # If the current command is a commanding command, the terminal moves to commanded mode
                if TerminalCommands.containsSubcontroller(command_name):
                    Terminal.commanded = True
                    Terminal.commanded_command = command
                    Terminal.set_command_line_prompt(RESPONSE_LINE)
                    Terminal.set_command_line_placeholder("'exit' to backout")

                # Execute the command
                command.execute()
                continue
            # Otherwise, throw and invalid command error
            else:
                Terminal.add_to_terminal_history(Error("InvalidCommandError", command_name))

        Terminal.add_to_terminal_history("\n")

    @classmethod
    def add_to_terminal_history(cls, text):
        # Add the text to the terminal history and update the terminal
        cls.terminalHistory.append(text)

        while len(cls.terminalHistory) > MAX_TERMINAL_HISTORY_LENGTH:
            cls.terminalHistory.pop(0)

        if cls.app is not None and cls.app.terminal_window is not None:
            cls.app.terminal_window.update_termainl_history(cls.terminalHistory)

    @staticmethod
    def add_to_command_history(text):
        Terminal.commandHistory.append(text)
        while len(Terminal.commandHistory) > MAX_COMMAND_HISTORY_LENGTH:
            Terminal.commandHistory.pop(0)
        Terminal.current_command_index = len(Terminal.commandHistory) - 1

    @staticmethod
    def cycle_command_history_up():
        if len(Terminal.commandHistory) == 0:
            return
        
        if Terminal.app is None or Terminal.app.terminal_window is None:
            return
        current_entry_text = Terminal.app.terminal_window.get_entry_text()

        if Terminal.current_command_index == len(Terminal.commandHistory) - 1 and current_entry_text == "":
            Terminal.current_command_index = len(Terminal.commandHistory) - 1
        else:
            Terminal.current_command_index -= 1

            if Terminal.current_command_index < 0:
                Terminal.current_command_index = 0

        entry_text = Terminal.commandHistory[Terminal.current_command_index]
        Terminal.set_entry_text(entry_text)

    @staticmethod
    def cycle_command_history_down():
        if len(Terminal.commandHistory) == 0:
            return
                
        Terminal.current_command_index += 1

        if Terminal.current_command_index > len(Terminal.commandHistory) - 1:
            Terminal.set_entry_text("")
            Terminal.current_command_index = len(Terminal.commandHistory) - 1
            return

        entry_text = Terminal.commandHistory[Terminal.current_command_index]
        Terminal.set_entry_text(entry_text)
        
    @staticmethod
    def set_entry_text(text):
        if Terminal.app is None or Terminal.app.terminal_window is None:
            return
        Terminal.app.terminal_window.set_entry_text(text)

    @staticmethod
    def get_terminal_history():
        return Terminal.terminalHistory

    @staticmethod
    def clear_terminal_history():
        Terminal.terminalHistory = []

    @staticmethod
    def return_command():
        Terminal.commanded = False
        Terminal.commanded_command = None
        Terminal.set_command_line_prompt(BASE_LINE)
        Terminal.set_command_line_placeholder("")
        Terminal.add_to_terminal_history("\n")

    @staticmethod
    def set_command_line_prompt(prompt):
        if Terminal.app is None or Terminal.app.terminal_window is None:
            return
        Terminal.app.terminal_window.set_command_line_prompt(prompt)

    @staticmethod
    def set_command_line_placeholder(placeholder):
        if Terminal.app is None or Terminal.app.terminal_window is None:
            return
        Terminal.app.terminal_window.set_command_line_placeholder(placeholder)

class TerminalCommands:
    # A master list of all valid commands
    commandsDictionary = {
        "clear": Clear,
        "funny": Funny,
        "change": ChangeBackground,
        "reset": ResetGraphics,
        "quit": Quit,
        "chat": Chat,
        "help": Help
    }

    # A master list of all commands which can take command of the terminal
    subControllers = [
        "chat",
        "help"
    ]
    # A master list of all commands which can exit the terminals commanded mode and return to the base terminal
    subControllersReturn = [
        "exit"
    ]

    @staticmethod
    def containsCommand(command_name):
        return command_name in TerminalCommands.commandsDictionary

    @staticmethod
    def containsSubcontroller(sub_controller_name):
        return sub_controller_name in TerminalCommands.subControllers
    
    @staticmethod
    def containsSubcontrollerReturn(sub_controller_return_name):
        return sub_controller_return_name in TerminalCommands.subControllersReturn
