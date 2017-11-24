import os
from PySide import QtCore

res_path = os.path.join(os.path.dirname(__file__), "resources.rcc")
if not QtCore.QResource.registerResource(res_path):
	raise ValueError("fail to register resource: %s"%res_path)
