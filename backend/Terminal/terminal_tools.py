import csv
import inspect
from backend.Terminal.commands import *

class Terminal:
    terminalHistory = []

    @staticmethod
    def parse(textBlock):

        if textBlock.strip() == "":
            return

        stringParts = csv.reader([textBlock], delimiter=';', quotechar='"', skipinitialspace=True)

        for parts in stringParts:
            reader = csv.reader([parts[0]], delimiter=' ', quotechar='"')
            subParts = next(reader)

            if len(subParts) == 0 or len(subParts) > 2:
                Terminal.add_to_terminal_history(textBlock)
                Terminal.add_to_terminal_history(Error("InvalidCommandError"))
                return

            command_name = subParts[0]
            command_argument = subParts[1] if len(subParts) == 2 else None

            Terminal.add_to_terminal_history(textBlock)

            if TerminalCommands.contains(command_name):
                command_class = TerminalCommands.commandsDictionary[command_name]

                if len(inspect.signature(command_class).parameters) == 0:
                    command = command_class()
                else: 
                    command = command_class(command_argument)

                command.execute()

    @classmethod
    def add_to_terminal_history(cls, text):
        cls.terminalHistory.append(text)

    @staticmethod
    def get_terminal_history():
        return Terminal.terminalHistory

    @staticmethod
    def clear_terminal_history():
        Terminal.terminalHistory = []

class TerminalCommands:
    commandsDictionary = {
        "clear": Clear,
        "funny": Funny
    }

    @staticmethod
    def contains(command_name):
        return command_name in TerminalCommands.commandsDictionary

