import csv
import inspect
from backend.Terminal.commands import *
from graphics.config import BASE_LINE, RESPONSE_LINE

class Terminal:
    app = None
    terminalHistory = []
    commanded = False
    commanded_command = None

    @staticmethod
    def parse(textBlock):

        if textBlock.strip() == "":
            return

        if Terminal.commanded:
            Terminal.add_to_terminal_history(RESPONSE_LINE + "  " + textBlock)
        else:
            Terminal.add_to_terminal_history(BASE_LINE + "  " + textBlock)

        stringParts = next(csv.reader([textBlock], delimiter=';', quotechar='"', skipinitialspace=True))

        for part in stringParts:
            reader = csv.reader([part], delimiter=' ', quotechar='"')
            subParts = next(reader)

            if len(subParts) == 0 or len(subParts) > 2:
                if not Terminal.commanded:
                    Terminal.add_to_terminal_history(Error("InvalidCommandSyntaxError"))
                Terminal.add_to_terminal_history("\n")
                continue

            command_name = subParts[0]
            command_argument = subParts[1] if len(subParts) == 2 else None

            if Terminal.commanded:
                if TerminalCommands.containsSubcontrollerReturn(command_name):
                    Terminal.return_command()
                    return
                else:
                    if Terminal.commanded_command is not None:
                        Terminal.commanded_command.inject_input(command_name)

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
                    Terminal.commanded_command = command
                    Terminal.set_command_line_prompt(RESPONSE_LINE)
                    Terminal.set_command_line_placeholder("'exit' to backout")

                command.execute()
                #Terminal.add_to_terminal_history("\n")
                continue
            else:
                Terminal.add_to_terminal_history(Error("InvalidCommandError", command_name))

        Terminal.add_to_terminal_history("\n")
        
    # @staticmethod
    # def parse_response(input):


    @classmethod
    def add_to_terminal_history(cls, text):
        cls.terminalHistory.append(text)
        if cls.app is not None and cls.app.terminal_window is not None:
            cls.app.terminal_window.update_termainl_history(cls.terminalHistory)
        

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
    commandsDictionary = {
        "clear": Clear,
        "funny": Funny,
        "change": ChangeBackground,
        "reset": ResetGraphics,
        "quit": Quit,
        "chat": Chat,
        "help": Help
    }

    subControllers = [
        "chat",
        "help"
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
