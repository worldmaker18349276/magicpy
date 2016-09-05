from magicpy.util import thiz, map


class Thiz(object):
    def __getattr__(self, name):
        def func(obj, *args, **kwargs):
            attr = getattr(obj, name)
            if not hasattr(attr, "__call__") and args == () and kwargs == {}:
                return attr
            else:
                return attr(*args, **kwargs)
        return func
thiz = Thiz()

