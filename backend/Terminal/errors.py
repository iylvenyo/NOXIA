## hold a list of errors for the noxia terminal

class Error:
    errorsDictionary ={    
            "ArgumentNullError": "The argument provided is null or undefined",
            "InvalidCommandError": "The command provided is invalid or not recognized",
            "InvalidCommandSyntaxError": "The command syntax provided is invalid or not recognized. Use <command> or <command> <argument>",
            "ApplicationNullError": ""
    }

    def __new__(cls, errorID, message=None):
        return f"<{errorID}> {cls.errorsDictionary.get(errorID)}: {message}"