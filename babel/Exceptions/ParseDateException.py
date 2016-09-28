class ParseDateException(ValueError):
    def __init__(self, message):
        self.message = message
