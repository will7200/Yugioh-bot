import os
from distutils.dir_util import copy_tree


def copy_file():
    copy_tree(os.path.join(os.environ.get('PYTHON'), r'\Lib\site-packages\APScheduler-3.4.0-py3.5.egg-info'), 'dist/dlbot/APScheduler-3.4.0-py3.5.egg-info')
    copy_tree(r'dist/dlbot/PyQt5/Qt/plugins',r'dist/dlbot')
    os.remove('dist/dlbot/APScheduler-3.4.0-py3.5.egg-info/requires.txt')


if __name__ == "__main__":
    copy_file()
