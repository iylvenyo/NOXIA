import csv
from backend.Terminal.commands import *

class Terminal:
    def __init__(self):
        self.terminalHistory = []

    def parse(self, textBlock):

        if textBlock.strip() == "":
            return

        stringParts = csv.reader([textBlock], delimiter=';', quotechar='"', skipinitialspace=True)

        for parts in stringParts:
            subParts = parts[0].split(" ")

            if len(subParts) == 0 or len(subParts) > 2:
                continue

            commandName = subParts[0]
            argument = subParts[1] if len(subParts) == 2 else None

            if TerminalCommands.contains(commandName):

                command_class = TerminalCommands.commandsDictionary[commandName]

                if commandName == "clear":
                    command = command_class(self)
                else:
                    command = command_class(argument)

                command.execute()
                
            if commandName == "clear": return

        self.add_to_terminal_history(textBlock)

    

    def add_to_terminal_history(self, text):
        self.terminalHistory.append(text)

    def get_terminal_history(self):
        return self.terminalHistory

class TerminalCommands:
    commandsDictionary = {
        "clear": Clear,
    }

    @staticmethod
    def contains(command_name):
        return command_name in TerminalCommands.commandsDictionary

    # def execute_command(self, command_name):
    #     command = self.commands.get(command_name)
    #     if command:
    #         command.execute()
    #     else:
    #         self.terminalObj.label.set_text(f"Command '{command_name}' not found.")

