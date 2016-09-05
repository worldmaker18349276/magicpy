import sys, os
if sys.version_info[0] == 2:  from future_builtins import map
sys.path.append(os.path.join(os.path.dirname(__file__), "../lib"))


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

