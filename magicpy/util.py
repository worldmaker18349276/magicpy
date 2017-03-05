import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../lib"))


if sys.version_info[0] == 2:
	from future_builtins import map, filter, zip
	from itertools import ifilterfalse as filterfalse
	range = xrange
else:
	map = map
	filter = filter
	zip = zip
	range = range
	from itertools import filterfalse


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
