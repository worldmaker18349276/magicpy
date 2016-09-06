"""
usage:
python test.py [module_name_regex] [module_path_regex]
"""
import sys, os, re, doctest, importlib

default_name = r'.*'
default_path = r'symplus|magicpy'
name = sys.argv[1] if len(sys.argv) >= 2 else default_name
name_pattern = re.compile(r'^(%s)\.py$' % name)
path = sys.argv[2] if len(sys.argv) >= 3 else default_path
path_pattern = re.compile(r'^\./(%s)?$' % path)

modules = []
for dir_path, dir_names, file_names in os.walk('.'):
    if '__pycache__' not in dir_path and path_pattern.match(dir_path):
        for file_name in file_names:
            if file_name != '__init__.py' and name_pattern.match(file_name):
                modules.append(os.path.join(dir_path, file_name)[2:-3].replace('/', '.'))

with open('report', 'w') as report:
    sys.stdout = report

    print('ready to test:')
    for module in modules:
        print(module)
    print('')
    print('test result:')
    for module in modules:
        doctest.testmod(importlib.import_module(module))

