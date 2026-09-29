## this script is a list of all commands for the noxia terminal
## each command is a unique class which inherits from the Command class

from backend.Terminal.errors import Error

class Command:
    def __init__(self, argument):
        self.argument = argument

    def execute(self):
        raise NotImplementedError("Subclasses must implement the execute method.")


class Clear(Command):
    def __init__(self, terminal):
        super().__init__(terminal)

    def execute(self):
        if self.argument.terminalHistory is None:
            raise ValueError(Error("ArgumentNullError", "terminalHistory is null or undefined"))

        self.argument.terminalHistory = []