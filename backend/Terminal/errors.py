## hold a list of errors for the noxia terminal

class Error:
    errorsDictionary ={    
            "ArgumentNullError": "The argument provided is null or undefined"
    }

    def __new__(cls, errorID, message=None):
        return f"{cls.errorsDictionary.get(errorID, f"Unknown error ID: {errorID}")}: {message}"