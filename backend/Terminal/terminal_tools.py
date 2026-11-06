import csv
import inspect
from backend.Terminal.commands import *
from graphics.config import BASE_LINE, RESPONSE_LINE

class Terminal:
    app = None
    terminalHistory = []
    commanded = False

    @staticmethod
    def parse(textBlock):

        if textBlock.strip() == "":
            return

        if Terminal.commanded:
            Terminal.add_to_terminal_history(RESPONSE_LINE + "  " + textBlock)
        else:
            Terminal.add_to_terminal_history(BASE_LINE + "  " + textBlock)

        stringParts = csv.reader([textBlock], delimiter=';', quotechar='"', skipinitialspace=True)

        for parts in stringParts:
            reader = csv.reader([parts[0]], delimiter=' ', quotechar='"')
            subParts = next(reader)

            if len(subParts) == 0 or len(subParts) > 2:
                Terminal.add_to_terminal_history(Error("InvalidCommandSyntaxError"))
                Terminal.add_to_terminal_history("\n")
                return

            command_name = subParts[0]
            command_argument = subParts[1] if len(subParts) == 2 else None

            if Terminal.commanded:

                if TerminalCommands.containsSubcontrollerReturn(command_name):
                    Terminal.return_command()
                    
                    Terminal.add_to_terminal_history("\n")
                    return

                MultiResponseHandler(command_name)
                Terminal.add_to_terminal_history("\n")
                return

            if TerminalCommands.containsCommand(command_name):

                command_class = TerminalCommands.commandsDictionary[command_name]

                if len(inspect.signature(command_class).parameters) == 0:
                    command = command_class()
                else: 
                    command = command_class(command_argument)

                if TerminalCommands.containsSubcontroller(command_name):
                    Terminal.commanded = True
                    Terminal.set_command_line_prompt(RESPONSE_LINE)

                command.execute()
                Terminal.add_to_terminal_history("\n")
                return
            else:
                Terminal.add_to_terminal_history(Error("InvalidCommandError", command_name))

        Terminal.add_to_terminal_history("\n")

    @classmethod
    def add_to_terminal_history(cls, text):
        cls.terminalHistory.append(text)

    @staticmethod
    def get_terminal_history():
        return Terminal.terminalHistory

    @staticmethod
    def clear_terminal_history():
        Terminal.terminalHistory = []

    @staticmethod
    def return_command():
        Terminal.commanded = False
        Terminal.set_command_line_prompt(BASE_LINE)

    @staticmethod
    def set_command_line_prompt(prompt):
        if Terminal.app is None or Terminal.app.terminal_window is None:
            return
        Terminal.app.terminal_window.set_command_line_prompt(prompt)

class TerminalCommands:
    commandsDictionary = {
        "clear": Clear,
        "funny": Funny,
        "change": ChangeBackground,
        "reset": ResetGraphics,
        "quit": Quit,
        "chat": Chat
    }

    subControllers = [
        "chat"
    ]
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
