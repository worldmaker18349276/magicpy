

class IllegalOperationError(Exception):
    pass

class PuzzleSystem:
    def __init__(self, st, tr, func):
        if not hasattr(st, '__contains__'):
            raise ValueError
        if not hasattr(tr, '__contains__'):
            raise ValueError
        if not hasattr(func, '__call__'):
            raise ValueError
        self.states = st
        self.transitions = tr
        self.applicationfunction = func
