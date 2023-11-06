class AgendaException(Exception):
    """This class is a custom exception for known errors"""
    
    def __init__(self, message):
        """initialize the agenda exception"""
        print(f'Raising agenda exception {message}')
