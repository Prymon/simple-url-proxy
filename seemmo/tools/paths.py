import os
import sys

home_path = os.path.expanduser('~')
script_path = os.path.split(os.path.realpath(sys.argv[0]))[0]


def logging_path(module):
    return must_exist('%s/logs/%s' % (home_path, module))


def dir_path(path):
    return os.path.split(path)[0]


def must_exist(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

    return dirpath
