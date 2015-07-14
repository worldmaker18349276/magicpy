

class UnsupportedAlgorithmError(Exception):
    pass


class EngineFunction():
    def __init__(self, *funcs):
        self.functions = funcs
    def __call__(self, *args, **kwargs):
        for func in self.functions:
            try:
                return func(*args, **kwargs)
            except UnsupportedAlgorithmError:
                continue
            raise UnsupportedAlgorithmError
    def __or__(self, other):
        if isinstance(other, EngineFunction):
            return EngineFunction(self.functions + other.functions)
        elif hasattr(other, '__call__'):
            return EngineFunction(self.functions + other)
        else:
            raise ValueError


def enginemethod(func):
    func.__isengine__ = True
    return func

class EngineMeta(type):
    def __new__(self, name, bases, attrs):
        clazz = type.__new__(self, name, bases, attrs)
        enginemethods = {name
                         for name, value in attrs.items()
                         if getattr(value, "__isengine__", False)}
        for base in bases:
            enginemethods |= getattr(base, "__enginemethods__", set())
        clazz.__enginemethods__ = frozenset(enginemethods)

        return clazz

    def __getattribute__(clazz, name):
        if name in clazz.__enginemethods__:
            def enginemthd(*args, **kwargs):
                classes = (clazz,)
                while classes:
                    for clz in classes:
                        try:
                            func = clz.__dict__[name].__get__(None,clz) # not clazz!
                        except KeyError or AttributeError:
                            continue
                        try:
                            return func(*args, **kwargs)
                        except UnsupportedAlgorithmError:
                            continue
                    classes = map(lambda l:getattr(l,'__bases__',tuple()), classes)
                    classes = reduce(tuple.__add__, classes, tuple())
                raise UnsupportedAlgorithmError
            return enginemthd
        else:
            return object.__getattribute__(clazz, name)

class Engine(metaclass=EngineMeta):
    def __getattribute__(instance, name):
        clazz = instance.__class__
        if name in clazz.__enginemethods__:
            def enginemthd(*args, **kwargs):
                classes = (clazz,)
                while classes:
                    for clz in classes:
                        try:
                            func = clz.__dict__[name].__get__(instance,clz) # not clazz!
                        except KeyError or AttributeError:
                            continue
                        try:
                            return func(*args, **kwargs)
                        except UnsupportedAlgorithmError:
                            continue
                    classes = map(lambda l:getattr(l,'__bases__',tuple()), classes)
                    classes = reduce(tuple.__add__, classes, tuple())
                raise UnsupportedAlgorithmError
            return enginemthd
        else:
            return object.__getattribute__(instance, name)
